# Convergence trajectory — phase-1-spec-crystallization (active cycle)

Finding progression across adversarial passes in this cycle.

## Finding Progression

| Pass | Findings | Delta | Disposition |
|------|----------|-------|-------------|
| 1 (phase-1d, 2026-11-17) | 129 (21 HIGH / 63 MEDIUM / 40 LOW / 5 COSMETIC) | — | NOT_CONVERGED — novelty HIGH; owner questions + fix burst next |
| 2 (phase-1d, 2026-11-17) | 116 (17 HIGH / 58 MEDIUM / 35 LOW / 6 COSMETIC) | −13 | NOT_CONVERGED — novelty MEDIUM; owner rulings OD-155..159 + fix burst next |
| 3 (phase-1d, 2026-11-18) | 150 (36 HIGH / 61 MEDIUM / 48 LOW / 5 COSMETIC) | +34 | NOT_CONVERGED — **REGRESSION** (investigated before continuing, see below); novelty MEDIUM; owner questions + fix burst next |
| 4 (phase-1d, 2026-11-17) | 133 (39 HIGH / 57 MEDIUM / 32 LOW / 5 COSMETIC) | −17 | NOT_CONVERGED — total down 17 but HIGH up 3 (36 → 39), many findings sibling-propagation; novelty MEDIUM-HIGH; owner rulings OD-169..175 + fix burst next |
| 5 (phase-1d, 2026-11-18) | 148 (24 HIGH / 75 MEDIUM / 43 LOW / 6 COSMETIC) | +15 | NOT_CONVERGED — total +15 but HIGH down 15 (39 → 24), severity mass moved to MEDIUM (75); novelty MEDIUM; owner rulings OD-176..180 + fix burst next |
| 6 (phase-1d, 2026-11-18) | 124 (27 HIGH / 52 MEDIUM / 38 LOW / 7 COSMETIC) | −24 | NOT_CONVERGED — largest total drop of the series (148 → 124) but HIGH ticked up 24 → 27; novelty MEDIUM; owner rulings OD-181..187 + fix burst next |

## Per-Pass Details

### Pass 1 — 2026-11-17 (phase-1d adversarial spec review)

- Scope: full P1 spec package, run as six fresh-context perimeters (corpus ~1.4 MB exceeds one context). Verbatim reports: `adversarial-reviews/pass-1.md`; index: `adversarial-reviews/ADV-P1-INDEX.md`.
- Perimeter counts: A 21, A2 28, B 20, C 8, C2 19, D 33.
- Perimeter severities: A 6H/9M/6L; A2 6H/15M/6L/1C; B 0H/11M/9L; C 1H/4M/2L/1C; C2 2H/7M/9L/1C; D 6H/17M/8L/2C.
- Novelty: A HIGH, A2 HIGH, B HIGH, C MEDIUM, C2 HIGH, D HIGH — pass-level HIGH.
- Tags: 5 [owner-question], 7 [process-gap], 1 (pending verification), 2 (pending intent verification).
- Verdict: NOT_CONVERGED. Next: consolidate owner questions, run fix burst, then pass 2.

### Pass 2 — 2026-11-17 (phase-1d adversarial spec review)

- Scope: full P1 spec package, re-reviewed as the same six fresh-context perimeters as pass 1. Verbatim reports: `adversarial-reviews/pass-2.md`; index: `adversarial-reviews/ADV-P2-INDEX.md`.
- Perimeter counts: A 26, A2 29, B 17, C 12, C2 14, D 18.
- Perimeter severities: A 4H/15M/6L/1C; A2 4H/17M/7L/1C; B 3H/6M/7L/1C; C 2H/4M/5L/1C; C2 1H/6M/6L/1C; D 3H/10M/4L/1C.
- Novelty: A HIGH, A2 HIGH, B MEDIUM, C MEDIUM, C2 MEDIUM, D MEDIUM — pass-level MEDIUM.
- Tags: 9 [owner-question], 1 [process-gap], 1 (pending intent verification), 1 (pending verification).
- Verdict: NOT_CONVERGED. Next: fix burst incl. owner rulings OD-155..159, then pass 3.

### Pass 3 — 2026-11-18 (phase-1d adversarial spec review)

- Scope: full P1 spec package, re-reviewed as the same six fresh-context perimeters as passes 1 and 2. Verbatim reports: `adversarial-reviews/pass-3.md`; index: `adversarial-reviews/ADV-P3-INDEX.md`.
- Perimeter counts: A 29, A2 27, B 18, C 22, C2 14, D 40.
- Perimeter severities: A 8H/9M/11L/1C; A2 6H/15M/6L; B 4H/6M/7L/1C; C 5H/9M/7L/1C; C2 3H/5M/4L/2C; D 10H/17M/13L.
- Novelty: A MEDIUM, A2 MEDIUM-HIGH, B MEDIUM, C HIGH, C2 MEDIUM, D HIGH — pass-level MEDIUM.
- Tags: 8 [owner-question], 5 [process-gap], 1 (pending intent verification).
- **REGRESSION (first delta-positive pass of the series: 129 → 116 → 150; HIGH 21 → 17 → 36).** Rule applied: investigate before continuing (adversarial-review skill, trajectory monotonicity) — done, before dispatching any fix burst.
- Root cause (orchestrator analysis): the pass-2 remediation added new scope without pre-validation, and that scope's propagation debt dominates the increase. Specifically: (1) OD-155 (8 new BC-1.07 `--subagent` BCs) and rulings OD-156..165 were not yet propagated to the parity harness, the Python oracle, the SS-02 config contracts, the SS-05 consumer lists or the L2 (L2/SM-04/DI-008 have no zero-byte carve-out; harness case model has no argv field; SS-02 Bool-set lists omit `statusline.subagent.enabled`; SS-05 dumps/consumer lists miss the subagent sites) — most pass-3 HIGH findings sit here (A01-A08, C01-C05, D04-D10); (2) the ARCH-06 reconciled signature canon was not propagated to BC-5.04.002/003 (D02, D03); (3) an escape-decoding corruption unescaped valid uXXXX sequences in expected-output/golden cells (C01, D09), making expected bytes ambiguous; (4) most pre-existing content shows refinements only — fixed findings did not relapse.
- Verdict: NOT_CONVERGED. Next: consolidate owner questions, fix burst (propagate OD-155/OD-156..165 scope + ARCH-06 canon, regenerate corrupted expected-output cells), then pass 4.

### Pass 4 — 2026-11-17 (phase-1d adversarial spec review)

- Scope: full P1 spec package, re-reviewed as the same six fresh-context perimeters as passes 1-3. Verbatim reports: `adversarial-reviews/pass-4.md`; index: `adversarial-reviews/ADV-P4-INDEX.md`.
- Perimeter counts: A 19, A2 26, B 22, C 15, C2 17, D 34.
- Perimeter severities: A 10H/6M/3L; A2 6H/11M/7L/2C; B 5H/9M/8L; C 3H/7M/4L/1C; C2 4H/9M/4L; D 11H/15M/6L/2C.
- Novelty: A HIGH, A2 HIGH, B MEDIUM, C MEDIUM, C2 MEDIUM, D MEDIUM — pass-level MEDIUM-HIGH.
- Tags: owner-question and process-gap rows continue (ADV-P4-INDEX); 7 owner rulings minted (OD-169..OD-175), next free OD-176; closed exclusion set grows to 11 ids (OD-166 added).
- Trajectory note: total down 17 (150 → 133) but HIGH up 3 (36 → 39). Many findings were sibling-propagation: fixed facts re-flagged at their sibling sites, not relapses of fixed findings; the HIGH concentration sits on the interface-definitions/registry closure (ADV-P4-A04/A05) and partial-fix propagation (ADV-P4-A2-03).
- Verdict: NOT_CONVERGED. Next: owner rulings OD-169..175 + fix burst (8 parallel fix agents + 2 residual sweeps + OD-148 layout correction + 2 sync-fix agents), then pass 5.
### Pass 5 — 2026-11-18 (phase-1d adversarial spec review)

- Scope: full P1 spec package, re-reviewed as the same six fresh-context perimeters as passes 1-4. Verbatim reports: `adversarial-reviews/pass-5.md`; index: `adversarial-reviews/ADV-P5-INDEX.md`.
- Perimeter counts: A 25, A2 36, B 16, C 17, C2 21, D 33.
- Perimeter severities: A 5H/13M/7L; A2 4H/22M/9L/1C; B 2H/7M/6L/1C; C 3H/8M/5L/1C; C2 0H/9M/10L/2C; D 10H/16M/6L/1C.
- Novelty: pass-level MEDIUM (index frontmatter; no per-perimeter novelty split recorded for this pass).
- Tags: 10 [owner-question], 5 [process-gap] (ADV-P5-INDEX row tags).
- Trajectory note: total +15 vs pass 4 (133 → 148) while HIGH fell 39 → 24 — the series' first pass where total rose but HIGH fell sharply; the HIGH concentration moved out of the interface-definitions/registry closure that dominated pass 4.
- Verdict: NOT_CONVERGED. Next: owner rulings OD-176..180 + fix burst (executed same burst; rulings incl. OD-176 keeping the full VSDD convergence standard), then pass 6.

### Pass 6 — 2026-11-18 (phase-1d adversarial spec review)

- Scope: full P1 spec package, re-reviewed as the same six fresh-context perimeters as passes 1-5. Verbatim reports: `adversarial-reviews/pass-6.md`; index: `adversarial-reviews/ADV-P6-INDEX.md`.
- Perimeter counts: A 19, A2 30, B 16, C 17, C2 15, D 27.
- Novelty: pass-level MEDIUM (index frontmatter; no per-perimeter novelty split recorded for this pass).
- Tags: 7 [owner-question], 2 [process-gap] (ADV-P6-INDEX row tags).
- Trajectory note: total −24 vs pass 5 (148 → 124), the largest total drop of the series, though HIGH ticked up 24 → 27; the drop follows the pass-5 remediation's widest-yet propagation (OD-176..180 scope, seventh D4-EX-3 class).
- Verdict: NOT_CONVERGED. Next: owner rulings OD-181..187 + fix burst (executed same burst; OD-181 closes the exclusion set at 12 ids; OD-182 makes VP Go sketches non-normative; sync check adv-p6 PASS-WITH-FINDINGS, SC-21..28 closed), then pass 7.

### Pass 7 — 2026-11-18 (phase-1d adversarial spec review)

- Scope: full P1 spec package, re-reviewed as the same six fresh-context perimeters as passes 1-6. Verbatim reports: `adversarial-reviews/pass-7.md`; index: `adversarial-reviews/ADV-P7-INDEX.md`.
- Perimeter counts: A 22, A2 22, B 15, C 14, C2 14, D 27.
- Perimeter severities: A 3H/10M/9L/0C; A2 0H/12M/9L/1C (zero HIGH — first time); B 1H/6M/7L/1C; C 1H/4M/7L/2C; C2 3H/4M/7L/0C; D 6H/11M/10L/0C.
- Novelty: pass-level MEDIUM (index frontmatter; report: all perimeters MEDIUM).
- Tags: 8 [owner-question], 0 [process-gap] (ADV-P7-INDEX row tags).
- Trajectory note: total −10 vs pass 6 (124 → 114) with HIGH nearly halved 27 → 14; the orchestrator spot-verified six findings on disk and against CPython 3.11.7, all held.
- Verdict: NOT_CONVERGED (per OD-176: three consecutive cosmetic-only passes required — 0 so far). Next: owner rulings OD-188..192 + fix burst (executed same burst; OD-188 rename_retry_limit; OD-192 ASM-007 owner capture before Phase 2 S1.07; crash register 48 paths, CP-T09 minted / CP-T08 retired; VP↔BC edges 261; sync check adv-p7 PASS-WITH-FINDINGS — 114 closed / 0 open, SC-29..31 closed), then pass 8.

### Pass 8 — 2026-11-18 (phase-1d adversarial spec review)

- Scope: full P1 spec package, re-reviewed as the same six fresh-context perimeters as passes 1-7. Verbatim reports: `adversarial-reviews/pass-8.md`; index: `adversarial-reviews/ADV-P8-INDEX.md`.
- Perimeter counts: A 13, A2 19, B 11, C 6, C2 15, D 24.
- Perimeter severities: A 2H/6M/4L/1C; A2 5H/6M/7L/1C; B 1H/4M/4L/2C; C 1H/2M/2L/1C; C2 1H/8M/6L/0C; D 2H/10M/10L/2C.
- Novelty: pass-level MEDIUM (index frontmatter; no per-perimeter novelty split recorded for this pass).
- Tags: 2 [owner-question], 3 [process-gap] (ADV-P8-INDEX row tags).
- Trajectory note: total −26 vs pass 7 (114 → 88), the second-largest total drop of the series, with HIGH easing 14 → 12; the orchestrator spot-verified eight findings (A01, A02, A05, A2-01, A2-05, B01, C2-03, C2-13) on disk and against CPython 3.11.7, all held.
- Verdict: NOT_CONVERGED (per OD-176: three consecutive cosmetic-only passes required — 0 so far). Next: owner ruling OD-193 + fix burst (8 fix agents + 2 residual sweeps, executed same burst; OD-193 keeps OD-158 — coverage gate S1+S5 only, `internal/parity` reported not gated; VP↔BC edges 269; sync check adv-p8 — 87 closed / 1 rejected (C02, measured unreachable) / 0 open, SC-32 disposed as no-change), then pass 9.

### Pass 9 — 2026-11-18 (phase-1d adversarial spec review)

- Scope: full P1 spec package, re-reviewed as the same six fresh-context perimeters as passes 1-8. Verbatim reports: `adversarial-reviews/pass-9.md`; index: `adversarial-reviews/ADV-P9-INDEX.md`.
- Perimeter counts: A 17, A2 20, B 7, C 11, C2 10, D 20.
- Perimeter severities: A 3H/9M/4L/1C; A2 4H/8M/7L/1C; B 1H/4M/2L/0C; C 2H/4M/4L/1C; C2 1H/4M/5L/0C; D 4H/9M/6L/1C.
- Novelty: pass-level MEDIUM-HIGH (per-perimeter: A HIGH, A2 HIGH, B/C/C2/D MEDIUM).
- Trajectory note: total −3 vs pass 8 (88 → 85), the smallest total drop of the series, but HIGH rose 12 → 15 — many findings are regressions introduced by pass-8 fixes: four pass-8 "for all inputs" VPs false over legal inputs (ADV-P9-A2-01..04, B01), 11 spec files left with unparsable YAML frontmatter (ADV-P9-C02), one measured case (HTTP 100) generalized to the class "any 1xx" (ADV-P9-C2-01), plus partial-fix sibling residues (A02, D01, D03, D05, B01/B02). The burst answered with four burst-wide gates for future fix agents: YAML-`safe_load` frontmatter on every changed file, for-all properties derived from the owning BC's postconditions, no generalizing one measured case to a class, ASCII-only wire goldens.
- Verdict: NOT_CONVERGED (per OD-176: three consecutive cosmetic-only passes required — 0 so far). Next: fix burst (8 fix agents incl. one agent-breakdown re-dispatch + 1 residual sweep + 1 closing fix, executed same burst; no owner rulings this pass — next free OD-194; crash register 48 → 49 paths, CP-O12 minted; VP↔BC `bcs:` edges re-machine-checked at 270; sync check `sync-check-adv-p9-2026-11-18.md` — 85 closed / 0 rejected / 0 open, SC-33/SC-34 closed), then pass 10.
