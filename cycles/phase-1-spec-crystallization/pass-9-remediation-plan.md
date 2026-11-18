---
document_type: remediation-plan
phase: 1d
pass: 9
date: 2026-11-18
source: adversarial-reviews/pass-9.md, adversarial-reviews/ADV-P9-INDEX.md
---

# Pass-9 remediation plan (canonical calls)

Read with the Rules section of `pass-4-remediation-plan.md` and the header rules of passes 6-8 (OD-176 fix everything; check calls against settled ODs; one measurement per fact; Python `/opt/homebrew/anaconda3/bin/python3 -I` only; verify fixes AND rejections on disk; OD-182 sketches are non-normative; edit only your file set and list out-of-set hits; re-check meaning at every use when renaming; check citations resolve).

**New gates for this burst (pass-9 lessons):**
- **YAML:** every file you change must still have frontmatter that parses with `yaml.safe_load` (run `/opt/homebrew/anaconda3/bin/python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]).read().split('---')[1])" <file>` after your last edit). Prefer block-style `modified:` lists; never leave an unbalanced quote.
- **For-all properties:** a "for all inputs" property is derived from the owning BC's exact postconditions (every PC, EC and exception, including skips, degrades, drops and offset/size adjustments) and walked against legacy's code paths before you write it. If any legal input breaks it, narrow the domain explicitly.
- **Measurements:** state only what you measured; never generalize one case to a class (pass-8 measured status 100 and wrote "any 1xx"). Depth and recursion facts are measured only through the real entry point (`python3 -I -s legacy/dgx_statusline.py`, isolated HOME and cwd).
- **Wire goldens:** a table that says it holds wire bytes contains only ASCII (`\u001b`, `✔`, `·`, ...); a display-form table says so; one notation per table.
- **Anchors into ARCH docs:** cite section anchors, never line numbers (pass-5 call 19).

No owner rulings this pass. Next free OD: OD-194.

## Orchestrator calls (binding; checked against the OD log)

1. **Mix-cache save/load asymmetry (A02, D03, D04; orchestrator-measured):** legacy saves the mix cache at document depth up to 994 (995 skipped) but loads it only up to 991. Measured: a transcript line at decode depth 993 with a deep `message.id` saves a mix cache of document depth 993; on the next refresh the load fails, legacy treats the cache as absent, re-reads the transcript from offset 0 and rewrites the cache — every refresh while that line remains (file rewritten, same size, no temp leak, exit 0). hylo reproduces this. Remove every "Save budget EQUALS Load budget" / "`Decode(Save(x))` never rejects" claim for the mix cache (session, git and cost-history keep equality); state the depth unit once (total nesting of the saved document, top-level object = 1); state the mix site as the measured exception to the `995 − s` law; pin the re-read loop in the owning transcript/cache BC.
2. **Row-2 rule (A2-01, A2-09, B01, B02):** legacy SL:1217 and SL:1224: row 2 is rendered iff `rows ≥ 2` and (`rows > 2` or `cols == 0` or `cols ≥ narrow_cols`). State exactly this in BC-1.01.007 (PCs, Inv 1, VP row, anchors), BC-1.01.003 if it restates it, VP-040 P7 (statement and generator domain) and VP-027.
3. **For-all legs corrected (A2-02, A2-03, A2-04, A2-06, A2-12, B06):** W-line quick leg: state after equals state before except as BC-1.03.018 PC2 says (offset advances; CP-O06..O08 drop `cur` to null). Delete-the-line oracle adjusted for PC4(a) (`size` = legacy's + deleted bytes and terminators) and PC4(b). History for-all: pruning (length ≤ `statusline.sparkline.history_cap`, age < `statusline.sparkline.max_age_s` — use the registered key names) holds on the success path only; the failure path re-saves the stored history verbatim (SL:327, SL:353-355). Subagent parse oracle: undecodable or non-object stdin → exactly zero stdout bytes. VP-004's MAIN fuzz generator excludes `--subagent`. BC-1.02.015 / VP-041 P-t restricted to finite `dur` in non-degrading renders.
4. **New crash id CP-O12 (B03; orchestrator-verified):** "cost-pick equivalence overflow: `tin` and `tout` each below the int→float overflow bound but their exact-int sum `tot` (SL:626) at or above it enters `tot * dgx_mtok` (SL:633) on the local lane with a valid basis → OverflowError → degraded line" (Surface 1, render-time degrade, like CP-O04). Append-only; the register becomes 49 paths (X4 S17 T8 N3 O12 A5). Owner BC-1.02.029 (EC + canonical vector), co-owner BC-1.05.003 if it owns the `⛏` value. Update every register count and family list (error-taxonomy, prd NFR-002 and E-REN-002, nfr-catalog, ARCH-03, VP-001, VP-011, gene-transfusion, BC-1.01.001/BC-1.01.009 lists). Also fix BC-1.03.018 Inv 3 (C03): transcript-borne exact-int totals that are counted (not skipped) can still degrade later at render (CP-O04, CP-O09, now CP-O12); BC-1.03.006 cross-references this.
5. **YAML repair (C02 + six more):** the frontmatter of these files does not parse and must: BC-1.07.002, BC-1.07.003, BC-1.07.006, BC-1.07.007, BC-1.07.008, dtu-assessment.md, VP-001, VP-011, VP-012, VP-030, VP-031. Each owning agent repairs its files without losing any history entry.
6. **Wire notation (C01, C06):** BC-1.07.007's canonical rows are wire form, pure ASCII (`\u001b`, `✔`, `·`), derived from the oracle; BC-1.07.004's string-token example uses a raw token that differs from its output (e.g. stdin token `"A"` → `"A"`), oracle-checked.
7. **OD-76 and D4-EX-1 closure (D01, D02):** no OD-76 or D4-EX-1 corpus case exists (corpus is UTC-only and every case seeds `proc_start`), so `exclusions.json` carries no entry for either id; each is closed by its rider test alone (pass-7 call 10: closure verifies a rider test for every closed id, including ids without parity entries). Fix BC-3.02.002 (Inv 2, VP row, rows I1-I6 → Go table tests), BC-3.02.001 Inv 4 (no unseeded corpus cases; the probe is exercised by table tests with a fake process table), BC-6.03.004 EC-006 (replace the OD-76 corpus example with a valid one), BC-6.02.003.
8. **Capture seeding (D12):** capture replays follow BC-6.02.003 PC-6's seeding rule exactly as corpus cases do (a fixed synthetic `proc_start` in the fresh cache dir); a replay never consults the machine's real process tree. BC-6.02.002 states this.
9. **Percentiles (D05):** BC-2.01.004 and BC-2.02.001 follow error-taxonomy: one composite key, intra-key ascending check, the error line names `statusline.cost.percentiles` with its full JSON value.
10. **Metrics client (C2-01, C2-02, C2-07):** agent 7 measures each once on CPython 3.11.7 against a local raw-socket server: only status 100 is skipped (`if status != CONTINUE`, orchestrator-verified in source); a 101/102/103 response is final → no sample; `urlsplit` sanitization before the scheme guard and quoting (orchestrator-verified: `/a<TAB>b` → `/ab`, `HTTP://` → scheme `http`, leading C0/space stripped); the `Host` header bytes (netloc as written, unquoted, port only when present). Pin results in BC-1.04.001 and ARCH-03.
11. **Cost record order (C2-03):** the OD-166 convertibility skip happens at the write step, after the history load and the `s.get(sid)` lookup, so legacy's earlier raise sites (CP-S15 at SL:230) still fire. OD-166's scope is unchanged.
12. **Git pointer file (B04, B05):** agent 5 measures once: `readline()` decodes the buffered chunk (state the measured size), so an invalid byte after the first line still fails the read; `os.path.isdir`/`isfile` swallow OSError/ValueError (stat errors never stop the walk; it continues upward); only `open`/read failures reach the SL:394 handler.
13. **Interfaces and CI (perimeter A):**
    - A01: interface-definitions gains the subagent stdin payload and the NDJSON stdout schema (zero-byte cases included), copied from BC-1.07.001/BC-1.07.004.
    - A03: path resolution lives in `internal/platform`: `platform.Abs(cwd, p string)` as BC-1.02.004 calls it (state its result type once); ARCH-05 adds the row; ARCH-03 removes the Win32 resolution from statusline's Env.
    - A04: the coverage job runs on every PR; it checks each gated package that exists (fails if one exists and reports `[no statements]` or < 95%), and prints `coverage: G of 3 gated packages present`. It is never gated on `internal/parity` existing.
    - A05: gitleaks gains a positive-coverage line (`gitleaks: N commits scanned`, fail if N == 0).
    - A06: the `toolchain` line in go.mod must land before govulncheck becomes a required check (ordering stated in ARCH-08; go.mod changes only when the owner asks).
    - A07: Tier A runs every case in-process and a subset as the built binary (ARCH-07). The coverage job excludes Tier A because Tier A needs the Python oracle, which the coverage job does not install; fix ARCH-08 and cicd-setup's rationale.
    - A11: `statusline.paths.cache_dir` (HYLO_PATHS_CACHE_DIR) must be absolute; a relative value is a config error with the path-grammar reason family of BC-2.02.006 (state the exact string).
    - A12: `EnvVars` has one home, `internal/platform` (`platform.EnvVars`); cmd/hylo and statusline use it.
14. **Configuration rules (perimeter D):**
    - D06: per-key errors for `backends[i]` fields sort after all registry keys, by index then field name; `[from <ENVNAME>]` names the variable that carried the rejected value.
    - D07: default-only Text/List keys run the Text-class checks first (empty, control character), then the default comparison (number-range class `out of range`).
    - D08: a Text, glyph, label or separator value that is not valid UTF-8 (on Windows: a WTF-8 value with a lone surrogate) is a Text-class error with a new exact reason string minted in BC-2.02.001 (`invalid UTF-8`), mirrored byte-for-byte in error-taxonomy.
    - D09: the Windows naive-time domain starts at 1970-01-02T00:00 local wall time (the `u1 − 86400` probe), matching BC-5.04.001's own lines 92-94.
    - D10: the Windows oracle env differs from POSIX by `PYTHONIOENCODING` plus `TMP`, `TEMP`, `SYSTEMROOT`; the table test asserts the exact per-OS sets.
    - D11: the stdio canary gets a negative control per leg that proves it can fail, or the claim is narrowed to what it can detect.
    - D16: state only the measurable consequence of the real-clock conversion (differs only for |ns| ≥ 2^62); do not describe CPython's C algorithm unless verified from source.
15. **Small fixes:** everything else in pass-9 is fixed as reported (C04 Inv 1 restricted to W-line-free transcripts; C05 `enabled=false` is not a DI-012 deviation; C07..C11; D13..D20; A08..A10, A13..A17; A2-05, A2-07, A2-08, A2-10, A2-11, A2-13..A2-20; C2-04 VP-012 row + `bcs:`; C2-05; C2-06 section anchors; C2-08..C2-10).

## Agent file sets (disjoint)

| Agent | Role | Files | Findings |
|---|---|---|---|
| 1 | architect | specs/architecture/*, specs/cicd-setup.md | A02, A03, A04, A05, A06, A07, A12, A13, A16, A17; call 1 ARCH side; call 4 ARCH-03 register; call 10 ARCH-03 side |
| 2 | product-owner | specs/prd.md, specs/prd-supplements/* | A01, A08, A09, A10, A11 (registry row), A14, A15; call 4 taxonomy/NFR/E-REN; C2-10; D08 taxonomy mirror; D05 taxonomy check |
| 3 | architect | VP-001..VP-020 | A2-02, A2-03 (VP-013), A2-06, A2-07, A2-08, A2-10, A2-11, A2-12, A2-20 (VP-004/016/017); call 4 VP-001/VP-011; call 5 YAML VP-001/011/012; C2-04 (VP-012 `bcs:`) |
| 4 | architect | VP-021..VP-041, VP-INDEX, domain-spec/*, product-brief.md, dtu-assessment.md, gene-transfusion-assessment.md, architecture-feasibility-report.md | A2-01, A2-02/03 (VP-029), A2-04, A2-05, A2-09, A2-13..A2-19, A2-20 (VP-037); B01 (VP-040), B06 (VP-041); call 4 gene-transfusion; call 5 YAML dtu/VP-030/VP-031; VP-INDEX sync for agent 3's `bcs:` deltas |
| 5 | product-owner | ss-01 BC-1.01.*, BC-1.02.* | B02, B03 (CP-O12 owner), B04, B05 (measure), B06 (BC side), B07; call 2 BC side; call 4 BC-1.01.001/009 lists |
| 6 | product-owner | ss-01 BC-1.03.*, BC-1.06.*, BC-1.07.* | C01, C02 (YAML), C03, C04, C05, C06, C07..C11; call 1 transcript/cache BC side |
| 7 | product-owner | ss-01 BC-1.04.*, BC-1.05.* | C2-01, C2-02, C2-03, C2-05, C2-06, C2-07, C2-08, C2-09; C2-04 (BC side); call 4 BC-1.05.003 co-owner |
| 8 | product-owner | ss-02..ss-06 BCs, BC-INDEX.md, BC-ALLOCATION.md | D01..D20; A11 (BC side), A12 (BC side) |
