---
document_type: sync-check
phase: 1d
pass: 13
date: 2026-11-18
---

# Pass-13 sync check (ADV-P13 remediation, 2026-11-18)

Scope: the uncommitted `specs/` diff (75 files, +1191/−572) checked against
`cycles/phase-1-spec-crystallization/pass-13-remediation-plan.md` (orchestrator
calls 1-19). Methods: scripted greps over live spec text (history/provenance
lines excluded from contradiction counts), a YAML-parsed recount of all 41 VP
`bcs:` lists against all 154 BC VP-tables and the VP-INDEX coverage map, a
citation-resolution sweep over every added diff line, and three field-by-field
vector walks of the nine pass-13-touched canonical vector tables against the
legacy oracle source. History/provenance lines and OD-log ruling rows are not
contradictions (SC-32 precedent).

## Result table

| Check | Verdict | Notes (failure locations in italics) |
|---|---|---|
| 1. Calls 1-19 present in every named file, no live contradiction | PASS (call 7 partial) | Calls 1-6 and 8-19 verified on disk; one residual under call 7 — *BC-1.05.004 "Owning component" line and BC-1.05.005 "Owning component" line still say writes go through the injected `Store` seam*, the wording call 7 replaced in ARCH-00 (details below) |
| 2. Cross-agent agreement | PASS (1 of 5 clusters fails) | CP-C register ↔ BC citations clean both directions (32 rows; the only two raw hits were slashed-shorthand false positives). E-CLI-003 agrees across error-taxonomy, prd.md §5, ARCH-00 Principle 4 and VP-004. Hylo-child exact key set (conditional `WINDOW_AGE_MAX_DEPTH=0` on the cache-003 empty-bin declaration) agrees across BC-6.01.002 PC-1/PC-3/CTV, ARCH-07 trigger text and VP-034. CI job/leg structure agrees across ARCH-08, cicd-setup and BC-6.04.001 (four test legs + floor leg; Tier A and timing each three-OS with setup-python and the printed patch on every leg; lint gofmt-only; govulncheck its own job; no separate Tier B job; coverage its own ubuntu job). **FAIL:** internal/cost API — ARCH-03's declared-API block (no I/O; pure functions; CacheStore owned by internal/statusline) vs the residual `Store`-seam sentences in BC-1.05.004/.005 |
| 3. Citations added this pass resolve | PASS | Scripted sweep over all added lines: BC ids (files exist), VP ids, PC/EC numbers (positional-numbered Pre/Postconditions lists and EC tables), Inv numbers, E-xxx-NNN register ids, CP-xxx register ids, OD numbers (<= OD-194), NFR ids, and SL:line pointers (all <= the oracle's 1245 lines) resolve. One informational hit: CP-S07 appears in an added BC-1.02.006 history row and resolves only via the register's slashed shorthand (the CP-S06/S07 pairing in the E-REN-002 carrier text and the register outro); no standalone CP-S07 row exists and no live added text introduces a new standalone citation — pre-existing equilibrium, not a pass-13 defect |
| 4. No `BC-x.yy.zzz:NN` / `ARCH-xx:NN` line pointers added | PASS | Single grep hit (`ARCH-02:91`) rides in a re-emitted history `modified:` list of the VP-017 file (pre-existing in the minus line); the new 1.8 entry adds no line-number pointer |
| 5. VP `bcs:` ↔ VP-INDEX map ↔ BC VP-table rows, both directions | PASS | Scripted recount (YAML-parsed frontmatter; packed first cells like `VP-028, VP-001` parsed): **297 directed VP→BC edges = the expected 297**; 0 forward-only, 0 reverse-only among live table rows; 154/154 coverage-map rows parsed, 0 map mismatches; no BC left without a VP-table row. Duplicate rows within one BC table are separate-property rows (e.g. two VP-036 rows in BC-6.04.002), not drift |
| 6. Frontmatter parses (all 75 changed files) | PASS | `yaml.safe_load` on every changed file's frontmatter block: zero failures |
| 7. Canonical vectors walked against legacy (setup + expected output, field by field) | PASS (2 setup defects) | 9 BCs, every vector row walked against `legacy/dgx_statusline.py`: BC-1.01.001 (4 rows), BC-1.01.008 (7), BC-1.01.009 (5), BC-1.02.029 (8 incl. the CP-O12 leg), BC-1.03.005 (7), BC-1.03.006 (11), BC-1.04.007 (5), BC-1.04.015 (5), BC-1.04.016 (7). Zero outcome contradictions, zero CANNOT-DERIVE fields. Two setup-admissibility defects of the pass-13 B01 class (below). Soft, cross-referenced dependency noted: BC-1.03.006's turn-drop row rests on the template declared in BC-1.03.016 PC2 (copied in BC-1.03.010), explicitly cited in-file |

## Findings (closing fixes)

1. **Retired `Store`-seam wording survives in two cost BCs (call 7 residual; Major).**
   ARCH-00's package table and ARCH-03's declared-API block now state the ruled
   form: internal/cost does no I/O and exposes pure functions; internal/statusline
   loads and saves the cost-history file through its own CacheStore (depth
   constant 990 lives with that cache file). But *BC-1.05.004 "Owning component"
   line* and *BC-1.05.005 "Owning component" line* still close with the replaced
   phrase "writes go through the injected `Store` seam", which no longer has a
   referent (ARCH-00's `Store` row is gone). Fix: respell both sentences to the
   ARCH-03 declared-API form (pure core; the record-before-percentile order kept;
   the persistence seam named CacheStore in internal/statusline).

2. **Missing `proc_start` seed in two new vector setups (corpus admission rule; Minor, setup-only).**
   The corpus admission rule (BC-3.02.001 parity-invariants item 4: every corpus
   case seeds `proc_start` or is the cache-003 case) is violated by the setups of
   *BC-1.03.005's canonical parse-leg row* and *BC-1.03.006's canonical
   save-failure-cycle row*: both declare a truthy session id against an empty
   cache with no `proc_start` seed and are not the cache-003 case — exactly the
   defect class pass-13 B01 fixed in BC-1.02.029 v1.8, which added the seed for
   the same rule. Outcome fields are unaffected (a None probe writes nothing;
   the degraded line, the byte counts and the cache contents derive identically
   with the seed added). Fix: add the `proc_start` seed (or a seeding sentence)
   to both rows' setup text and re-stamp.

3. **Informational, no action required.** (a) CP-S07 resolves only as the slashed
   shorthand inside the error-taxonomy register's carrier/outro prose; no
   standalone row exists (S06→S08). Long-standing, untouched this pass. (b) The
   OD-log row for OD-186 still spells the original 1..1000 range for the rename
   retry delay; ruling rows are provenance and the live registry
   (interface-definitions, ARCH-04, VP-018) uniformly carries the paired 1..100 /
   0..10 bounds with the at-most-1000-ms-per-Save rationale — no change wanted.

## Verified rule surfaces (check 1 evidence, by call)

- Call 1: error-taxonomy CP-C register extends to CP-C32 with per-site rows and
  the family label "the CP-C family (OD-160)"; every live "CP-C01..C10"
  appearance is framed as the former label or history.
- Call 2: BC-6.03.002 PC-1 defines the one open CRLF→LF conversion for every
  Windows oracle-stdout comparison; BC-6.01.001 PC-3 (version probe) and
  BC-6.01.003 PC-4 (clock canary) cite it.
- Call 3: BC-6.01.003 PC-4/PC-5 (clock leg the gating detector; stdio leg UTF-8
  round trip only; stdio no-shim negative control withdrawn; no "LF half"
  discriminator); BC-6.01.002 PC-4 (no newline reconfigure).
- Call 4: conditional `HYLO_STATUSLINE_WINDOW_AGE_MAX_DEPTH=0` keyed to the
  cache-003 empty-bin declaration in BC-6.01.002 (PC-1/PC-3/CTV), ARCH-07 and
  VP-034; "subprocess-fake table" retired everywhere live (VP-034, ARCH-07,
  BC-6.01.002, BC-6.03.003/BC-3.02.002 histories).
- Call 5: Tier A and timing jobs each three-OS with setup-python and the printed
  resolved patch on every leg; Tier B census owned by the plain legs; no
  separate Tier B job (ARCH-08, cicd-setup, BC-6.04.001).
- Call 6: govulncheck its own ubuntu job, required in the same change as the
  go.mod toolchain line; lint job gofmt-only and required; branch-protection
  contexts match the emitted check-run names.
- Call 7: ARCH-00 package table replaced; ARCH-03 declares the cost API
  (purity boundary, function names, step 7c order) — residual in finding 1.
- Call 8: E-CLI-003 in the error-taxonomy closed exit table; prd.md §5 and
  ARCH-00 Principle 4 list it as the one non-zero exit outside
  validate/usage/harness; VP-004 aligned.
- Call 9: VP-001 main-entry legal set is the four exclusive surfaces (29-byte
  line; VP-002 unknown-flag grammar regex; E-CFG-001 config-error regex; normal
  render of one or two non-empty LF-terminated rows); zero bytes removed;
  "render-grammar classifier" appears only as an explicit negation.
- Call 10: per-(case, step) unit, cold-start replay, 100.0 ms ceiling breach on
  p95 (exactly 100.0 ms passes) in VP-036, ARCH-08, BC-6.04.002 and the brief
  ("at most 100 ms"); no live "steady-state"/"binds per case" timing wording
  (the unrelated thermodynamic sense in BC-1.04.021 remains, correctly).
- Call 11: coverage exclusion stated as the five-member ORACLE_TESTS pattern
  (ARCH-07 pattern constant; ARCH-08/cicd-setup coverage rows), every other
  in-process test under the internal tree counts.
- Call 12: BC-1.03.021 PC5 states the measured session-cache save/reload
  behavior (reload bounded at 991 nesting levels) measured in an isolated
  temporary HOME and cwd with the oracle interpreter; the equal-budget claim is
  confined to git and cost-history.
- Call 13: cicd-setup states the public-GitHub-owner exemption for the D1 module
  path's owner segment explicitly.
- Call 14: NFR-005's four-cap render-state list plus the separately listed
  ancestor-walk bound and the buffered LF-less tail sentence (no invented cap).
- Call 15: interface-definitions, ARCH-04 and VP-018 carry the paired 1..100 /
  0..10 bounds with the at-most-1000-ms-per-Save labeled judgment call.
- Call 16: R-009 security row in risk-register with the pinned parser limits and
  the Phase 6 fuzz target; gate-notes security list updated.
- Call 17: VP-035 planted canaries runtime-composed from committed fragments,
  flagged shapes only, composed values in no committed file; exempt shapes are
  negative controls.
- Call 18: Tier A and timing timeouts derived from corpus size with the formula
  beside each (cicd-setup rows).
- Call 19: `%LOCALAPPDATA%\hylo\cache` per OD-144 in every live location
  checked (prd.md OQ-11, VP-032, BC-3.01.001, BC-2.03.002, ARCH-04/05/07,
  interface-definitions); the bare-directory form appears only as the
  shared-dir/ConfigDir contrast in BC-3.01.001 and as OD-log ruling history.

## Gate

**PASS WITH FIXES** — no convergence blocker; the two closing fixes (1 and 2)
are single-sentence respells in four files. Consistency score 91% (33.5 of 37
weighted sub-items: 18.5/19 calls, 4/5 agreement clusters, checks 3-6 clean,
7/9 vector files clean).
