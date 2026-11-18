---
document_type: architecture-section
level: L3
section: "parity-harness"
version: "1.4"
status: draft
producer: architect
timestamp: 2026-11-18T07:00:00Z
phase: 1b
inputs: [prd.md, semport/hylo-legacy/statusline-target-design.md, behavioral-contracts/BC-INDEX.md]
traces_to: ARCH-INDEX.md
input-hash: "089b35b"
---

# ARCH-07 — Parity harness (`internal/parity`)

> Referees D4: runner, fixture corpus, comparison, exclusion machinery, CI legs.
> Classification: **infrastructure** (spawns interpreters and builds; test-only; never
> imported by the render path). HIGH tier (>= 90%). The referee must be stronger than
> the refereed — weak machinery fake-passes parity (module-criticality).

### Decision: three-tier harness with a closed named exclusion list (AD-09)

- **Context:** P1's exit criterion is 0 unexplained diffs vs the CPython 3.11.x oracle
  (OD-104) over the synthetic corpus plus the owner's recorded inputs replayed from
  git-ignored `captures/` (OD-107); ruled differences exist and must be bounded.
- **Options considered:** (1) ad hoc diff scripts per phase; (2) one harness package,
  three tiers, exclusion machinery that fails closed.
- **Option 2.** Tiers per design doc §5.1: **A** live differential (oracle runs
  `legacy/` under the clock shim; Go in-process and as the built binary for a subset;
  per-step stdout bytes + exit code + named caches byte-for-byte by file name across the
  two directories); **B** committed goldens (written by **Python** under the pinned
  oracle, never Go; `*.golden` on the Linux oracle run, `*.windows.golden` on the
  **Windows** oracle run — BC-6.03.001, ADV-P2-A09; Go must match on every OS);
 Tier C differential fuzz, nightly on all three OSes (OD-149; design doc had Linux), non-gating, random valid inputs to both sides.
- **Rationale:** Tier A proves parity on live runs (the D4 exit criterion); Tier B makes
  parity executable without Python on every CI leg and PR; Tier C hunts P27-class hidden
  exception paths the 43-path catalogue may have missed (RK-2).
- **Consequences:** the exclusion list is JSON (zero-dependency budget), one entry per
  excluded case `{id, case, expected_output_file, table_test}`; harness FAILs with a
  named reason on: an excluded case without a matching table test, an excluded case whose
  Go output differs from its own expected file, a glob ("no blanket exclusions"), or an
  id outside the closed set — TEN ids: {D4-EX-1, D4-EX-2, D4-EX-3, OD-30, OD-76,
  temp-file, cp-x03, OD-159, OD-160, OD-161} (spelling exactly per BC-6.03.004;
  ADV-P1-A05; OD-159 = Go reads files as UTF-8 on all OSes, OD-160 = foreign-cache
  shapes ruling Q-b, OD-161 = integer `transcript_path` → no transcript, never touch
  foreign descriptors).
  stderr is never compared (Python tracebacks invisible to Claude Code).
- **Verification feasibility:** comparison and exclusion machinery are
  **provably-closable**: a closure property test proves every exclusion id ∈ closed set,
  every entry has its table test, and corpus case-ids are unique (E-HAR-001 dispositions
  are themselves table-tested); the runner is testable-only.

## Oracle execution (BC-6.01.001..003)

- Explicit absolute CPython 3.11.x interpreter path, never PATH discovery (OD-104);
  invoked with `-s`, never `-I`/`-E` — `-I` would drop the sitecustomize clock shim
  (OD-109). Child environment constructed from scratch: no `*_proxy`, fixed
  HOME/USERPROFILE, TMPDIR, `LANG=en_US.UTF-8`, no inherited GP-1..GP-6 variables.
- Clock shim `internal/statusline/testdata/pyhooks/sitecustomize.py` on `PYTHONPATH`
  freezes `time.time`/`strftime`/`localtime`/`gmtime` from `HYLO_TEST_NOW` (decimal
  string parsed by both sides), stepped between refreshes; canary test fails the harness
  if the shim did not load (BC-6.01.003). Depth boundaries are call-context dependent
  (ADV-P1-B17): the stdio shim and runner frames change the Python-frame depth at
  `json.load`, so the oracle is always invoked with the exact recorded recipe for the
  site being measured — the END-TO-END program invocation (piped stdin through
  `main()`; the transcript parse in program context), which measured 993 accepted /
  994 rejected for BOTH the stdin and transcript sites (orchestrator re-measurement,
  2026-11-17; the earlier frame-local 989 probe does not transfer). The same burst
  measured the cache loaders under the END-TO-END recipe with isolated HOME, closing
  ADV-P2-A07: session cache (main → effective_rl → load_cache, 8 frames) 991 accepted /
  992 rejected; git cache (main → render_lane → git_segment → load_cache, 9 frames)
  990/991; peers at equal chain depth derived — get_sample, claude_window_start and the
  mix cache (8 frames) 991/992; cost-history record_cost/cost_thresholds (9 frames)
  990/991. Governing formula: limit = 999 − Python frames from `<module>` down to json's
  raw_decode (full table and per-site recipes: VP-006). A boundary measured
  under a different invocation does not transfer.
- Metrics directed to an httptest fake via the typed settings translation (legacy gets
  `DGX_SL_*` + `LOCAL_MODEL_PREFIXES`; Go gets the `HYLO_*` equivalents per OD-05;
  outside-domain values legal only in D4-EX-3 cases).

## OD-145 provisional names, flags, test names, seed paths (decided here; adversarial review may adjust)

| Item | Provisional name |
|---|---|
| Runner package | `internal/parity` |
| Interpreter setting | `HYLO_PARITY_PYTHON` (settled, OD-104/OD-108) |
| Golden update flag | `-update` (`go test ./internal/parity -run TestParityTierB -update`); writes Python output; fails if interpreter unset |
| Tier A test | `TestParityTierA_Corpus` |
| Tier B test | `TestParityTierB_Goldens` |
| Tier C test | `TestParityTierC_DiffFuzz`, budget env `HYLO_PARITY_FUZZSECONDS` (0 = skip; nightly sets 1800 = 30 min per OS, OD-149) |
| Canary | `TestParityCanary_ShimLoaded` |
| Exclusion machinery | `TestParityExclusions_ClosedSet` |
| Cache swap | `TestParityCacheSwap_FourCaches` |
| Corpus hygiene | `TestCorpusHygiene` (settled, NFR-006) |
| Case dirs | `internal/statusline/testdata/parity/cases/<case-id>/` |
| case-id grammar | `<family>-<nnn>[-<variant>]`, families: frame, row1, transcript, row2, cost, cache, platform, cfgerr, swap, subagent, cps01..cps17, cpt01..cpt07, cpn01, cpn02, cpo01..cpo11, cpa01..cpa05 |
| Case contents | `stdin.json.tmpl`, `settings`, `argv` (one JSON array of string arguments passed to the built `hylo` binary verbatim; default `["statusline"]`; subagent-family rows carry the flag arrangements under test, e.g. `["statusline", "--", "--subagent"]` — pass-3 A03, OD-155/OD-168: the harness invokes the built binary with the case argv, superseding the earlier "invokes `hylo statusline` without flags" wording), `metrics.json` or mode (down/500/garbage), optional `seed/` cache seeds, `steps.jsonl` (clock step + transcript appends per step) |
| Exclusions file | `internal/statusline/testdata/parity/exclusions.json` |
| Tier B goldens | `internal/statusline/testdata/goldens/*.golden`, `*.windows.golden` |
| Clock shim | `internal/statusline/testdata/pyhooks/sitecustomize.py` |
| pyfmt generators/tables | `internal/pyfmt/testdata/gen/*.py`; tables `internal/pyfmt/testdata/*.golden` |
| Replay captures (git-ignored) | `captures/` (repo root) |
| D4-EX-3 class tests | `TestConfigError_D4EX3_{Number,NumberGrammar,Boolean,URL,Enum,Theme}` — six names, six classes (pass-2 follow-up, syncing ARCH-07 to VP-016's A2-07 number-grammar table): `Number` covers number-range (BC-2.02.002), `NumberGrammar` covers number-grammar (BC-2.02.003); the other four names map one-to-one |
| D4-EX-1 test | `TestWindowAge_D4EX1_Windows` |
| Seeds reference | `seed/` holds the four cache files under their legacy file-name formats (legacy-shared named constants, BC-1.06.001; not renamed by the harness) |

Fixture co-location ADR (AD-13): fixtures live under `internal/statusline/testdata/`
(goldens pin statusline bytes) while the runner is `internal/parity`; Go testdata is
opaque, so the cross-package read is deliberate — one fixture home, no duplicate corpus.

## Mapping

BC-6.01.x -> oracle execution; BC-6.02.x -> case model/corpus/swap; BC-6.03.x ->
comparison + exclusions; BC-6.04.x -> CI legs, timing report, nightly Tier C
(workflow design in ARCH-08).
