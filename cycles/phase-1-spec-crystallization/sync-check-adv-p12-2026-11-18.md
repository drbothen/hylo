---
document_type: sync-check
phase: 1d
pass: 12
date: 2026-11-18
source: pass-12-remediation-plan.md (calls 1-17) vs uncommitted `git diff -- specs` (86 files, +1135/-651)
method: required-presence greps over all of specs/ (history/modified lines excluded as provenance per the SC-32 precedent); bidirectional scripted recounts; frontmatter YAML parse of every changed file; field-by-field derivation of changed canonical vectors against the legacy reference file
---

# Pass-12 sync check (adversarial pass 12 remediation)

Verdict: **PASS — 10/10 check groups clean, zero blocking findings, one non-blocking observation.**

## Result table

| # | Check | Result | Evidence / notes |
|---|---|---|---|
| 1a | Call 1: full-history gitleaks scan present; no live two-ref statement | PASS | Property Statement in VP-035 (sec. scan leg), BC-6.04.001 PC-4, BC-6.02.001 PC-4 tail + Related-BCs line, ARCH-08 CI diagram node + hygiene bullet + positive-coverage bullet, cicd-setup findings table all state `--log-opts="--all"` after checkout with `fetch-depth: 0` and the `git rev-list --count --all` counter. Remaining two-ref mentions are `modified:` history entries (VP-035 1.4, BC-6.04.001 1.2.7, BC-6.02.001 1.2.6) or framed as "the interim invocation" (cicd-setup) — provenance, not live rules |
| 1b | Call 2: no fake process table / fake ps for a corpus case or the temp-file case | PASS | BC-6.03.003 (Pre-2, PC-3 note, CTV row: "There is NO fake process table", empty-bin conditional PATH), BC-6.01.002 (conditional-PATH bullet, "NO fake process table and NO fake `ps`"), BC-6.02.003 PC-6, BC-3.02.001 Inv 4 + EC-008, BC-3.02.002 Pre-3 (closing sentence: fake `ps` exists only in the GO TABLE TESTS, never in a parity case), dtu-assessment inventory row 4 + integration-surface justification. Remaining "fake process table"/"fake ps" hits describe Go table tests only, which is the allowed form |
| 1c | Call 2: no live "every corpus case seeds proc_start" universal without the temp-file exception | PASS | Restated with the exception in BC-3.02.001 Inv 4, BC-6.03.004 D4-EX-1 row + closure paragraph, VP-014 statement, VP-019 swap-leg carve-out, and the three ss-01 lone-surrogate vector rows (BC-1.01.001/.008/.009). Universal dissolutions recorded in each file's history |
| 1d | Call 6: five-member ORACLE_TESTS everywhere; no live three-member form | PASS | ARCH-07 OD-145 selector row, ARCH-08 selector bullet + diagram, cicd-setup test/Tier-C/timing rows, BC-6.01.001 PC-7 (1.2.8: two new members join), BC-6.04.002 Pre-3, BC-6.04.001 PC-3, VP-034 (membership pointer, no restatement). Three-member wording only in `modified:` history |
| 1e | Call 4: timing unit = one hylo invocation; no live sum-over-steps | PASS | ARCH-08 sampling-unit paragraph, nfr-catalog NFR-001 binding note, BC-6.04.002 PC-1/PC-2/PC-3/EC-005, cicd-setup timing rows: per-(case, step) 1 warm-up + 20 samples, p95 gated per (case, step), "no summing over steps". Only negative forms of the sum exist |
| 1f | Call 8: Windows env U+FFFD substitution; lone-surrogate → invalid-UTF-8 leg removed from the env path | PASS | BC-2.01.001 PC-6 (minting site), BC-2.02.001 error table `invalid UTF-8` row, error-taxonomy `invalid UTF-8` row, BC-2.01.003 PC-3: all state Go's standard UTF-16 decoding substitutes the replacement character and a lone surrogate cannot reach the env path; the reason is "reachable from POSIX byte values only" |
| 1g | Call 3: max_depth range 0..1000; no live "any Int" for it | PASS | prd.md NFR-005 row, nfr-catalog NFR-005, interface-definitions range cell (0 = no ancestor walk, upper bound mirrors the sparkline history cap, labeled judgment call; classified as tunable key). Remaining "any Int" strings belong to other keys (timer margins, power bands, narrow_cols) where the wide range is intentional |
| 1h | Call 13: request selector drops only the text after the LAST number-sign | PASS | BC-1.04.001 Description + redirect-hop postcondition (rpartition/splittag rule; a path number-sign survives the wire), ARCH-03 comment block. No live "drops the fragment (at the first)" phrasing found in either file |
| 1i | Call 12: CP-C06/CP-C07 live; no live CP-C11/CP-C12 | PASS | Formerly-reserved ids are allocated in error-taxonomy register rows and in both owner BCs; CP-C11/CP-C12 appear only inside `modified:` history arrays (renumber notes) |
| 1j | Call 17: anchors defined and re-anchored | PASS | ARCH-03 closed anchor set gained both targets with table rows (input.go family, statusline.go family; "fourteen anchors"); BC-1.01.002 and BC-1.01.008 link the input anchor, BC-1.01.003 and BC-1.01.009 link the frame anchor. No bare unnamed-frame fragment remains; the guard anchor survives legitimately for guard.go links (BC-1.01.001, BC-1.07.008) |
| 2a | CP-C06/CP-C07 agreement across agent 2 / agent 5 / agent 7 files | PASS | error-taxonomy rows (mix-cache tin consult, composition-tail sum), BC-1.02.018 EC-009 + vector row, BC-1.02.007 EC-010 + vector row: same SL refs (586; 1181), same OD-160 tag, same "Go table test, not byte-parity" disposition |
| 2b | ARCH-03 defines every anchor the ss-01 BCs cite | PASS | Scripted census of `ARCH-03-statusline.md#…` fragments vs the defined set: all 14 targets used live are defined; zero undefined |
| 2c | VP-041 and BC-1.02.010 state the same NaN carve-out | PASS | Both: every comparison against now is false for NaN, so shown-with-absolute-bands coexists with a false reset-greater-than-now; VP-041 P-r quantifier/generator excludes NaN, BC-1.02.010 Inv 1 + VP-table row mirror it |
| 2d | Four CI legs agree (ARCH-08, cicd-setup, BC-6.04.001, VP-037) | PASS | Three OS legs from the toolchain line + ubuntu 1.26.0 floor leg, all required; branch-protection context list names all four plus lint/coverage/govulncheck/gitleaks; gofmt+govulncheck once in the ubuntu lint job, vet+staticcheck per OS leg; setup-python only in oracle jobs |
| 2e | Five ORACLE_TESTS members agree across all five carriers | PASS | Same five names in ARCH-07, ARCH-08, cicd-setup, BC-6.01.001, BC-6.04.002; plain/coverage/release skip the whole pattern; three Python-installing jobs each run their own member(s) |
| 3 | Citations added this pass resolve | PASS | 115 distinct BC ids in added lines all have files; 33 VP ids all exist; 39 BC→(EC/PC/Inv) cross-citations all resolve at the target file; OD-160/OD-193/OD-194 etc. present in the decisions log |
| 4 | No line-number pointers added | PASS | Zero `BC-x.yy.zzz:NN` / `ARCH-xx:NN` matches in added diff lines |
| 5 | VP bcs: ↔ VP-INDEX ↔ BC VP-tables, both directions | PASS | Scripted: frontmatter→BC edges = 289 (= the planned total), coverage-map edges = 289, 154/154 BCs covered, 0 forward-only, 0 reverse-only on authoritative surfaces (VP-table rows + VP Anchors bullets). Observation below on two prose-only raw hits |
| 6 | Frontmatter YAML parses for every changed file | PASS | All 86 changed files parse without error under the prescribed parse expression |
| 7 | Changed canonical vectors derive field-by-field from the legacy reference | PASS | Walks below |

## Canonical-vector walks (check 7 detail)

All derivations ran against the frozen legacy reference file (repo-relative `legacy/dgx_statusline.py`), reading the code that sets each expected-output field. No field resisted derivation.

1. **Lone-surrogate display-name vectors (BC-1.01.001 edge-case row, BC-1.01.008, BC-1.01.009; seeded proc_start).**
   - Cache content "{seeded proc_start} + rl + rl_ts exactly": `main()` calls `effective_rl` before any rendering (≈SL:303→307-308), which loads the cache, sets `rl` and `rl_ts`, and saves; with rows = 1 the sample getter is never entered, and the window-start consult short-circuits on the cached, harness-seeded `proc_start` (no probe, no write). Exactly three keys. Correct in all three vector rows.
   - "rl/rl_ts written before the fault": the rl save precedes lane assembly and the single stdout write, per the call order above.
   - "degraded 29 bytes, exit 0": the only encoding point for the surrogate is the final print (strict UTF-8 text mode raises on the lone surrogate; string assembly and width trimming never encode). The guard prints GREY + "statusline degraded" + RESET + newline; GREY is the 5-byte 90-level grey escape and RESET the 4-byte reset, giving 5+19+4+1 = 29 bytes, exit 0.
   - Byte-pinning of the cache content ("byte-pinned" in BC-1.01.001) is consistent: no writer touches the cache between the rl save and process exit.
2. **BC-1.04.009 EC-012 (negative giant plots the lowest glyph).** With the plotted value a huge negative integer: the point-scaling helper's `max(v, 0.0)` compares exactly and returns the float 0.0 without converting v (arbitrary-precision ints compare to float exactly in the reference interpreter), so no overflow occurs on the negative leg — while a positive giant at or above the long→float boundary overflows at the divide in the same helper (SL:674), matching EC-011's positive-only bound. The window top at SL:671 takes the max over the plotted values against the floor, which a negative never wins; index 0 selects the lowest glyph. The claimed byte-equality to EC-004's [-5, 2] vector derives: both pairs yield identical index sequences through identical arithmetic.
3. **BC-1.02.007 EC-010 (foreign non-numeric bucket at the composition tail).** SL:1181 is exactly `if not counts or sum(counts[:3]) <= 0:` inside the mix-segment builder; a non-numeric member raises TypeError at the sum, propagating to the top-level guard, which prints the same grey degraded line ("never blank, never nonzero") and exits 0. The vector's expected stdout and error class, and the Go-table-test (not byte-parity) disposition, all derive.

## Observation (non-blocking)

- BC-6.01.002 PC-4's prose (the comparator LF-normalization sentence) cites two VPs by id whose `bcs:` do not list this contract, and the VP-INDEX standing-residue enumeration (3 design references + 3 removal-note citations + 2 scope-split contrast mentions) does not name these two raw hits. The citations pre-date this pass and sit outside the authoritative VP-table/VP-Anchors surfaces, so check 5 passes; a future sync could either reciprocate them into the two VPs' `bcs:` or extend the residue definition by one line so the raw-hit census (10) matches the recorded residue count (8) exactly.

## Hygiene

Report contains no identities, machine paths, network addresses, hostnames or account handles; line references are to the repo-local legacy reference file and spec files; interpolation values quoted (the 90-level grey escape, boundary exponents) are protocol/mathematical constants on the public allowlist by nature.

## Closing fixes

None required. Recommended (optional, next sync or pass-13 residual): resolve the BC-6.01.002 observation above.
