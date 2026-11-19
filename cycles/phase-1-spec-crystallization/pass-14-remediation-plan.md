---
document_type: remediation-plan
phase: 1d
pass: 14
date: 2026-11-18
source: adversarial-reviews/pass-14.md, adversarial-reviews/ADV-P14-INDEX.md
---

# Pass-14 remediation plan (canonical calls)

Read with the Rules section of `pass-4-remediation-plan.md` and the gates of passes 9-13 (YAML parse after every edit; for-all properties derived from every PC/EC/exception and walked against legacy; state only what you measured, bracketing boundaries on both sides; ASCII wire goldens; cite by section/ID + PC/EC/Inv/row, never line numbers; synthetic values on the pre-push hook allowlist; edit only your file set, list out-of-set hits; when a fix changes a rule, grep every sibling that states it and list each hit; escape-bearing text is written with a script and verified; a vector's setup text is part of the vector; new ids and anchors are minted only by the file that owns them; a call applies to every file it names, BC files included). New this pass: **keep `modified:` lists in ascending order when you append** (pass-14 C2-08 found three files with a new entry inserted ahead of lower versions).

Stop rule (OD-195): Phase 1d stops after 2 consecutive passes with zero CRITICAL/HIGH/MEDIUM findings; every finding of every severity is still fixed each pass. Pass 14 is NOT_CLEAN (3 HIGH, 25 MEDIUM). No owner rulings this pass. Next free OD: OD-196.

## Orchestrator calls (binding; checked against the OD log)

1. **Rider register lives in the code tree (A2-01).** `.factory/` is git-ignored on main, so no Go test can read a BC file. The rider register is a committed, machine-readable file in the code tree, `internal/parity/testdata/exclusion-riders.json`: for each of the 12 closed exclusion ids, a non-empty list of concrete `{package, test}` pairs (no globs). BC-6.03.004's register is the spec source and gains a package column and concrete test names for every id (D4-EX-1, OD-30, OD-76, OD-160, OD-161, OD-166, OD-181, D4-EX-2 included). VP-012's leg reads the committed JSON, checks its key set equals the closed set, and checks that every listed test exists (`go test -list` over the named package), failing on any missing name. The factory-side sync check compares the JSON content stated in BC-6.03.004 with the register table.
2. **Cost API carries its config (A01, C2-03).** `CostConfig` gains every cost key the cost BCs use (at least `statusline.cost.record_throttle_s`, plus the keys BC-1.05.004/.005 Pre list); `RecordCost(history, sess, cfg CostConfig, now)` and `CostThresholds(history, sess, cfg CostConfig)` take it. No hard-coded throttle.
3. **Exact threshold values (A02, C2-07).** `CostThresholds` returns its pairs as `pyfmt.Num` (exact int or float), compared with `pyfmt.NumCmp`. Orchestrator-measured on CPython 3.11.7: `9007199254740995 >= 9007199254740996.0` is False while the float64 conversion gives True; use this as the pinned example.
4. **Foreign-cache matrix (C2-01, C2-02, B03, B04).** Agent 2 builds the complete OD-160 matrix in error-taxonomy, replacing site-by-site discovery. Method, stated in the file: list every read of a cache-sourced value in `legacy/dgx_statusline.py` (session cache, mix cache, sparkline history, git cache, cost history), and for each read site and each fault class {string, null, list, dict, positive giant int, negative giant int} record legacy's outcome (raise with exception type, or a pinned non-raise result such as the positive-giant KV rendering `KV▰▰▰▰ 100%` from `min(int, 100.0)`; measured: `math.isnan(10**400)` raises OverflowError). Every raising cell is a CP-C row (CP-C33 onward, existing rows reused where they already match); non-raising cells are listed as pinned outcomes. The matrix is declared complete under its method. Owner BCs get ONE edge case each that cites their CP-C id range ("foreign cached values: CP-Cxx..yy, OD-160, Go table tests") instead of one edge case per cell; BC agents name the cached fields they read, and the residual sweep adds the id ranges. CP-C01's step attribution is corrected (session-cache non-object faults at step 3, SL:307/311, never at step 6), and BC-1.02.013 gains the non-object session-cache edge case.
5. **Label width reason (D01).** The display-width check covers the three `pill.label_*` keys AND the nine OD-194 `statusline.labels.*` keys; a value outside 1..16 columns gives the existing pill-label width reason string. BC-2.01.004 PC-6/PC-9, BC-5.03.001 Inv 1, BC-2.01.005 PC-6 and error-taxonomy say so.
6. **LF goldens on every OS (D05).** `-update` applies the BC-6.03.002 PC-1 CRLF→LF conversion to the oracle's stdout before writing any golden, so every committed golden is LF on every OS.
7. **D4-EX-3 self-consistency (D06).** The leg compares only cache members that legacy does not rewrite from the clock on every refresh; agent 8 enumerates the excluded members by legacy site (at least `rl_ts`, `fetch_ts`, `ts`) and states the compared remainder.
8. **Empty List value (D02).** A default-only List key with an empty value is the empty list and gives `out of range` (BC-2.01.005 PC-7); BC-2.01.001 PC-2's `expected non-empty control-free text` applies to Text keys only.
9. **int64 overflow reason (D03).** BC-2.02.001's reason-precedence order is canonical: int64 overflow is range rule 3, after rule 2 `negative`; BC-2.02.003 moves it out of the grammar checks.
10. **`~` without a home (D04).** With `HYLO_PATHS_CACHE_DIR=~/...` and home unset or relative, the stderr line is the path-grammar `home directory unknown` line; the general `cannot determine cache directory (HOME unset)` line applies only when no cache-dir key is set. BC-2.03.002 states both exact lines.
11. **Surrogate storage (D07).** A byte mapped to U+DC00+b is stored in the BC-5.02.004 WTF-8 form, and prefix matching runs over those WTF-8 bytes.
12. **Subagent dispatch (D09).** `run` routes `--subagent` to `runStatuslineSubagent(args, ...)` per ARCH-01; BC-4.01.001 PC-1 matches.
13. **Cost file I/O home (A2-03).** VP-018 and VP-020 place cost-history file I/O and temp-dir tests in `internal/statusline` (pass-13 call 7); VP-INDEX module columns follow.
14. **govulncheck in branch protection (A05).** The required-check list names `govulncheck (required)` only from the change that adds go.mod's `toolchain` line; until then the list says it reports but is not required.
15. **Censuses (A03, A04, A08).** Tier A census counts (case, step) comparisons; timing census counts (case, step) pairs; Tier B census on each leg counts golden comparisons made (variant or default fallback, each case once) and equals that leg's case count; govulncheck's positive coverage is the number of packages it analysed (from its JSON output), compared with `go list ./...`.
16. **NFR-002 families (A06).** NFR-002's target and the E-REN-002 derived carrier set include CP-O06..O09 (skip-render) and the CP-C register (degrade, OD-160 Go table tests) beside the X/S/T/N/O/A families.
17. **Everything else** as reported, routed below. Note on B02's ntpath doubt: orchestrator-measured `ntpath.normpath('//')` is two backslashes on CPython 3.11.7, as BC-1.02.022 states.

## Agent file sets and findings (routed by file)

| Agent | Role | Files | Findings |
|---|---|---|---|
| 1 | architect | specs/architecture/*, specs/cicd-setup.md | A01 + A02 (calls 2, 3; ARCH-03 cost API), A03, A04, A05, A08 (calls 14, 15), A10 (ARCH-01), A11, A12, A13; C2-06 (ARCH-03 cites); D05 (call 6, ARCH-07); D16 (ARCH-08 if stated) |
| 2 | product-owner | specs/prd.md, specs/prd-supplements/*, specs/owner-decisions-log-2026-11-14.md | A06 (call 16), A07, A09, A10 (interface-definitions), A14; B03 (taxonomy row), B08; C04 (taxonomy CP-C26); C2-01 + C2-02 (call 4, the matrix); D01 (call 5, taxonomy) |
| 3 | architect | VP-001..VP-020 | A2-01 (call 1, VP-012), A2-03 (call 13), A2-04, A2-05, A2-11; B01 (VP-012 `bcs:`), B02 (VP-001 source contract) |
| 4 | architect | VP-021..VP-041, VP-INDEX, domain-spec/*, product-brief, dtu, gene-transfusion, feasibility | A2-02 (VP-021: cold start grey below $1, yellow from $25, else white; `$/h` grey), A2-06, A2-07, A2-08, A2-09, A2-10; VP-INDEX sync (module columns per call 13; `bcs:` deltas) |
| 5 | product-owner | ss-01 BC-1.01.*, BC-1.02.* | B01 (BC rows), B02 (BC rows), B03, B04 (call 4), B05, B06, B07, B09 |
| 6 | product-owner | ss-01 BC-1.03.*, BC-1.06.*, BC-1.07.* | C01, C02, C03, C04, C05 |
| 7 | product-owner | ss-01 BC-1.04.*, BC-1.05.* | C2-01 + C2-02 (call 4: name the cached fields each BC reads; one OD-160 edge case per BC), C2-04, C2-05, C2-08, C2-09, C2-10 |
| 8 | product-owner | ss-02..ss-06 BCs, BC-INDEX, BC-ALLOCATION | D01..D16 (calls 5-12); A2-01 BC-6.03.004 register (call 1) |
