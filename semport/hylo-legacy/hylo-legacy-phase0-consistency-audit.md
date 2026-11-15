# Phase 0 fresh-context consistency audit — hylo-legacy (pre-gate)

- **Auditor:** consistency-validator, fresh context (no prior Phase 0 state; this audit is the "fresh-context consistency audit" step in STATE.md's next-steps chain).
- **Date:** 2026-11-14. **Mode:** read-only. Nothing edited, nothing committed, nothing run from `legacy/`, nothing networked. `CLAUDE.local.md` not read.
- **Inputs read in full:** `.factory/STATE.md`, `.factory/policies.yaml` (1-20), `hylo-legacy-owner-decisions.md`, `hylo-legacy-extraction-validation-r2.md`, `hylo-legacy-coverage-audit.md`, `hylo-legacy-pass-8-deep-synthesis.md`, `docs/PLAN.md`, `docs/RESUME.md`, `docs/STATUSLINE-WIDGETS.md`, `docs/STATUSLINE-REVIEW-2026-11-13.md`, `README.md`, `CLAUDE.md`, `specs/research/RESEARCH-INDEX.md` + `peer-tool-lessons-2026-11-14.md` (full) and the parity-crossplatform report (config-path section). Targeted greps across all 47 files in `semport/hylo-legacy/` and the 4 cycle files.
- **Audit question:** is the perimeter right, not just the content inside it?

## 1. Summary

| # | Check area | Result |
|---|------------|--------|
| 1 | Cross-document IDs and counts | **PASS** — every headline count reconciles to its source artifact (§2) |
| 2 | Owner decision list integrity | **PASS with one numbering caveat** (F-02, Q-03) |
| 3 | Settled-decision conformance (policy 12) | **PASS** — no artifact reopens D1-D16; two wording touches are framed as owner clarifications (OD-10, OD-14), as policy 12 requires |
| 4 | Perimeter gaps vs PLAN §4/§6/§7, D13-D16, status line docs | **PASS with caveats** (F-01, F-05, F-06, Q-02) |
| 5 | Public-doc drift | **3 findings** (F-01, F-03, F-04) — proposed updates only; owner-approved commits |
| 6 | Policy compliance (13, 14, 16) | **PASS** (details §4) |

**Finding counts: BLOCKING 0 · IMPORTANT 3 · MINOR 4 · QUESTION 3** (10 total).

## 2. Count reconciliation (check 1)

Every count claimed in STATE.md and the pass-8 synthesis was traced to its source artifact. No mismatches found.

| Claim (STATE.md / synthesis) | Source verification | Result |
|---|---|---|
| 232 BCs = 137 BX + 44 JE + 10 OOS + 6 approved deviation + 35 pending OD | pass-3 r4 checkpoint `bc_index_by_parity: {BX 137, JE 44, OOS 10, approved_deviation 6, pending_OD 30}` at the r4 base of 227; the 5 r5-r8 additions (BC-EX-027, BC-PX-046..049) are all pending-OD class → 30+5 = 35. Per-component 103+49+27+23+11+2+2+13+2 = 232 (EV r2 recounts; arithmetic rechecked here) | ✓ |
| 147 thresholds = 79+31+37; contiguous T-001..T-147; classes CFG 96 / NC 37 / DROP 7 / OOS 2 / EXT 2 / NEW-H 2 / N-A 1 | pass-4 r7 §B.2 and EV r2 recount; class sum = 147 | ✓ |
| "120 rationales resolved" + OD-57 (18 bulk + 27 in 7 groups) | pass-4 r7: "Rationale resolved **120 of 147** (102 final + 18 awaiting one bulk yes)"; OD-57 = 18 (Dv†) + 27 (OWNER) = 45; 120+27 = 147. Fully coherent | ✓ |
| Env 43 explicit + 21 implicit | EV r2: 43 = 27 Python + 22 launcher − 6 overlap; I-01..I-21 (I-21 added pass-5 r4) | ✓ |
| Lessons 53 = 13 P0 + 13 P1 + 9 P2 + 18 P3 | pass-8 §10: L0-01..13, L1-01..13, L2-01..09, L3-01..18 counted directly = 53 | ✓ |
| OD list: 64 issued (2 ruled), groups A 12 / B 19 / C 13 / D 10 / E 2 / F 8; 23 KEEP / 30 DEVIATE / 11 NEW; unused 30 (OD-44, 49, 62-65, 67-73, 77-93); next free OD-95 | Recounted row-by-row from `hylo-legacy-owner-decisions.md`: 12+19+13+10+2+8 = 64; every type cell and the summary table match; unused enumeration = 30; 64+30 = 94 IDs in range | ✓ |
| Retractions: ~50 distinct; CONV-ABS through 94; next free 95; 101-104 unused; RET crosswalk pass-3 r4 | synthesis §9.2 series-sums to exactly 50 (2+7+14+5+17+5); max issued CONV-ABS-94 verified by sorted grep; RET-01..RET-12 present in pass-3 r4 | ✓ |
| Statement partition 1,809 = 903 + 422 + 133 + 351; AST 1,809 = 742+500+316+146+86+19 | EV r2 metric table; both partitions sum to 1,809 | ✓ |
| Convergence rounds 3/3/9/8/7/5 = 35; 2 overrides | synthesis §9.1 and checkpoint; matches STATE.md Phase Progress | ✓ |
| Extraction validation r2: 78/232 sampled, 0 hallucinated; 26/27 metric groups exact; 1 fix (spawn census 10→9) | EV r2 §§1.1, 2; fix confirmed present in pass-0 r3 §2.5 with evidence | ✓ |
| Coverage audit PASS, 0 gaps; "all 44 files" at audit time | coverage-audit §4; 47 files exist now (44 + validation r2 + synthesis + OD list) — chronologically consistent | ✓ |

## 3. Findings

Severity scale: BLOCKING (gate must not pass) / IMPORTANT (gate should not pass without acknowledging) / MINOR (fix at convenience) / QUESTION (owner call, not a defect).

### IMPORTANT

**F-01 · PLAN §6 config path conflicts with Go `os.UserConfigDir`, and the conflict is parked in research only.**
Evidence: `docs/PLAN.md` §6 says `~/.config/hylo/config.yaml` (Windows `%APPDATA%\hylo\config.yaml`). `specs/research/general-go-port-parity-crossplatform-2026-11-14.md:291-292` flags it: "PLAN conflict. ... On macOS, `os.UserConfigDir` returns `~/Library/Application Support`". Neither the pass-8 synthesis nor the OD list carries the item, so no owner decision absorbs it before P1/P4 config work.
Proposed fix: owner clarifies PLAN §6 (literal `~/.config/hylo/config.yaml` with tilde expansion, or `os.UserConfigDir` with a macOS note; Windows agrees either way). One-sentence PLAN edit, owner-approved commit. Owner: owner.
Why not BLOCKING: behavior-shaping value, not parity behavior; no artifact contradicts it today.

**F-02 · OD "next free" bookkeeping rests on an unstated convention, and the trailing unused declarations are not in the companion file.**
Evidence: the OD companion header says "Unused or reserved IDs are skipped: OD-44, OD-49, OD-62..65, OD-67..73, OD-77..93. Next free ID: OD-95" (and STATE.md line 104 repeats it). But round checkpoints declared OD-95..97 (pass-4 r5 `od_unused`), OD-98..101 (pass-5 r4), OD-102..105 (pass-4 r6), OD-106..109 (pass-5 r5), OD-110..113 (pass-4 r7) as unused — a traversed trail up to OD-113 that the companion's unused list does not include. The same asymmetry exists for CONV-ABS: synthesis §9.2 sets "next free 95" while recording 101-104 (and pass-5 r5 records 97-100; pass-4 r6 records 95-96) as unused.
Reading: the convention actually applied is "a declared-unused ID is not issued, not consumed" — next free is 95 for both series, and re-declaring is harmless. That is applied consistently. But nowhere is it stated, while the companion DOES list the earlier skipped IDs (62-65 etc.) as if consumption mattered. A Phase 1 agent issuing new ODs can read these two signals oppositely (policy 1, append-only numbering).
Proposed fix: one sentence in the companion header (and eventually STATE.md at the next burst): "IDs declared unused in round checkpoints (OD-95..OD-113, CONV-ABS-95..104) were never issued and remain available; next free OD-95 / CONV-ABS-95." Owner: consistency-validator / orchestrator (write permitted in `.factory/`).

**F-03 · `docs/RESUME.md` P1 guidance is stale in two load-bearing spots now that Phase 0 analysis exists.**
Evidence: (a) "Open questions for the owner — None blocking P1" (RESUME.md line 65) predates the analysis; the OD list now gates P1 on ~15 decisions (OD-01, 02, 03, 05, 14, 21, 30, 32, 55, 56, 57, 58, 59, 61, 74 — "Needed before P1 starts" in the companion). (b) RESUME step 3 sketches the harness clock as a `sitecustomize.py` shim patching `time.time` — the analysis found that insufficient (a frozen `time.time` hides the Kev early stop and does not freeze `strftime`-derived fields; CONV-ABS-47/48, OD-58 extended shim). (c) it is silent that a private decision list accompanies the gate.
Proposed fix (owner-approved commit, public-safe wording): update the open-questions line to "the Phase 0 ingestion analysis is complete; a private decision list gates P1 (mirrored into the repo at Phase 1 start)"; amend step 3 to "clock shim (frozen and strftime-masked modes)". Owner: owner.

### MINOR

**F-04 · PLAN §3 goal "one config file instead of ~25 env vars" understates the measured surface.**
Phase 0's census is 43 explicit env inputs + 21 implicit (EV r2 verified). The plan-era estimate is now superseded by a defensible number. Fix: "instead of the prototype's 43 environment variables (plus 21 implicit inputs)" in a future PLAN edit. Owner: owner.

**F-05 · No explicit rule-by-rule crosswalk from `docs/STATUSLINE-REVIEW-2026-11-13.md` to BC IDs.**
CLAUDE.md requires "a table test for every rule the status line review fixed" and the P1 exit criterion repeats it (RESUME step 6). Coverage is materially there — 103 BC-SL contracts, 100% line-level citation coverage of `dgx_statusline.py` (coverage-audit §2.4), and EV r2 confirmed the fixed behaviors at their sites (e.g. timer math, width rule, TTFT bounds, degradation ladder) — but no artifact maps review defect IDs (9.1, 5.2, 17.1, ...) to the BCs that pin them. Cheap insurance for the Phase 1 test plan: a two-column table (review defect → BC) produced in P1 story decomposition. Owner: story-writer (Phase 1).

**F-06 · Public WIDGETS doc carries dangling references to private-repo docs.**
Evidence: `docs/STATUSLINE-WIDGETS.md` cites "THRESHOLDS §8b" (twice), "ECONOMICS-BRIEF", and "RESUME TODO #29-32" — documents that stayed in the private home-lab repo (PLAN §4 migrates only the status line docs, OBSERVABILITY client parts, ROLLBACK). Related: the OD-57 threshold rationales that policy 16 requires "in the docs" currently live only in the private pass-4 catalogue; when the Phase 1 config reference is written, the public docs need the rationales inline (sanitized). Fix: inline one-phrase rationale pointers at the P1 config-reference stage; decide TODO #29-32 disposition. Owner: owner + Phase 1 technical-writer.

**F-07 · Two overlapping "OD" namespaces with confusable spellings.**
The research report `peer-tool-lessons-2026-11-14.md` issues "OD-1 / OD-2" (= D13/D14, settled), while the Phase 0 register issues "OD-01, OD-02, ..." (pending; OD-01 is config key naming, OD-02 status-line glyphs). STATE.md disambiguates ("OD-1 (= D13)"), but the companion does not mention the research pair. One clarifying line in the companion header prevents conflation at the gate. Owner: consistency-validator.

### QUESTION (policy 12: owner clarifications, not defects)

**Q-01 · D13 wording vs `count_tokens` behavior (already OD-10).** D13 text names only "POST /v1/messages"; legacy (and live behavior, 5/5 answered 200) also routes `/v1/messages/count_tokens` and batches to the backend (method-agnostic prefix, BC-PX-035). OD-10 asks only for a D13 text clarification. Confirm at the gate; no spec change beyond wording.

**Q-02 · `hylo cost backfill` has no phase in PLAN §7 (already OD-36).** It appears in PLAN §4 and §6 but no phase row; OD-36 recommends scheduling it in P6 with the cost basis. Confirm at the gate; consider a one-word PLAN §7 edit ("P6 ... cost basis configurable (incl. `hylo cost backfill`)").

**Q-03 · Confirm the stated reading of F-02:** next free OD is 95 (declared-unused IDs remain free), so a future OD-95 does not collide with pass-4 r5's `od_unused: [OD-95, OD-96, OD-97]`. If the owner prefers, burn 95-113 and set next free = OD-114.

## 4. Policy compliance (check 6)

- **Policy 13 (parity BCs cite legacy):** PASS. EV r2 verified 78/232 sampled BCs at their cited `legacy/` file:line sites (100%), including operator-level distinctions (T-038 `> 60000` vs T-039 `>= 60000`) and the D4-EX-1/2, D13, D14 deviation rows. Coverage audit found no symbol > 20 LOC without a BC and no cluster > 100 LOC undocumented; statement partition covers 1,809/1,809.
- **Policy 16 (thresholds explained or marked OWNER):** PASS. All 147 rows carry rationale codes; 120 resolved (102 final + 18 bulk-awaiting-sign-off), 27 grouped for owner wording (OD-57, 8 answer rows), OD-94 moves 9 rows between classes with both outcomes tabulated (pass-4 r7 §B.2.4). Inert thresholds are flagged (OD-55) rather than silently kept.
- **Policy 14 (public hygiene):** N/A inside `.factory/` as the policy states; checked for leak-risk anyway: the synthesis anonymizes the backend as `<backend>` (§ preamble), state.md/companion contain no private IPs, hosts, emails or session links. Public docs use 192.0.2.x correctly (WIDGETS tunables). No content found that would leak if copied verbatim into public docs — the only adjacent issue is the dangling private-doc references (F-06), which leak nothing.

## 5. Perimeter assessment (check 4) — the package covers what P1-P4 need

- **Every PLAN §4 component has BCs:** launcher (11), proxy (49), coordinator (2), status line (103), backfill (13), exporter + LaunchAgents (27+2), stop hook (23), preflight (2); `opus_router.py` is history-only under D6 (no BCs required, correctly). 56 features in synthesis §3 map to all 232 BCs; superseded draft BCs (BF-001..005 etc.) are explicitly marked do-not-promote with successor folding rules (§8.1).
- **Every PLAN §6 subcommand has a legacy source or is marked new:** run, proxy, statusline, exporter, hook stop, doctor, ca (← legacy trust CLI, OOS-by-D13), cost backfill (← legacy script; unscheduled — Q-02); new: ui, top (D16), config (F-LN-10 touches `config show`; `validate` trivial), version (RESUME only).
- **D13-D16 implications traced into the synthesis:** D13 (LD-2, F-PX-02, OD-10 wording question), D14 (LD-10, L0-09 mechanism plan incl. the research recommendation and residual-leak reporting), D15 (LD-5, L1-02 registry generation, 96 CFG / 37 NC mapping), D16 (BC6 context, F-PX-14, L0-06 loopback/token guardrails). The research conflicts are recorded, not buried (name-constrained CA superseded by OD-1/D13; config path — see F-01).
- **Status line docs:** all 21 reviewed widgets (review doc 21/21 COMPLETE) map to F-SL-01..15 feature rows and thence to BC ranges; the two known public-doc corrections surface from the analysis itself (Health-dot sentence and inert thresholds — OD-55), not from drift the audit had to catch.

## 6. Verdict

The package is internally consistent to an unusual degree: every count claim traced to its source with zero deltas, the OD amendment trail is disclosed rather than hidden (OD-14 reversal, OD-32 CONV-ABS-15 amendment, OD-35/36→37/38 renumbering all announced), and the perimeter anticipates P1-P4 rather than merely describing legacy. The three IMPORTANT findings are one-line owner actions or clarifications that should ride along with the gate; none undermines the analysis.

Verdict: READY-WITH-CAVEATS
