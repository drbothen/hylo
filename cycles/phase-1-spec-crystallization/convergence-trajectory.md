# Convergence trajectory — phase-1-spec-crystallization (active cycle)

Finding progression across adversarial passes in this cycle.

## Finding Progression

| Pass | Findings | Delta | Disposition |
|------|----------|-------|-------------|
| 1 (phase-1d, 2026-11-17) | 129 (21 HIGH / 63 MEDIUM / 40 LOW / 5 COSMETIC) | — | NOT_CONVERGED — novelty HIGH; owner questions + fix burst next |
| 2 (phase-1d, 2026-11-17) | 116 (17 HIGH / 58 MEDIUM / 35 LOW / 6 COSMETIC) | −13 | NOT_CONVERGED — novelty MEDIUM; owner rulings OD-155..159 + fix burst next |
| 3 (phase-1d, 2026-11-18) | 150 (36 HIGH / 61 MEDIUM / 48 LOW / 5 COSMETIC) | +34 | NOT_CONVERGED — **REGRESSION** (investigated before continuing, see below); novelty MEDIUM; owner questions + fix burst next |

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
