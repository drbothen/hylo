# Coverage audit (step B.5): hylo-legacy

- **Scope:** `legacy/` only: 11 files, 3,181 lines (`find legacy -type f -exec wc -l {} +`; recounted this audit, unchanged).
- **Artifacts audited:** all 44 files in `.factory/semport/hylo-legacy/`. Passes 0-5 are graded on **every** round of the pass (broad + deep + rN).
  Pass 6 synthesis and the extraction validation are graded in one informational column (`6+EV`). The canonical consolidations named in the brief
  (pass-0 r3 §2, pass-1 r3 §B, pass-2 r8 §7 + r9, pass-3 r4 §7 + r5-r8, pass-4 r7, pass-5 r3 + r4/r5) are among the files graded.
- **Method:** grep only, no judgment calls. Scripts and outputs are in the scratch directory
  `/private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/b5/`:
  `syms.py` (makes the Python symbol table with `ast`, output `py_syms.tsv`), `other_syms.tsv` (shell blocks and functions, plist keys and ROLLBACK
  sections, by hand from `cat -n`), `matrix.py` (makes the matrix, output **`coverage-matrix.tsv`**, the machine-readable appendix), and `linecov.py`
  (line-level citation coverage, output `line-coverage.tsv`).
- **Rules followed:** read-only on `legacy/` and on every existing artifact. Nothing ran from `legacy/`: the symbol table came from `ast.parse` of the
  file text under `python3 -I`, and nothing was imported or executed. No proxy, nothing networked. `CLAUDE.local.md` was not read. No commit.

## 1. Inventory (`ls -R legacy/`)

```
legacy/: auto_continue.py claude-dgx deploy/ dgx_ledger_exporter.py dgx_preflight.py dgx_proxy.py dgx_statusline.py
         dgx-proxy-coordinator.sh ROLLBACK.md tools/
legacy/deploy: io.hylo.ledger-exporter.plist io.hylo.ledger-tunnel.plist
legacy/tools:  backfill_cost_history.py
```

| File | LOC | Matrix rows | Row kinds |
|---|---:|---:|---|
| `dgx_statusline.py` | 1245 | 39 | 33 functions, 5 module-level statement blocks, `__main__` |
| `dgx_proxy.py` | 764 | 42 | 25 functions, 2 classes + 11 methods, 5 module blocks, `__main__` |
| `dgx_ledger_exporter.py` | 414 | 9 | 4 functions, `Handler` + 2 methods, 1 module block, `__main__` |
| `auto_continue.py` | 275 | 12 | 9 functions, 2 module blocks, `__main__` |
| `dgx_preflight.py` | 41 | 1 | one module-level script (no functions) |
| `tools/backfill_cost_history.py` | 121 | 5 | 3 functions, 1 module block, `__main__` |
| `claude-dgx` | 185 | 16 | 15 top-level blocks + `is_router` |
| `dgx-proxy-coordinator.sh` | 50 | 5 | 3 functions, 2 blocks |
| `deploy/io.hylo.ledger-exporter.plist` | 13 | 3 | key groups (Label+ProgramArguments, RunAtLoad+KeepAlive, log paths) |
| `deploy/io.hylo.ledger-tunnel.plist` | 18 | 3 | same key groups |
| `ROLLBACK.md` | 55 | 6 | sections (preamble + 5 `##` sections) |
| **Total** | **3181** | **141** | Row LOC sums to 3,362 because class rows overlap their method rows |

The full symbol list with line ranges is `py_syms.tsv` + `other_syms.tsv`, and also columns 1-6 of `coverage-matrix.tsv`.

## 2. Coverage matrix

### 2.1 Grading rule (applied mechanically by `matrix.py`)

For each row and each pass, three kinds of grep evidence are counted, one count per artifact line:

- **N:** lines matching the row's name pattern: the function, class or method name; for a module block, any constant it assigns; for a shell or plist
  row, its identifying variables or keys (the regex is in column `name_pattern`). For an **ambiguous** name (`main`, `request`, `error`, `ts`, `esc`,
  `emit`, `note`, `ledger`, `heat`, `visible`, `LEDGER`, `PORT`, and others, plus any name under 8 characters without `_`), the match must be
  backticked or followed by `(`, **and** the line's file context must be the row's file.
- **Q:** explicit file-qualified line citations (`dgx_statusline.py:440-637`, or the artifacts' aliases `SL: PX: EX: HK: LN: L: PF: BF: CO:`, including
  comma lists) whose range overlaps the row's range.
- **C:** bare `:N` citations, attributed to a file by context, whose range overlaps the row's range. The context is the last file alias or file name on
  the line, a `BC-SL/PX/EX/HK/LN/PF/BF/CO-NNN` id on the line, or the file named in the nearest enclosing heading (the artifacts' own notation rule).
  A citation of a non-legacy file (`m/proxy/server.py:123`, `*.go:N`) resets the context, so mitmproxy and Go line numbers are never counted.
- Citations that span more than 250 lines are ignored (a whole-file citation proves nothing about one symbol).
- **Cell:** `yes` if (N≥1 and Q+C≥1) or N≥3 or Q+C≥2; `partial` if there is any evidence; `no` if there is none.
- **P3-BC:** pass-3 lines that contain `BC-` and also N, Q or C evidence for the row. This is the per-symbol "BC citation" count for test 3b.

The appendix columns per pass are `pN, pN_N, pN_Q, pN_C`, then `p3_BC_lines`, `name_pattern`, and the grep command per row.

### 2.2 Totals (yes / partial / no)

| Row set | Rows | Pass 0 | Pass 1 | Pass 2 | Pass 3 | Pass 4 | Pass 5 | 6+EV (info) |
|---|---:|---|---|---|---|---|---|---|
| **All rows** | 141 | 101 / 36 / 4 | 87 / 22 / 32 | 114 / 18 / 9 | **129 / 5 / 7** | 97 / 18 / 26 | 118 / 10 / 13 | 32 / 37 / 72 |
| **In scope** | 102 | 70 / 29 / 3 | 64 / 18 / 20 | 95 / 5 / 2 | **100 / 1 / 1** | 76 / 13 / 13 | 94 / 6 / 2 | 30 / 29 / 43 |
| Out of scope | 39 | 31 / 7 / 1 | 23 / 4 / 12 | 19 / 13 / 7 | 29 / 4 / 6 | 21 / 5 / 13 | 24 / 4 / 11 | 2 / 8 / 29 |

### 2.3 Per file (all rows; yes/partial/no)

| File | Rows | P0 | P1 | P2 | P3 | P4 | P5 |
|---|---:|---|---|---|---|---|---|
| `dgx_statusline.py` | 39 | 21/16/2 | 16/6/17 | 34/5/0 | **39/0/0** | 27/6/6 | 35/1/3 |
| `dgx_proxy.py` | 42 | 33/9/0 | 33/8/1 | 32/9/1 | **42/0/0** | 31/5/6 | 37/5/0 |
| `dgx_ledger_exporter.py` | 9 | 7/2/0 | 7/1/1 | 9/0/0 | **9/0/0** | 6/1/2 | 8/1/0 |
| `auto_continue.py` | 12 | 8/3/1 | 7/2/3 | 9/2/1 | **12/0/0** | 12/0/0 | 11/1/0 |
| `dgx_preflight.py` | 1 | 1/0/0 | 1/0/0 | 1/0/0 | **1/0/0** | 1/0/0 | 1/0/0 |
| `tools/backfill_cost_history.py` | 5 | 3/2/0 | 1/1/3 | 4/0/1 | **4/0/1** | 3/1/1 | 5/0/0 |
| `claude-dgx` | 16 | 16/0/0 | 15/1/0 | 16/0/0 | **15/1/0** | 11/4/1 | 16/0/0 |
| `dgx-proxy-coordinator.sh` (OOS) | 5 | 5/0/0 | 4/1/0 | 5/0/0 | 2/3/0 | 3/0/2 | 5/0/0 |
| `deploy/*.plist` (OOS) | 6 | 4/2/0 | 3/2/1 | 4/2/0 | 5/1/0 | 3/1/2 | 0/2/4 |
| `ROLLBACK.md` (OOS) | 6 | 3/2/1 | 0/0/6 | 0/0/6 | 0/0/6 | 0/0/6 | 0/0/6 |

### 2.4 Line-level cross-check (pass 3, `line-coverage.tsv`)

This check catches drift inside large functions, which a symbol-level hit could hide. It takes the union of every file-attributed pass-3 citation
(Q + C, span ≤ 250) against the non-blank, non-comment lines:

| File | Code lines | Cited by pass 3 | Uncited runs of ≥ 8 code lines |
|---|---:|---:|---|
| `dgx_statusline.py` | 910 | 910 (100%) | none |
| `dgx_proxy.py` | 618 | 618 (100%) | none |
| `dgx_ledger_exporter.py` | 367 | 367 (100%) | none |
| `auto_continue.py` | 232 | 232 (100%) | none |
| `claude-dgx` | 109 | 109 (100%) | none |
| `dgx-proxy-coordinator.sh` | 38 | 31 (81%) | none |
| `tools/backfill_cost_history.py` | 106 | 82 (77%) | `2-26`: module docstring + imports (read: `cat -n`, lines 1-27) |
| `dgx_preflight.py` | 36 | 23 (63%) | `2-16`: module docstring + imports (read: `cat -n`, lines 1-16) |

The only pass-3 uncited runs are docstrings and `import` lines, which carry no behavior. The backfill constants (`PRICES`, `MIN_USD`,
`MIN_BACKFILL_API_MS`, `:30-35`) are cited by name in pass-3 broad-deep and r3. Line coverage for the other passes is in `line-coverage.tsv`: pass 2
covers 62-100% per file, pass 5 covers 81-91% for the six main programs, and passes 1 and 4 are lower as their topics predict.

## 3. Gap tests

### 3.1 Test A: file or cluster > 100 LOC with no entity or BC documentation

The files over 100 LOC are `dgx_statusline.py`, `dgx_proxy.py`, `dgx_ledger_exporter.py`, `auto_continue.py`, `claude-dgx` and
`tools/backfill_cost_history.py`. Each has both entity documentation (pass-2 cells `yes` for 75-100% of its rows, no in-scope `no` cell except `auto_continue.py:184` and backfill `__main__`) and its own BC series. Grep counts of
distinct BC ids (`grep -oE 'BC-<P>-[0-9]+' | sort -u | wc -l`):

| Prefix | File | Distinct ids, all pass-3 rounds | In pass-3 r4 §7 index | Cited in pass 2 |
|---|---|---:|---:|---:|
| BC-SL | `dgx_statusline.py` | 103 | 103 | 7 |
| BC-PX | `dgx_proxy.py` | 49 | 45 | 13 |
| BC-EX | `dgx_ledger_exporter.py` | 27 | 26 | 8 |
| BC-HK | `auto_continue.py` | 23 | 23 | 3 |
| BC-BF | `tools/backfill_cost_history.py` | 13 | 13 | 1 |
| BC-LN | `claude-dgx` | 11 | 11 | 3 |
| BC-PF | `dgx_preflight.py` (41 LOC) | 2 | 2 | 0 |
| BC-CO | coordinator (OOS) | 2 | 2 | 0 |
| BC-SV | plists (OOS) | 2 | 2 | 1 |

The four BC-PX ids beyond r4 (`BC-PX-046..049`) come from the r5-r8 amendments. No cluster inside a file has more than 100 LOC without coverage:
the largest clusters (`render_lane` 198, `_mix_counts` 156, `rebuild` 173, `Handler.do_GET` 135, `render_telemetry_fields` 111, `DGXRouter.response`
100) have P3-BC = 58, 28, 17, 12, 14 and 16. **Test A finds no gap.**

### 3.2 Test B: symbol > 20 LOC with zero pass-3 BC citations

There are 42 rows over 20 LOC. All in-scope rows have P3-BC ≥ 1. The weakest are `claude-dgx` ARGS block `:117-139` (P3-BC 1, which is
BC-LN-007, confirmed by grep `DGX_MAIN_MODEL|DGX_REMOTE|LANGUAGE RULE|dangerously-skip`) and `<module 951-974>` (1). The only row with P3-BC = 0 is
`ROLLBACK.md ## Rollback the laptop side` (22 lines), which is out of scope as documentation. **Test B finds no gap.**

### 3.3 Residual weak cells (in scope; not gaps under either test)

- **Pass 3:** `tools/backfill_cost_history.py __main__` `:120-121` is `no` (two lines, `if __name__ == "__main__": main()`; `main` itself has
  P3-BC 8). `claude-dgx` header `:1-7` (`set -u`, `HERE=${0:A:h}`) is `partial`: P3-BC 0, but pass 0, 1, 2 and 5 are `yes`, and `set -u`/`HERE` are
  catalogued in pass 5.
- **Pass 2:** `auto_continue.py` `CJK` `:184` (1 line; pass 3, 4 and 5 are `yes`) and backfill `__main__`.
- **Passes 1 and 4:** 20 and 13 in-scope `no` cells, all on small helpers (`truecolor`, `heat`, `_norm_pt`, `_iso_ts`, `esc`, `_current_size`) or on
  logic without architecture-level or numeric content (`normalize_for_dgx`, `extract_stop_reason`, `uses_server_tool` have no pass-4 hit). The step
  defines a gap by entity/BC documentation, not by every pass, so these are recorded and not counted.
- **6+EV column:** pass 6 and the extraction validation are summaries by design (43 in-scope `no`), so this column is informational only.

## 4. Gap list

**None.** No in-scope file, cluster or symbol fails test A or test B, so no BC-AUDIT contracts, entity catalogue, integration points or pattern
notes are produced (step 4 of the method applies only to gaps).

## 5. Known out of scope (listed, not counted)

| Item | Rows / location | Matrix evidence (for the record) |
|---|---|---|
| Trust CLI body (BC-PX-031) | `dgx_proxy.py:560-764` (13 rows: constants, `_login_keychain` … `_build_parser`, `__main__`) + `claude-dgx:8-14` | P3 `yes` on all 13 Python rows (P3-BC 3-4 each) |
| D6 visible-mode launcher branches | `claude-dgx:15-22` (router port 4141-4199), `:85-96` (`is_router` + `opus_router.py` start) | P0-P5 `yes`/`partial` |
| Unwired coordinator | `dgx-proxy-coordinator.sh:1-50` (5 rows) | P3: 2 `yes`, 3 `partial` (BC-CO-001/002) |
| `--subagent` status line mode (OD-14 pending) | `dgx_statusline.py:845-936` (`_SUB_GLYPH`, `_fmt_lines`, `_fmt_tok_c`, `_fmt_tokens`, `render_subagent_rows`, `main_subagent`) | P3 `yes` on all 6 |
| Plists as deploy artifacts | `deploy/io.hylo.ledger-exporter.plist`, `deploy/io.hylo.ledger-tunnel.plist` (6 rows) | P3: 5 `yes`, 1 `partial` (BC-SV-001/002) |
| ROLLBACK.md as documentation | 6 sections | P0: 3 `yes`, 2 `partial`, 1 `no`; P1-P5 `no` |
| CP-C01..C10 (foreign-cache crash paths) | owner ruling: out of parity scope; the Go writer writes legacy's exact cache format | not a matrix row (they are crash paths inside covered symbols) |

Note: `_fmt_lines` and `_fmt_tok_c` are also called by row-1 `render_lane` (pass-3 r6 §A1 lists them as row-1 widget renderers). Their rows are
graded `yes` in pass 3 either way, so the OOS tag does not hide anything.

## 6. Limits of this audit (what was not verified)

- The grading is grep evidence that a symbol or range is **cited**. It does not check that the cited contract is **correct**; that is step B.6
  (extraction validation) and the rounds' own pinning.
- The bare `:N` attribution uses context (line, BC id, enclosing heading). Spot checks found it under-attributes rather than over-attributes: before
  heading inheritance was added, `main :1200-1235` showed P3-BC 0, although BC-SL-002 cites `:1201-1206`. A residual false-positive risk remains
  where a bare citation follows a legacy file name in the same line but refers to another file. The matrix rows that carry the result (> 20 LOC,
  P3-BC ≥ 1) were confirmed by direct grep for the largest clusters, the launcher ARGS block (BC-LN-007), `dgx_preflight.py` (BC-PF-001
  `dgx_preflight.py:18-24`) and the backfill constants.
- Shell, plist and ROLLBACK rows were segmented by hand from `cat -n`. Python rows come from `ast`. Docstrings count as "code lines" in §2.4, so
  that table understates coverage slightly.

## State checkpoint

```yaml
pass: B.5
status: complete
files_scanned: 11
rows: 141 (102 in scope, 39 out of scope)
gaps: 0
timestamp: 2026-11-14
next_pass: B.6 re-check / Step C final synthesis
appendix: /private/tmp/claude-501/-Users-user-Dev-hylo/<uuid>/scratchpad/b5/coverage-matrix.tsv
```

Result: PASS
