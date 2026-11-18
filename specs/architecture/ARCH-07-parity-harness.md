---
document_type: architecture-section
level: L3
section: "parity-harness"
version: "1.11"
status: draft
producer: architect
timestamp: 2026-11-19T20:00:00Z
phase: 1b
inputs: [prd.md, semport/hylo-legacy/statusline-target-design.md, behavioral-contracts/BC-INDEX.md]
traces_to: ARCH-INDEX.md
input-hash: "431bb1a"

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
 **C** differential fuzz, nightly on all three OSes (OD-149; design doc had Linux), non-gating, random valid inputs to both sides.
- **Rationale:** Tier A proves parity on live runs (the D4 exit criterion); Tier B makes
  parity executable without Python on every CI leg and PR; Tier C hunts P27-class hidden
  exception paths the catalogued crash-path register (error-taxonomy.md; CP-X/S/T/N/O/A
  families) may have missed (RK-2).
- **Consequences:** the exclusion list is JSON (zero-dependency budget), one entry per
  excluded case `{id, case, expected_output_file, table_test}`; harness FAILs with a
  named reason on: an excluded case without a matching table test, an excluded case whose
  Go output differs from its own expected file, a glob ("no blanket exclusions"), or an
  id outside the closed set — TWELVE ids: {D4-EX-1, D4-EX-2, D4-EX-3, OD-30, OD-76,
  temp-file, cp-x03, OD-159, OD-160, OD-161, OD-166, OD-181} (spelling exactly per BC-6.03.004;
  ADV-P1-A05; OD-159 = Go reads files as UTF-8 on all OSes, OD-160 = foreign-cache
  shapes ruling Q-b, OD-161 = integer `transcript_path` → no transcript, never touch
  foreign descriptors, OD-166 = cost-history bytes written after a refresh whose `usd`
  or `api_ms` could not convert to float — nothing else; OD-169; OD-181 = metrics
  transport beyond plain http — non-http(s) redirect targets and TLS trust-store
  differences for https; parity cases use plain http only, pass-6 OD-181).
  stderr is never compared (Python tracebacks invisible to Claude Code).
- **Verification feasibility:** comparison and exclusion machinery are
  **provably-closable**: a closure property test proves every exclusion id ∈ closed set,
  every entry has its table test, and corpus case-ids are unique (E-HAR-001 dispositions
  are themselves table-tested); the runner is testable-only.

## Oracle execution (BC-6.01.001..003)

- Explicit absolute CPython 3.11.x interpreter path, never PATH discovery (OD-104);
  oracle SELF-CHECK at harness start (OD-185, pass-6 A02: CI resolves the latest 3.11
  patch while the measured constants were taken on 3.11.7): the harness measures the
  JSON depth boundaries and `unicodedata.unidata_version` against the RESOLVED oracle
  and FAILS CLOSED on any mismatch, printing the resolved version; Tier B golden
  metadata records the resolved patch (RK-4). Pinned constants, copied verbatim from
  BC-6.01.001 PC-4 (pass-7 D04, the ONE end-to-end definition; CPython 3.11.7, default
  recursion limit 1000): stdin decode 993 accepted / 994 rejected; session-cache save
  991 writes / 992 skips; subagent wire 991 renders; `unicodedata.unidata_version`
  `14.0.0` — identical to the laws' constants.
  invoked with `-s`, never `-I`/`-E` — `-I` would drop the sitecustomize clock shim
  (OD-109). Child environment constructed from scratch — ALLOWLIST construction, never
  inherit-then-strip (BC-6.01.002:70/:157 authoritative; pass-5 A02 aligns VP-034 and
  this section to it). AUTHORITATIVE EXACT KEY SETS (copied verbatim from
  BC-6.01.002 PC-1 "Authoritative exact key sets", pass-7 D05, orchestrator call 2 —
  ARCH-07 and VP-034 copy these sets verbatim; with no fake table and no declared
  `COLUMNS` the constructed key sets are exactly:
  - POSIX oracle child: `HOME`, `USERPROFILE`, `TMPDIR`, `LANG`, `TZ`,
    `PYTHONPATH`, `HYLO_TEST_NOW`, `LOCAL_MODEL_PREFIXES` (+ the `DGX_SL_*` keys
    the case sets, + `COLUMNS` when declared, + `PATH` when a fake table is
    declared).
  - Windows oracle child: the POSIX set, plus `TMP`, `TEMP`, `SYSTEMROOT` and
    `PYTHONIOENCODING=utf-8` (OD-183; the same conditional additions apply: + the
    `DGX_SL_*` keys the case sets, + `COLUMNS` when declared, + `PATH` when a fake
    table is declared).
  - POSIX Go child: `HOME`, `USERPROFILE`, `TMPDIR`, `XDG_CACHE_HOME`,
    `LOCALAPPDATA`, `HYLO_PATHS_CACHE_DIR`, `LANG`, `TZ`, `HYLO_TEST_NOW`,
    `HYLO_BACKENDS_0_MODEL_PREFIXES` (+ the `HYLO_*` setting keys the case sets, +
    `COLUMNS` when declared; NO `PATH` ever — the built binary is started by
    absolute path).
  - Windows Go child: the POSIX Go set, plus `TMP`, `TEMP`, `SYSTEMROOT` (the same
    conditional additions apply).
  `HOMEDRIVE`/`HOMEPATH` are NOT constructed keys on any OS (home is
  `HOME`+`USERPROFILE`); no key set on any OS includes `PATH` unless the fake-table
  condition holds; `HOME` is present on BOTH OSes (Windows included) and
  `USERPROFILE` on BOTH OSES (POSIX included), always the same case-temp value —
  both are set because Python 3.8+ `expanduser` ignores `HOME` on Windows, and
  legacy writes its caches to `<case-home>/.cache/dgx-llm/` (SL:78)).
  Value spellings: `LANG=en_US.UTF-8` (the strict UTF-8 parity locale, BC-1.01.008
  inv 2), `TZ=UTC` on every leg (pin, OD-171/OD-177), `PYTHONPATH` carrying only the
  sitecustomize clock shim, `SYSTEMROOT` with the runner's value (CPython cannot
  start without it; Go's `os/exec` adds it on Windows when missing), the child env
  built from scratch so the host shell's case-insensitive key matching never applies
  (pass-5 A2-07). Windows stdio, exactly ONE extra variable,
  `PYTHONIOENCODING=utf-8` (OD-183, pass-6 A03: CPython 3.11 piped stdio on
  Windows otherwise uses the ANSI code page, so the strict-UTF-8 parity mode of
  BC-1.01.008 could not be reached on the windows-2025 oracle and glyphs outside
  cp1252 would degrade the Windows goldens; stdio only — a table test pins that
  the variable changes stdio encoding and nothing else; `PYTHONUTF8` stays
  forbidden). By OD-190 this LF behavior is hylo-wide and named beside the builder
  variable, never hidden in the shim: hylo writes UTF-8 + LF line endings on every
  OS, and the Windows oracle's LF normalization is produced by the two named
  mechanisms — the builder's `PYTHONIOENCODING=utf-8` (encoding) and the shim's
  `newline="\n"` reconfigure (LF-only newlines). Conditional `PATH`: `PATH=<case>/bin`,
  ONLY when the case declares a subprocess-fake table (the fake `ps` of BC-3.02.002);
  the value is the harness constant, never the runner's `PATH`; cases without a fake
  table get no `PATH` key (ADV-P1-D05 resolution) — with no `PATH` key, CPython's
  subprocess fallback searches `os.defpath` (`/bin:/usr/bin`, SL:280), which is why
  the harness rejects an unseeded case with a truthy `session_id` unless a fake table
  is declared (ADV-P2-D12; BC-6.02.003 PC-6).
  Forbidden on both OSes: NO other `PYTHON*` variable except `PYTHONPATH` (EC-002: no
  `PYTHONUTF8` on either OS — BC-1.01.008 inv 2: `PYTHONUTF8=1` is NOT
  the parity mode; `PYTHONIOENCODING` appears on Windows only, as the OD-183
  `=utf-8` stdio pin above), no `*_proxy`, no inherited GP-1..GP-6 variables (e.g. no
  `DGX_SL_TTL`, which changes legacy TTL).
- Clock shim `internal/statusline/testdata/pyhooks/sitecustomize.py` on `PYTHONPATH`
  freezes `time.time`/`strftime`/`localtime`/`gmtime` from `HYLO_TEST_NOW` (decimal
  string parsed by both sides), stepped between refreshes; canary test fails the harness
  if the shim did not load (BC-6.01.003). Frozen-clock law (pass-5 D02, call 7): the
  shim parses `HYLO_TEST_NOW` to a float64 exactly as Python `float()` (within the BC
  grammar) and that float IS the `time.time()` value everywhere — Go parses the value
  to float64 once and `Env.Now` returns it directly; it is never round-tripped through
  `time.Time` nanoseconds (float64 spacing at ~1.79e18 ns exceeds the seconds-value
  ulp, so fractional instants could return as a neighbouring double and repr-drift the
  cache `ts`/`rl_ts`/`fetch_ts` bytes). `TimeFloat` applies only to the real clock
  (ARCH-06 time.go). Depth boundaries are call-context dependent
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
| Golden update flag | `-update` (`go test ./internal/parity -run TestParityTierB -update`); writes Python output; fails if interpreter unset. Writes ONLY the host's NATIVE golden set — `*.golden` from a Linux oracle run, `*.windows.golden` from a WINDOWS oracle run (pass-5 D29: a Linux `-update` run never touches `*.windows.golden`, resolving the BC-6.03.001 PC-6/PC-8 contradiction); regenerating the Windows set therefore requires the same command on a Windows host with the pinned interpreter (owner-periodic action; both sets committed together) |
| Tier A test | `TestParityTierA_Corpus` |
| Tier B test | `TestParityTierB_Goldens` |
| Tier C test | `TestParityTierC_DiffFuzz`, budget env `HYLO_PARITY_FUZZSECONDS` (0 = skip; nightly sets 1800 = 30 min per OS, OD-149) |
| Canary | `TestParityCanary_ShimLoaded` |
| Exclusion machinery | `TestParityExclusions_ClosedSet` |
| Cache swap | `TestParityCacheSwap_FourCaches` |
| Corpus hygiene | `TestCorpusHygiene` (settled, NFR-006) |
| Case dirs | `internal/statusline/testdata/parity/cases/<case-id>/` (corpus root; OD-148, matching BC-6.02.001/.003, BC-6.04.003) |
| case-id grammar | `<family>-<nnn>[-<variant>]`, families: frame, row1, transcript, row2, cost, cache, platform, cfgerr, swap, subagent, cps01..cps17, cpt01..cpt07, cpn01..cpn03, cpo01..cpo11, cpa01..cpa05. SUBAGENT FAMILY RULE (pass-7 D14): a subagent-family case is identified by the case-id SUFFIX `-sub` on a base case (e.g. `row1-003-sub`), the marker BC-6.01.001/BC-6.02.003/BC-6.03.001 use ("id suffix `-sub`"); the grammar's `subagent` token denotes that suffix family, NOT a `<subagent>-<nnn>` spelling, so the validator's rule is the determinate suffix match |
| Case contents | `stdin.json.tmpl`, `settings`, `argv` (pass-4 ruling, ADV-P4-A15/D09: the HANDLER-RELATIVE argument list — the elements after the `statusline` verb; default `[]`. In P1 the corpus validator admits only `[]` and `["--subagent"]`; the oracle receives `[python, -s, script]` plus the same list, so the oracle — which has no `statusline` verb — sees exactly the handler arguments. Other argv shapes are covered by Go table tests (BC-4.01.002), never parity. Supersedes the pass-3 "passed to the built `hylo` binary verbatim, default `["statusline"]`" wording and BC-4.01.002:111's "no flags" wording), `metrics.json` or mode (down/500/garbage), optional `seed/` cache seeds, `steps` (clock step + transcript appends per step, carried INSIDE `case.json` — pass-4 D10 — not as a sibling `steps.jsonl`) |
| Exclusions file | `internal/statusline/testdata/parity/exclusions.json` (beside the corpus root; OD-148 layout, BC-6.03.003/.004 PC-1); capture replays additionally use a git-ignored `captures/exclusions.json` validated by the same closed-set rule, CI never runs captures (pass-4 D12) |
| Tier B goldens | `internal/statusline/testdata/goldens/*.golden`, `*.windows.golden` |
| Clock shim | `internal/statusline/testdata/pyhooks/sitecustomize.py` |
| pyfmt generators/tables | `internal/pyfmt/testdata/gen/*.py`; tables `internal/pyfmt/testdata/*.golden` |
| Replay captures (git-ignored) | `captures/` (repo root) |
| D4-EX-3 class tests | `TestD4EX3_{Boolean,Enum,URL,Number,Text}` — FIVE names, five classes (OD-178, pass-5 A07; superseding the pass-4 four-name set): `Number` covers both number-range (BC-2.02.002) and number-grammar (BC-2.02.003; the grammar class maps to `_Number`); `Text` is the OD-178 seventh D4-EX-3 class covering composite-shape, pill-label, glyph and empty-text errors, with exact reason strings in the taxonomy vocabulary and its own table test `TestD4EX3_Text`. No Theme member — theme settings are rejected by the corpus validator (BC-6.02.003 EC-007), so a Theme D4-EX-3 case cannot exist in the corpus and no `TestD4EX3_Theme` name is canonical; the split rationale is NOT legacy analogs — Text also has none, yet keeps its Go table test precisely because its keys ARE registry-declared (composite-shape, pill-label, glyph, empty-text): `TestD4EX3_Text` is a Go table test only, not a parity exclusion entry (pass-6 A20, call 1). Superseding the earlier six-name list |
| D4-EX-1 test | `TestWindowAge_D4EX1_Windows_AncestorFound` (settled name, VP-012 v1.13; pass-7 A2-05) |
| Seeds reference | `seed/` holds the four cache files under their legacy file-name formats (legacy-shared named constants, BC-1.06.001; not renamed by the harness) |

Fixture co-location ADR (AD-13, OD-148): the synthetic corpus root is
`internal/statusline/testdata/parity/cases/`, with the committed exclusions file
`internal/statusline/testdata/parity/exclusions.json` beside it — fixtures stay with
the subject package while the runner `internal/parity` is generic and reads the
fixtures from the subject package (the pass-4 D10 fix aligned all live docs to this
OD-148 layout); Tier B goldens stay under `internal/statusline/testdata/` (they pin
statusline bytes); Go testdata is opaque, so the cross-package read is deliberate —
one fixture home per fixture class, no duplicate corpus.

Fixture resolution rule (pass-5 A2-16, call 18): `go test` sets cwd to the PACKAGE
directory, so cwd-relative fixture paths load zero cases and the POL-11 guard turns
that into a false red. Tests in `internal/parity` (and any cross-package testdata
reader) resolve fixtures through the named helper `par.moduleRoot()` — walks up from
cwd to the directory containing `go.mod`, returns that root; fixture paths are rooted
at the module root (`internal/statusline/testdata/...` relative to it), never
cwd-relative. Table-tested by the helper itself (run from a nested package dir:
resolver finds the root from any package directory).

## Mapping

BC-6.01.x -> oracle execution; BC-6.02.x -> case model/corpus/swap; BC-6.03.x ->
comparison + exclusions; BC-6.04.x -> CI legs, timing report, nightly Tier C
(workflow design in ARCH-08).
