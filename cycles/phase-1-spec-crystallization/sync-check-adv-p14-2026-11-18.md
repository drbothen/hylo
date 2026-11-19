---
document_type: sync-check
phase: 1d
pass: 14
date: 2026-11-18
source: cycles/phase-1-spec-crystallization/pass-14-remediation-plan.md
diff_scope: uncommitted working-tree diff over specs/ (86 files, +1083/-491)
producer: consistency-validator
---

# Pass-14 sync check (adversarial pass 14 remediation)

Method: the 17 orchestrator calls of `pass-14-remediation-plan.md` were checked for
PRESENCE in every file the plan names (live body text, not only history entries), and
the whole uncommitted `specs/` diff was swept for live contradicting statements (history
lines, explicit withdrawals, and OD-log ruling rows not counted as contradictions).
Scripted recounts are described per check; measured claims were re-measured on the
pinned interpreter (CPython 3.11.7) and walked against `legacy/dgx_statusline.py`.

## Verdict table

| # | Check | Verdict | Notes |
|---|-------|---------|-------|
| 1 | Calls 1-17 present in every named file; no live contradiction | FAIL (1 gap) | Finding F1: call 5 present in BC-2.01.004, BC-2.01.005, error-taxonomy, but BC-5.03.001 Inv 1's live text not extended (history entry only) |
| 2 | Cross-agent agreement (rider register, CP-C register, cost API, CI structure) | FAIL (1 gap) | Finding F2: VP-012 live prose names the superseded OD-76 concrete test name in two places |
| 3 | Citations added this pass resolve | PASS | 180 distinct ids in added lines; all resolve (BC, VP, CP, DI, E-*; CP-T04/05/06 resolve to BC-1.03.018's D4-EX-2 row tables per the pass-10 row-id rule) |
| 4 | No line-number pointers added in the diff | PASS | Sole regex hit (`VP-013:54`, VP-029) is a pass-11-era history entry and body line outside this pass's hunks; this pass's VP-029 hunk only respells leg (b) and appends 1.7 |
| 5 | VP `bcs:` vs VP-INDEX vs BC VP-tables, scripted recount | PASS | 41 VP files; 312 directed `bcs:` edges = 154 map rows' 312 edges; 0 forward-only, 0 reverse-only, 0 duplicate map cells; every BC-body VP mention covered by the map (0 reverse); every routed edge's VP present in its BC body |
| 6 | Changed-file frontmatter parses; `modified:` ascending | PASS | 86/86 parse with the prescribed loader; every pass-14 entry appended LAST; version trails monotone; last entry carries the current `version:` in all files (pass-14 C2-08 rule holds) |
| 7 | Canonical vectors changed this pass walked field-by-field vs legacy | PASS | Walks below; no undecipherable field encountered; measured boundary 2**1024 - 2**970 confirmed exact (that value itself overflows) |

Gate result: **FAIL** — two findings (F2 high, F1 medium) before convergence.

## Check 1 - call-by-call presence

| Call | Present in | Evidence (section/ID) |
|---|---|---|
| 1 rider register in code tree | BC-6.03.004, VP-012 | BC-6.03.004 Preconditions 3: closed set of TWELVE ids; "Rider register (machine-readable; A2-01, pass-14 orchestrator call 1)" table with `id` / `{package}` / tests columns for all 12 ids and the per-test provenance narrative; VP-012 leg loads `internal/parity/testdata/exclusion-riders.json`, asserts the key set equals the twelve-element closed set, verifies each listed test via `go test -list` over the named package. The pass-13 parsed-from-BC formulation is withdrawn in VP-012 v1.26 and no live text retains it |
| 2 cost API carries config | ARCH-03, BC-1.05.004/.005, VP-020 | ARCH-03 §Interfaces `CostConfig` (six keys: `window_s`, `min_usd`, `min_sessions`, `rate_min_api_ms`, `percentiles`, `record_throttle_s`, citing BC-1.05.005 Pre 3 and BC-1.05.004 Pre 2), `RecordCost(history, sess, cfg CostConfig, now)`, "NO hard-coded" throttle note; VP-020 sketch calls `RecordCost(hist, session, costCfg, now)` |
| 3 exact threshold values | ARCH-03 | `CostThresholds` returns `*[2]pyfmt.Num` pairs, `pyfmt.NumCmp`, pinned example `9007199254740995 >= 9007199254740996.0` False. No `*[2]float64` signature remains anywhere in specs |
| 4 foreign-cache matrix | error-taxonomy + owner BCs | CP-C family "Method" paragraph (eight load_cache calls, five cache files, six fault classes), matrix rows CP-C01..C57 (contiguous; CP-C33..C57 = the 25 new raising cells), pinned non-raising cells, "Completeness declaration ... under the method above"; CP-C01 step attribution corrected (step 3, SL:307-308/311, step 4 SL:324, step 6 unreachable); BC-1.02.013 EC-012 + vector rows; single id-range edge cases per owner BC (BC-1.04.004/.006/.007/.008/.010/.011/.012/.013) |
| 5 label width reason | BC-2.01.004, BC-2.01.005, BC-5.03.001, error-taxonomy | BC-2.01.004 OD-184 Scope passage and PC-6/PC-13 scope text extend the ONLY-consulted set to the nine width-bounded `statusline.labels.*` members; BC-2.01.005 PC-6 same bound + reason; error-taxonomy reason row "the three `pill.label_*` keys AND the nine OD-194 `statusline.labels.*` keys". GAP = Finding F1 (BC-5.03.001) |
| 6 LF goldens on every OS | ARCH-07 | Golden-update-flag row: `-update` applies the BC-6.03.002 PC-1 CRLF-to-LF conversion to the oracle's stdout BEFORE writing any golden, "LF ON EVERY OS"; consistent with BC-6.03.002 PC-1 (comparator conversion definition) and VP-009/VP-011/VP-034/BC-1.01.001 wording (comparator-side, hylo bytes never converted) |
| 7 D4-EX-3 member scope | BC-6.03.004 | Oracle self-consistency leg MEMBER SCOPE: excluded by legacy site (session `rl_ts`/`fetch_ts`/`ts`, sparkline `hist`, git-cache `ts`, cost-history entry `ts`), COMPARED REMAINDER stated (`rl`, `up`, `sample`, `proc_start`; `branch`; `lane`, `usd`, `api_ms`, `src`; mix cache fully) |
| 8 empty List value | BC-2.01.005, BC-2.01.001 | BC-2.01.005 PC-7 default-only rule: `HYLO_STATUSLINE_LIMITS_WINDOWS=` is the empty list, not the default, giving `out of range`; BC-2.01.001 scopes `expected non-empty control-free text` to TEXT keys explicitly (List empty value IS the empty list) |
| 9 int64 overflow reason | BC-2.02.001, BC-2.02.003 | BC-2.02.001 "Numeric-range failures by type": rule 2 `negative` fires BEFORE the int64-overflow clause of rule 3, canonical precedence confirmed pass-14; BC-2.02.003 PC-4: outside-int64 result is NOT a grammar failure, goes to the range check |
| 10 `~` without home | BC-2.03.002 | PC-4 states both exact lines: path-grammar `home directory unknown` for a `~/` cache-dir key with home unset/relative; `cannot determine cache directory (HOME unset)` only when no cache-dir key is set |
| 11 surrogate storage | BC-5.02.004, BC-2.01.005 | BC-5.02.004 Strings section: POSIX byte mapped to U+DC00+b stored in the WTF-8 form, prefix matching over those bytes; BC-2.01.005 PC-6 List-item passage cross-pins the same form |
| 12 subagent dispatch | ARCH-01, BC-4.01.001 | ARCH-01: exact `--subagent` argument routes to `runStatuslineSubagent(args, ...)`, `runStatusline` renders main mode only; BC-4.01.001 PC-1 restated identically, within-runStatusline dispatch wording withdrawn |
| 13 cost file I/O home | VP-018, VP-020, VP-INDEX | VP-018 `module: internal/statusline (cache.go, cost-history CacheStore)`; VP-020 `module: internal/statusline (cost-history CacheStore I/O), internal/cost (pure record/throttle properties)`; VP-INDEX module cells synced (re-machine-checked in the recount); no live text places cost-history file I/O inside `internal/cost` |
| 14 govulncheck branch protection | cicd-setup, ARCH-08, BC-6.04.001 | Job table `govulncheck (required)` marked conditional; required-check section: the list carries it ONLY FROM the change that adds go.mod's `toolchain` line, until then "reports but is not required"; ARCH-08 ACTIVATION-IS-SAME-CHANGE note; BC-6.04.001 PC-3 live: own job, runs and reports every change, becomes required in the same change. No live "required now" statement remains |
| 15 censuses | cicd-setup, ARCH-08 | Tier A: pair count P of (case, step) comparisons with committed and runtime pair-census equality; timing: same pair accounting plus case census; Tier B: `tier-b: N goldens compared` counts comparisons made (variant or default fallback, each case once) and equals the leg's case count; govulncheck positive coverage = packages analysed (JSON) compared with `go list ./...`. No live census counts cases only |
| 16 NFR-002 families | nfr-catalog, error-taxonomy | NFR-002 target gains CP-O06..O09 (skip-render) and the foreign-cache family CP-C01..C57 (OD-160, degrade-observable, Go table tests), validation route via owner BCs' id-range edge cases; E-REN-002 derived carrier set walked against owner BC EC text (37 carriers) |
| 17 residual + B02 | BC-1.02.022 et al. | BC-1.02.022 CTV rows: `"//"` Windows golden renders the label as two backslashes (matching the orchestrator's measured `ntpath.normpath('//' )`); residual-sweep stamps present in ss-01/ss-06 owners and the supplements |

Contradiction sweep: every required grep (rider register parsed from a BC, config-less
cost signatures, float64 pairs, pill-only width scope, goldens without conversion,
non-empty-text reason on an empty List, int64 overflow as a grammar error, cost I/O in
`internal/cost`, govulncheck required-now, cases-only censuses) returns only history
lines, withdrawal notes, or ruling-consistent text. No live negation found beyond F1.

## Check 2 - cross-agent agreement

(a) **Rider register vs VP-012 vs owning BCs** - the register's 12 id/package/test rows
agree with VP-012's leg description (committed JSON, key-set equality, `go test -list`
per package, fail on missing name). Every named test is named in its owning contract,
with the documented delegations honored (BC-3.02.002's live PC delegates the final
OD-76 name to BC-6.03.004; `TestTranscript_D4EX2_T01` is pinned by BC-6.03.004's own
CTV with BC-1.03.019 supplying the `TestTranscript_D4EX2_<row>` form and T-ids).
**One disagreement found: F2 below** (VP-012 still carries the superseded OD-76 name in
two live passages).

(b) **CP-C register two directions, scripted** - 57 rows, contiguous CP-C01..C57.
Register-to-BC: every owner id listed in the register appears in the owner BC's body
(two cells via BC-1.01.009's step-table family shorthand `CP-C01/C02` and `CP-C03/C04`,
same citation class the register's 1.22 sweep disclosed). BC-to-register: all CP-C
citations in BC bodies resolve; the 8 non-owner citations are explanatory
cross-references or renumbering-history notes (BC-1.06.001's `CP-C11..CP-C19` range
attribution "out of parity scope", BC-1.01.001's CP-C10 site citation crediting
BC-1.01.009 PC2, BC-1.02.018's and BC-1.02.007's CP-C11-to-CP-C06 / CP-C12-to-CP-C07
renumbering notes), none phrased as ownership. Reproduces the taxonomy's 1.22 scripted
two-way pass.

(c) **ARCH-03 cost API vs cost BCs and VP-020** - signatures and `CostConfig` keys in
ARCH-03 §Interfaces match BC-1.05.004 Pre 2 (`statusline.cost.record_throttle_s`,
T-022) and BC-1.05.005 Pre 3 (`window_s`, `min_usd`, `min_sessions`, `rate_min_api_ms`
cc/other map, `percentiles` ascending pair); BC-1.05.006 and BC-1.05.009 quote the
declared API (pure core, no I/O; `internal/statusline` loads/saves via `CacheStore`);
VP-020's skeleton goes through the CacheStore seam and calls the cfg-carrying
`RecordCost`. Agreed.

(d) **CI structure across ARCH-08, cicd-setup, BC-6.04.001, VP-037** - govulncheck is
its own ci.yml job, runs and reports on every change, becomes a required check in the
same change that adds go.mod's `toolchain` line (never onto the no-patch 1.26.0
toolchain); gofmt runs once in the required ubuntu lint job; coverage is its own job
with the committed-package-manifest arithmetic; Tier A and the timing job run on all
three OSes with setup-python printing the resolved patch; Tier B lives in the plain
legs which own the tier-b census. All four documents agree; VP-037's skeleton is
declared non-normative (illustrative sketch) and its leg contents match.

## Check 3 - citations resolve

Added lines cite 180 distinct ids across BC-, VP-, CP-, DI- and E- families. BC ids
match contract files; VP ids match the catalog (VP-INDEX); CP ids resolve to the
error-taxonomy register, except CP-T04/T05/T06 which are BC-1.03.018's owner-defined
D4-EX-2 row ids cited "by row id, not by drifted line numbers" per the pass-10 rule -
verified present in that contract's tables. DI ids resolve to the domain invariants
file; E-ids resolve to the taxonomy/PRD. Nothing unresolved.

## Check 4 - line-number pointers

Regex sweep for `BC-x.yy.zzz:NN`, `ARCH-xx:NN` and analogous spec-internal `VP-NNN:NN`
pointers over added lines: exactly one hit (`VP-013:54`, in VP-029). It sits in a
pass-11 history entry and a pass-11 body line outside this pass's hunks (the pass-14
VP-029 hunk appends entry 1.7 and respells leg (b)); the YAML `modified:` array is a
single line, so the old text is re-emitted wholesale by the append. No pointer was
INTRODUCED by pass-14. Legacy-source anchors (`SL:...`) remain the established id-plus-
row citation practice and are out of scope for this check per its stated patterns.

## Check 5 - traceability recount (scripted)

- 41 VP files; `bcs:` frontmatter yields **312 directed VP-to-BC edges** - matches the
  VP-INDEX v1.30 recorded count of 312.
- VP-INDEX map: **154 rows**, 312 edges; set-equal to the `bcs:` edge set in both
  directions (0 forward-only, 0 reverse-only), 0 duplicate cells.
- BC bodies: 375 VP-table rows; every row appears in its map row (0 reverse); every
  routed edge's VP is present in its owning BC's body (0 orphans; 54 edges are keyed to
  PC/prose text beside the VP-table row, the standing frontmatter-rider citation class
  the index discloses).
- Module-column sync (call 13): VP-018/VP-020 `module:` fields agree with their
  VP-INDEX Catalog cells.

## Check 6 - frontmatter (scripted)

All 86 changed files parse with the prescribed loader. In every file the newest history
entry is the LAST element and carries the file's current `version:`; version trails are
monotone non-decreasing; no pass-14 entry was inserted ahead of a lower version (the
C2-08 defect class is fixed on disk, including the taxonomy's re-slotted entry).

## Check 7 - canonical vectors walked against legacy

Vectors and vector-bearing edge cases added this pass, walked setup-plus-expected
against `legacy/dgx_statusline.py`:

- BC-1.02.013 EC-012 + CTV rows (session cache `[]`): `effective_rl` item assignment
  raises TypeError with stdin `rl` present and `.get` AttributeError when absent;
  `get_sample`'s `.get` faults at step 4; the step-6 consult is unreachable with a
  non-object cache; outcome is the guard line, exit 0. All four claims read directly
  from the source; the main flow calls `effective_rl` before the window-start consult.
- EC-008/CP-C02/CP-C33 (`rl` object, `rl_ts` string or exact giant int): the
  short-circuit line's `now - ts` raises TypeError (string) or OverflowError (giant) -
  measured `1.0 - 10**400` raises OverflowError. Verified.
- Git-cache and cost-history sites (CP-C49 at the TTL line, CP-C50 at the throttle and
  scan subtractions, CP-C08 scalar): same `now - c.get("ts", 0)` shapes. Verified.
- Idle gate (CP-C47): positive giant passes `last > 0` exactly, then
  `time.time() - last` raises OverflowError; negative giant is pinned non-raising by
  the same gate. Matches legacy lines verbatim.
- TTFT gate (CP-C40): `math.isnan(giant)` raises OverflowError - measured. The
  conversion boundary claim `|n| >= 2**1024 - 2**970` was re-measured: that exact value
  is the smallest failing int (`float()` raises on it), so the rows' boundary is exact.
- Format-family rows (CP-C37/CP-C39/CP-C41/CP-C44 and the `.2f` usd site): int-times-int
  stays exact, then `:.0f`/`.2f` of a giant raises OverflowError - measured.
- Composition share (CP-C52): true-division is ratio-dependent - `10**400/10**299`
  succeeds, a giant over a small divisor raises - matching the row's "giant quotient
  over a comparable-magnitude total converts silently; measured".
- Utilization product (CP-C48/CP-O12): the int product stays exact; the divide of the
  `eq` expression raises OverflowError when the quotient is unrepresentable (measured
  `10**308*10**310/1e6` raises) - consistent with the row's SL:626/633 span attribution
  and typed-degrade outcome.
- Turn machine (CP-C56/CP-C57): `cur.get("id")` consult at the cited site; a truthy
  non-dict `cur` raises AttributeError; float*str is TypeError ("can't multiply sequence
  by non-int"), no sequence-repeat fallback - measured.
- Mix-cache negative size (BC-1.03.002 EC-009): with `size < off` false and a negative
  seek argument, the open guard's `except OSError` returns without writing - the
  mechanism, the catch site, and the no-write outcome read as stated.
- VP-021 cold-start colour leg (A2-02): legacy's dollar ladder is grey below
  `COST_MIN_USD` (1.0), threshold-chosen otherwise, and on cold start yellow at or above
  `COST_FALLBACK_YELLOW` (25.0) else white; `$`/h is grey when no rate thresholds exist.
  The corrected leg text matches the legacy ladder and constants exactly.
- Giant-int non-raise pins: `min(giant, 100.0)` returns 100.0 and renders `100%`,
  matching the pinned positive-giant KV outcome in the matrix's non-raising cells.

No field was found that could not be derived from legacy plus the pinned interpreter.

## Findings and closing fixes

**F2 (high; check 2a) - VP-012 live prose carries the superseded OD-76 concrete test
name in two places.** Pass-14's register minted `TestWindowStart_OD76_TrueStart` as the
FINAL concrete OD-76 name (BC-6.03.004's rider-register table and its provenance note;
BC-3.02.002's live precondition delegates the final name to BC-6.03.004). VP-012's live
text still names `TestWindowStart_OD76_NativeProbeDiffTable` twice: in the Named-Tests
enumeration (the `BC-3.02.002 (OD-76, ...)` item) and in the register-content
enumeration near the end of the file (the "concrete member of the formerly abbreviated
family" passage). The v1.26 pass-14 history entry did not respell them. Because
VP-012's leg is defined as agreement between the committed JSON, the BC register table,
and the VP's own description, the two stale spellings are a fake-fail risk for the
factory-side sync comparison.

Closing fix (owner: VP-012's producer): respell both live occurrences to
`TestWindowStart_OD76_TrueStart` with the mint provenance (BC-6.03.004 v1.3.6,
per-BC-3.02.002 deferral), append the corresponding `modified:` entry, keep `bcs:`
unchanged.

**F1 (medium; check 1, call 5) - BC-5.03.001 Inv 1's live text was not extended to the
nine OD-194 width-bounded label members.** The 1.2.2 history entry says the
validation-only ban scope extends to the nine `statusline.labels.*` members beside the
pill-label bound, but Invariant 1's live parenthetical still characterizes the OD-170
table function's validation as "the pill-label 1..16 display-width bound" only. A reader
of the live body concludes the table function validates only the pill-label keys,
contradicting BC-2.01.004's scope passages and BC-2.01.005 PC-6 (same bound and reason
for the nine members). History-only propagation is the exact drift class this pass
fixed elsewhere.

Closing fix (owner: BC-5.03.001's producer): extend Inv 1's parenthetical to "the
pill-label 1..16 display-width bound AND the nine width-bounded `statusline.labels.*`
members (OD-194)"; no history-entry addition beyond the existing 1.2.2 entry is needed
(it already claims the extension), but the version bump should accompany the body edit.

Non-blocking observation: VP-037's illustrative sketch (explicitly non-normative,
OD-182) bundles gitleaks into the per-leg step list; the normative documents keep
gitleaks as its own full-history job. No action required this pass.

## Gate

FAIL - resolve F2 and F1, then re-run the two-way register/name comparison (F2) and a
body-vs-history spot check on BC-5.03.001 (F1). All other sync surfaces for pass-14 are
clean on disk: the 312-edge recount, the 57-row CP-C register, the frontmatter hygiene,
and the vector walks.
