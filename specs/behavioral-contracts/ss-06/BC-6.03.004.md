---
document_type: behavioral-contract
level: L3
version: "1.3.6"
status: draft
producer: product-owner
timestamp: 2026-11-21T06:00:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - domain-spec/invariants.md
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - owner-decisions-log-2026-11-14.md
input-hash: "2fda8ad"
traces_to: domain-spec/L2-INDEX.md
origin: greenfield
extracted_from: "n.a. (new contract, no legacy source)"
subsystem: "SS-06"
capability: "CAP-009"
legacy_id: "new"
parity_class: "n.a."
confidence: "—"
lifecycle_status: active
introduced: "0.1"
modified:
  - "1.2.1 2026-11-17T21:45:00Z patch bump + ADV-P2 pass-2 remediation (owner rulings OD-155..165)"
  - "1.2.2 2026-11-18T01:42:00Z ADV-P3 remediation D06+D19+D20+D38: D4-EX-3 cache halves compared asymmetrically (oracle self-consistency + Go empty-listing) making Go-writes-no-caches satisfiable; OD-159/160/161 riders named; canonical entries gain package/scope and JSON expected files; EC-006 scope-conflict rule rewritten"
  - "1.2.3 2026-11-18T02:00:00Z: ADV-P4 remediation D12+D13+D22+OD-169 - closed set = eleven ids (OD-166 added with own scope wording); oracle self-consistency leg defined for single-step and Number-class shapes; exclusions.json relocated beside the corpus root; TestD4EX3 canonical names, Theme member removed (stamp re-dated ascending 2026-11-19, SC-27)"
  - "2026-11-18T22:00:00Z (1.2.4): pass-4 correction (item 10) - exclusions.json and corpus root restored to the OD-148 homes internal/statusline/testdata/parity/exclusions.json and internal/statusline/testdata/parity/cases/ (fixtures stay with the subject package)"
  - "2026-11-18T23:30:00Z (1.2.5): pass-4 sync-check SC-11 — modified history re-spun oldest-first so the version field matches the last entry; no behavioral change"
  - "2026-11-19T00:20:00Z (1.2.6) ADV-P5 remediation D04+D20+OD-178 — Number class corrected per value (grammar failures crash at import; nan/inf/-1/1e400/4_0/non-ASCII digits parse at SL:74 and use the two-legged asymmetry); scope is required, no default; canonical D4-EX-3 tests gain TestD4EX3_Text (five names, OD-178)"
  - "2026-11-19T02:00:00Z (1.2.7): sync-check adv-p5 closure (SC-19/SC-20) — modified history re-spun oldest-first so the version field matches the last entry; no behavioral change"
  - "2026-11-19T03:30:00Z (1.2.8): ADV-P6 remediation OD-181 + D14 + D24 — closed set = TWELVE ids (OD-181 'metrics transport beyond plain http' added with its own scope row); D4-EX-3 row states TestD4EX3_Text is a Go table test only backing no parity entry (Text keys have no legacy analog, same no-legacy-equivalent rule as Theme); EC-006 'defaulting' wording aligned with the required scope key (ADV-P5-D20)"
  - "2026-11-19T16:00:00Z (1.2.9): sync-check adv-p6 closure (SC-27) — the dipping 1.2.3 stamp re-dated ascending and respelled to the sibling version-leading form; no behavioral change"
  - "2026-11-19T17:00:00Z (1.3.0): ADV-P7 remediation D15 - PC-3's Number-value enumeration is the exhaustive union of the BC-2.02.002/BC-2.02.003 exclusion lists: the formerly unstated float-accepted values 2_0, ٢, -inf, 99999999999999999999 (int64 overflow) and 9223372036.854776 (Duration ceiling) now render-and-write on the oracle leg under the standard two-legged asymmetry"
  - "2026-11-19T19:00:00Z (1.3.1): pass-7 residual remediation — cp-x03's dedicated table test named TestCPX03_WriteFailureExit0 (OD-145 provisional name settled; ADV-P7-B09; VP-003, VP-012 and BC-1.01.001 EC-005 agree); OD-159 rider citation corrected from BC-1.03.001 PC-3 (the stat-race postcondition, which never mentions OD-159) to its real home BC-1.02.004 TestGitTextReads_OD159_StrictUTF8, the closure-validated riding test (VP-012's OD-159 row corrected to match); no behavioral change"
  - "2026-11-19T21:00:00Z (1.3.2): ADV-P8 remediation A2-05+D14 — OD-160 register riders corrected to the on-disk-verified anchors BC-1.02.017 EC-004..006 and BC-1.01.008 PC3 (the former EC-010/EC-011 pointed at the CP-O05 overflow row and a nonexistent row); PC-3 float-accepted enumeration respelled as the union of the float-accepted values in the BC-2.02.002/003 exclusion case lists AND edge cases (1e400 is BC-2.02.002 EC-004, not a named case)"
  - "2026-11-20T18:30:00Z (1.3.3): ADV-P9 remediation D01 (orchestrator call 7) — rider-test closure pinned: NO exclusions.json entry exists for OD-76 or D4-EX-1 (no corpus case can exercise either id); register rows and a post-table note respelled; EC-006's example respelled to an OD-30 + D4-EX-2 pair (the former OD-76 repeated-DST corpus case is impossible under the UTC-only corpus)"
  - "2026-11-21T06:00:00Z (1.3.4): ADV-P10 remediation D07 (orchestrator call 7) — example corpus ids flattened to the ARCH-07 grammar's flat cases/<case-id>/ form with <family>-<nnn>[-<variant>] ids: config/ttl-nan → cfgerr-001, cache/sid-slash-temp → cache-003, transcript/cp-t01 → cpt01-001, EC-001's glob respelled cpt01-* (EC and CTV examples only; no schema change)"
  - "2026-11-22T00:00:00Z (1.3.5): ADV-P12 remediation D01 (orchestrator call 2) — the D4-EX-1 row and the rider-test-closure paragraph restated per the corrected cache-003 design: every corpus case either seeds proc_start or is cache-003 (empty fake PATH raises FileNotFoundError on the oracle; Go child at HYLO_STATUSLINE_WINDOW_AGE_MAX_DEPTH=0 — no probe on either side); the former 'every corpus case seeds proc_start' universal is dissolved"
  - "2026-11-25T00:00:00Z (1.3.6): ADV-P14 remediation A2-01 (orchestrator call 1) + D06 (call 7) — PC-3 gains the machine-readable rider register for all TWELVE closed ids (package + concrete test names, no globs) as the spec source of the committed internal/parity/testdata/exclusion-riders.json (VP-012's leg reads it, checks the key set equals the closed set and every listed test exists via go test -list); TestWindowStart_OD76_TrueStart minted as the final concrete OD-76 name per BC-3.02.002's deferral; the oracle self-consistency leg's member scope pinned — clock-rewritten members excluded by legacy site (session rl_ts/fetch_ts/ts, sparkline hist, git-cache ts, cost-history entry ts) with the compared remainder stated"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-6.03.004: Exclusion-list machinery: per-case entries, expected files, table tests, no globs

## Description

Every owner-approved byte difference against the oracle is recorded as an explicit
entry in one committed JSON file. Each entry names one case, the expected Go output
for that case, and the dedicated Go table test that pins it. The harness validates the
list on every run and fails when:

- an entry has no table test;
- the Go output differs from its expected file;
- an entry uses a glob;
- an entry uses an id outside the closed set of approved deviation classes.

This is the only mechanism by which a parity case may differ from the oracle (DI-012).

## Preconditions

1. The file is `internal/statusline/testdata/parity/exclusions.json`, beside the corpus root
   `internal/statusline/testdata/parity/cases/` (OD-148 layout; single meaning for "relative to
   the corpus root"). JSON keeps the P1
   build at zero added dependencies.
2. Each entry is an object with exactly these keys:
   - `id`, one of the closed set of TWELVE ids `D4-EX-1`, `D4-EX-2`, `D4-EX-3`, `OD-30`,
     `OD-76`, `temp-file`, `cp-x03`, `OD-159`, `OD-160`, `OD-161`, `OD-166`, `OD-181`
     (the parity-class names of BC-ALLOCATION.md; `cp-x03` added by OD-136;
     `OD-159`/`OD-160`/`OD-161` added by the owner rulings of 2026-11-17; `OD-166`
     added by OD-169; `OD-181` added by OD-181);
   - `case`, a case directory path relative to the corpus root;
   - `expected_output_file`, a path relative to the corpus root;
   - `package`, the Go test package import path that declares `table_test` (the tests
     live in more than one package — `internal/config`, `internal/platform`,
     `internal/statusline`, `internal/parity` — so `go test -list` needs it;
     ADV-P1-D17);
   - `scope`, one of `stdout` (compares captured stdout and exit code only),
     `stdout+caches` (stdout, exit code and the named-cache listings of both sides),
     `go-cache-listing` (the Go cache listing only); required — no default (all six
     keys are mandatory, ADV-P5-D20; the formerly implied `stdout` default contradicted
     the missing-key validation below);
   - `table_test`, the name of a Go test function.
   `expected_output_file` format (one file per entry, defined): a UTF-8 JSON object
   `{"exit": <int>, "stdout": "<literal captured stdout>", "caches": {"<side>":
   {"<filename>": "<literal file bytes>"}}}` where `<side>` is `oracle` or `go` and
   `caches` may be omitted when the entry's `scope` does not claim caches
   (ADV-P1-D17).
3. The approved deviations and their owners:

   | `id` | Approved by | Scope of the exclusion | Contract that defines the expected behavior |
   |---|---|---|---|
   | `D4-EX-1` | D4-EX-1 | ⌂ on Windows (fake probe returns a start); NO `exclusions.json` entry exists (every corpus case either seeds `proc_start` or is `cache-003`, which probes on neither side, BC-3.02.001 Invariant 4): rider-test closure, ADV-P9-D01 | BC-3.02.001 (`TestWindowAge_D4EX1_Windows*`) |
   | `D4-EX-2` | D4-EX-2, OD-21/OD-32 | wrong-shape transcript lines skipped | BC-1.03.018/019/020 (21 BC-SL-099 rows + BC-SL-100/103 rows) |
   | `D4-EX-3` | D4-EX-3, OD-102/OD-114 | config-error line | BC-2.02.001..006 (`TestD4EX3_{Number,Boolean,URL,Enum,Text}` + `config validate`; no Theme member — theme settings are rejected by the corpus validator, BC-6.02.003 PC-3/EC-007, so no Theme D4-EX-3 case can exist; by the same no-legacy-equivalent rule `TestD4EX3_Text` is a GO TABLE TEST ONLY and backs no parity exclusion entry — Text keys (glyphs, labels, suffix) have no legacy analog; ADV-P6-D14, orchestrator call 1; ADV-P4-D22) |
   | `OD-30` | OD-30, OD-110 | numeric sid: one string-form cost-history key | BC-1.05.006, BC-1.05.009 |
   | `OD-76` | OD-76, OD-110 | native process probe on macOS/Linux (true start in a repeated DST hour; ⌂ where localized `ps` fails); NO `exclusions.json` entry exists (UTC-only corpus; rider-test closure, ADV-P9-D01) | BC-3.02.002 |
   | `temp-file` | OD-110 | Go removes temp files legacy leaks (cache-file comparison only) | BC-6.03.003 (`TestCacheStore_TempFile_CleanupOnFailedReplace`) |
   | `cp-x03` | OD-136 | degraded-line write itself fails (stdout closed); Go swallows the error and exits 0 where legacy CP-X03 exits 1 | BC-1.01.001 EC-005 (dedicated table test `TestCPX03_WriteFailureExit0` — the OD-145 provisional name settled; ADV-P7-B09) |
   | `OD-159` | OD-159 | Go reads files as UTF-8 on all OSes where legacy's encoding differs | stories owning the file-reading verbs (SS-01; rider: BC-1.02.004 riding table test `TestGitTextReads_OD159_StrictUTF8` — the deviation's defining UTF-8-read contract, ADV-P3-D19) |
   | `OD-160` | OD-160 | foreign-cache shapes in the cache directories | stories owning the cache-store verbs (SS-01; riders: BC-1.02.017 EC-004..006, BC-1.01.008 PC3 directional tests, ADV-P3-D19; anchors verified on disk and corrected from EC-010/EC-011 by pass-8 A2-05 — EC-010 is the CP-O05 overflow row and BC-1.01.008 has no EC-011) |
   | `OD-161` | OD-161 | integer `transcript_path` → no transcript | stories owning the stdin path-field verbs (SS-01; rider: BC-1.03.015 PC-3 directional test, ADV-P3-D19) |
   | `OD-166` | OD-169 | cost-history bytes written after a refresh whose `usd` or `api_ms` could not convert to float (nothing else) | BC-1.05.004 (dedicated table test; VP-012 closure row per OD-169) |
   | `OD-181` | OD-181 | metrics transport beyond plain http: non-http(s) redirect targets (hylo: no sample) and TLS trust-store differences for https (hylo: OS trust store); parity cases use plain http only, table tests pin hylo's behaviour | BC-1.04.001 (dedicated table tests) |

   ADV-P9-D01 / orchestrator call 7 (rider-test closure): NO committed `exclusions.json`
   entry exists for `OD-76` or `D4-EX-1` — no corpus case can exercise either id (the
   corpus is UTC-only, so a repeated-DST case cannot exist, and every corpus case either
   seeds
   `proc_start` or is the `temp-file` case `cache-003`, whose oracle raises
   `FileNotFoundError` on the empty fake `PATH` and whose Go child runs at
   `HYLO_STATUSLINE_WINDOW_AGE_MAX_DEPTH=0` — no probe on either side, BC-3.02.001
   Invariant 4 — so no unseeded-probe or Windows ⌂ case exists
   either). Each of the two ids is closed by its rider test alone — the dedicated Go table
   tests of BC-3.02.002 and BC-3.02.001. PC-1's `case`-existence requirement applies only
   when an entry is minted; a future phase that adds such a case mints the entry then. The
   ids stay in the closed set (owner-approved deviation classes, DI-012).

#### Rider register (machine-readable; A2-01, pass-14 orchestrator call 1)

The committed, machine-readable rider register in the code tree,
`internal/parity/testdata/exclusion-riders.json`, carries EXACTLY this content: one
entry per closed id, each a non-empty list of concrete `{package, test}` pairs, no
globs (`.factory/` is git-ignored on main, so no Go test can read a BC file — this
register is the machine-readable copy of the spec table above; the factory-side sync
check compares the JSON content with the table). VP-012's leg reads the committed
JSON, checks its key set equals the closed set, and checks that every listed test
exists (`go test -list` over the named package), failing on any missing name:

| `id` | `{package}` | tests |
|---|---|---|
| `D4-EX-1` | `internal/platform` | `TestWindowAge_D4EX1_Windows_AncestorFound` |
| `D4-EX-2` | `internal/statusline` | `TestTranscript_D4EX2_T01` |
| `D4-EX-3` | `internal/config` | `TestD4EX3_Number`, `TestD4EX3_Boolean`, `TestD4EX3_URL`, `TestD4EX3_Enum`, `TestD4EX3_Text` |
| `OD-30` | `internal/statusline` | `TestCostHistory_OD30_NumericSidStringKey` |
| `OD-76` | `internal/platform` | `TestWindowStart_OD76_TrueStart` |
| `temp-file` | `internal/statusline` | `TestCacheStore_TempFile_CleanupOnFailedReplace` |
| `cp-x03` | `internal/statusline` | `TestCPX03_WriteFailureExit0` |
| `OD-159` | `internal/statusline` | `TestGitTextReads_OD159_StrictUTF8` |
| `OD-160` | `internal/statusline` | `TestForeignCacheShape_OD160_Vectors` |
| `OD-161` | `internal/statusline` | `TestTranscriptPath_OD161_IntMeansNoTranscript` |
| `OD-166` | `internal/statusline` | `TestCostHistory_OD166_RecordGuard` |
| `OD-181` | `internal/statusline` | `TestMetricsClient_OD181_TransportTable` |

Each pair is the riding test its owning contract already names:
`TestWindowAge_D4EX1_Windows_AncestorFound` (BC-3.02.001 VP-014);
`TestTranscript_D4EX2_T01` (the T01-row test this contract's CTV pins; each
`exclusions.json` entry names its own row's concrete test in the same
`TestTranscript_D4EX2_<row>` form, BC-1.03.019); the five `TestD4EX3_*` names
(BC-2.02.001, OD-178; `TestD4EX3_Text` is the Go-table-only member backing no parity
entry); `TestCostHistory_OD30_NumericSidStringKey` (BC-1.05.006);
`TestWindowStart_OD76_TrueStart` (FINAL concrete name minted here per BC-3.02.002's
deferral: one dedicated table test carrying the D1-D4 exclusion rows and the
I1-I6 identical-column rows); `TestCacheStore_TempFile_CleanupOnFailedReplace`
(BC-6.03.003); `TestCPX03_WriteFailureExit0` (BC-1.01.001 EC-005, OD-145 settled);
`TestGitTextReads_OD159_StrictUTF8` (BC-1.02.004);
`TestForeignCacheShape_OD160_Vectors` (BC-1.05.004 VP-012, with BC-1.02.017
EC-004..006 and BC-1.01.008 PC3 as the directional anchors);
`TestTranscriptPath_OD161_IntMeansNoTranscript` (BC-1.03.015 VP-012);
`TestCostHistory_OD166_RecordGuard` (BC-1.05.004 VP-012, OD-169);
`TestMetricsClient_OD181_TransportTable` (BC-1.04.001 VP-012, defined in VP-030).
The cost-history record-path riders (`OD-30`, `OD-166`) are declared in
`internal/statusline`, where pass-13 orchestrator call 7 places cost-history file
I/O and temp-dir tests — not in the pure `internal/cost` core.

## Postconditions

1. **Load-time validation.** Before any case runs, the harness validates every entry.
   It fails the whole run, naming the entry index and the reason, when:
   - a key is missing, or an extra key is present;
   - `id` is not in the closed set;
   - `case` or `expected_output_file` contains any glob metacharacter (`*`, `?`, `[`,
     `{`), or is `.`, empty, or an absolute path;
   - `case` does not name an existing case directory, or `expected_output_file` does
     not exist;
   - two entries share the same `(id, case)`;
   - `table_test` does not match `^Test[A-Za-z0-9_]+$`;
   - `package` is not one of the harness's declared test-package import paths, or
     `scope` is not one of the three values above.
2. **Table test must exist and run.**
   - Each `table_test` must appear in `go test -list '.*'` output for its entry's
     `package`.
   - In a full `go test` run, the harness checks the test-event stream (`-json`) and
     fails if a named test did not run or did not pass.
   - Error message: `parity: exclusion <id>/<case>: table test <name> missing|skipped|failed`.
3. **Excluded comparison.** For an excluded case, the artifacts named by the entry's
   `scope` are compared to `expected_output_file` instead of the oracle: `temp-file`
   entries use `go-cache-listing`; D4-EX-3 config-error cases use `stdout` — scope
   `stdout` means ONLY the stdout line and exit code are pinned to the expected file.
   For the Boolean, Enum and URL classes legacy renders normally and writes its caches
   (SL:73-77, 89, 186), while a config-error run stops at step 0 on the Go side and Go
   writes NO caches. The cache halves are therefore compared ASYMMETRICALLY for these
   cases (ADV-P3-D06 disposition, amending the ADV-P2-D05 wording "still compared to the
   oracle under BC-6.03.002 PC-6"). The oracle self-consistency leg is DEFINED for every
   case shape (ADV-P4-D13): when the case has two or more steps, the oracle's caches
   after step k are compared against its own caches after step k-1; when the case has a
   SINGLE step, the harness runs the oracle TWICE at the same step instant (two
   consecutive refreshes) and compares the second refresh's caches against the first's
   — so "previous refresh" always exists. MEMBER SCOPE of the leg (pass-14 D06, orchestrator call 7): the leg compares only the cache members legacy does NOT rewrite from the clock on every refresh in which their write path fires — excluded by legacy site: session cache `rl_ts` (SL:307), `fetch_ts` (SL:349 update and SL:353) and `ts` (SL:349), plus the sparkline `hist` member (rewritten at SL:349-350, its appended points embedding `t: now`, SL:342); git cache `ts` (SL:410); cost-history per-session entry `ts` (SL:236). COMPARED REMAINDER: session cache `rl`, `up`, `sample`, `proc_start`; git cache `branch`; cost history `lane`, `usd`, `api_ms`, `src`; the mix cache fully (every member content-derived, SL:1150-1153). For the NUMBER class the degeneration holds
   ONLY for its grammar-failure values: `""`, `four`, `0x4` and rows `2.0` crash legacy
   at import (SL:74 `TTL = float(...)` / SL:75 `ROWS = int(...)`; CP-X01/X02: exit 1,
   empty stdout), so the oracle leg pins exactly that — exit 1, zero stdout bytes, empty
   cache listing — while the Go leg pins the config-error line via the expected file.
   The float-accepted Number values (`nan`, `inf`, `-inf`, `-1`, `1e400`, `4_0`, `2_0`,
   non-ASCII digits such as `٤` and `٢`, and the range-miss values `99999999999999999999`
   (int64 overflow) and `9223372036.854776` (Duration ceiling) — all accepted by legacy
   `float()`/`int()`, so legacy renders and writes its caches for every one of them)
   parse at SL:74/75: legacy renders normally and writes its caches
   (corrected per value, ADV-P5-D04 / owner call 12; the BC's own canonical
   `cfgerr-001` case previously pinned a crash real legacy does not perform). For
   those values the standard two-legged asymmetry applies, and the enumeration here is
   the union of the float-accepted values in the BC-2.02.002 and BC-2.02.003 exclusion
   case lists AND edge cases — BC-2.02.002's `1e400` is its EC-004 edge case, not a
   named exclusion case (pass-8 D14) — (pass-7 D15:
   `2_0`, `٢`, the two range-miss values and `-inf` were formerly unstated). The
   Boolean, Enum and URL
   classes — and the float-accepted Number values — use the two-legged asymmetry; PC-3
   of the class contracts names them exhaustively.
   The Go side asserts the EMPTY-listing invariant of BC-2.02.001 PC-6 ("Go writes no
   caches") instead of being compared to the oracle's listing. BC-6.03.002 PC-3's
   set-equality requirement is waived for an excluded case by the entry itself — the
   waiver is what the `scope: stdout` entry licenses. The other ids use
   `stdout+caches` over the named caches the case declares.
   - Every artifact outside the scope is still compared to the oracle (BC-6.03.002).
   - A Go output that differs from the expected file fails with
     `parity: exclusion <id>/<case>: go output differs from <expected_output_file>`.
4. **Unlisted differences fail.** A case with no entry is always compared to the
   oracle. No other configuration, flag, environment variable or skip list can exempt
   a case.
5. **Report.** Each run prints one line per entry: `<id> <case> <table_test>
   ok|FAIL`. It also prints a count per `id`, so a reviewer can see the full set of
   approved differences at a glance.

## Invariants

1. The closed id set changes only through an owner decision recorded in the
   decisions log (OD-105/OD-110 pattern). Adding an id is a spec change, not a test
   change.
2. No blanket exclusions: every entry names exactly one case and one test.
3. Expected files for excluded cases are reviewed artifacts. They are never
   regenerated from the oracle by `-update` (that would erase the deviation), and
   never silently regenerated from Go. They are updated only with an explicit
   `-update-exclusions` flag that writes Go's output and shows the diff in review.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Entry `{"id": "D4-EX-2", "case": "cpt01-*", "expected_output_file": "...", "package": "...", "scope": "...", "table_test": "..."}` | Run FAIL: glob in `case` (no blanket exclusions) |
| EC-002 | Entry with `id: "OD-99"` | Run FAIL: id not in the closed set |
| EC-003 | Entry whose `table_test` names a deleted test | Run FAIL: table test missing |
| EC-004 | Excluded case where Go output now equals the oracle | Passes against its expected file only if the expected file also equals that output. Otherwise FAIL; the entry must be revisited, never silently ignored |
| EC-005 | `-update` (Tier B) run | Does not touch any `expected_output_file` of an exclusion entry |
| EC-006 | Same case listed under two different ids (e.g. a case with a numeric sid whose transcript also contains a wrong-shape line, hitting both OD-30 and D4-EX-2, each entry declaring `scope: stdout+caches`) | Allowed. Each entry checked independently. Conflict rule: the entries' comparison halves must not DISAGREE on an artifact — two entries on one case must declare the same scope for the same artifact, or an explicitly narrower one (`stdout` inside `stdout+caches` is fine); disagreement on any claimed artifact fails the run (ADV-P3-D38: the former "must not both claim stdout" phrasing was wrong — the OD-30/D4-EX-2 entries declare stdout+caches; scope is REQUIRED with no default, ADV-P5-D20) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| Entry `{"id": "D4-EX-3", "case": "cfgerr-001", "expected_output_file": "cfgerr-001/expected.json", "package": "internal/statusline", "scope": "stdout", "table_test": "TestD4EX3_Number"}`; Go prints the expected config-error line; test passes | Report `D4-EX-3 cfgerr-001 TestD4EX3_Number ok` | happy-path |
| Entry for `temp-file` on `cache-003` | Cache-listing scope only; stdout still compared to the oracle and equal | edge-case |
| Entry with `"case": "transcript/*"` | Run FAIL before any case: `exclusion[3]: glob not allowed in case` | error |
| Entry whose table test fails | Run FAIL: `parity: exclusion D4-EX-2/cpt01-001: table test TestTranscript_D4EX2_T01 failed` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-012 | The validator rejects every entry with a glob, an unknown id, a missing key, a missing file or a missing test | table test on the validator |
| VP-012 | A case differs from the oracle without failing only if a valid entry lists it and its expected file matches | table test over synthetic comparator inputs |

## Traceability

| Field | Value |
|-------|-------|
| Source | OD-105 (named exclusion list D4-EX-1/2/3; each excluded case matches its own expected output in dedicated table tests; an exclusion without a test fails the harness; no blanket exclusions); OD-110 (named entries for OD-30, OD-76 + native probe, Go temp cleanup; still no blanket exclusions); design §5.4 (`exclusions.json`, entry `{id, case, expected_output_file, table_test}`; fail on missing test, differing output, or glob); OD-117 target (1); DI-012; OD-169 (OD-166 as the eleventh closed-set id, own table test and VP-012 closure row, "rides D4-EX-2"/"OD-156" wordings removed); OD-181 (twelfth closed-set id: metrics transport beyond plain http); ADV-P4-D13 (defined oracle self-consistency leg); ADV-P4-D22 (canonical TestD4EX3 names, no Theme member); ADV-P6-D14 (TestD4EX3_Text is a Go table test only, no parity entry) |
| Parity class | n.a. (harness machinery) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/statusline/testdata/parity/exclusions.json`; harness exclusion validator (BC-COMPONENT-MAP: internal/parity/exclusions.go (closed set, no globs) — ARCH-07) |
| Stories | TBD (filled by story-writer) |

> Capability anchor rationale (OD-153): the parity harness is verification machinery whose sole purpose is proving CAP-009 byte parity (the D4 exit criterion), governed by DI-012.

## Related BCs (Recommended)

- BC-6.03.002 — composes with: excluded artifacts bypass the oracle comparison
- BC-6.03.003 — depends on: the `temp-file` entry
- BC-2.02.001 — depends on: D4-EX-3 entries and their table tests
- BC-1.03.019 — depends on: D4-EX-2 entries (21 rows)
- BC-1.05.006 — depends on: OD-30 entry
- BC-3.02.001, BC-3.02.002 — depend on: D4-EX-1 and OD-76 (rider-test closure; NO `exclusions.json` entries, ADV-P9-D01)

## Architecture Anchors (Recommended)

- `architecture/ARCH-07-parity-harness.md` — internal/parity/exclusions.go (closed set, no globs) (parity harness exclusion list) (BC-COMPONENT-MAP: ARCH-07 (ARCH-07-parity-harness.md))

## Story Anchor (Recommended)

TBD (filled by story-writer)

## VP Anchors (Recommended)

- VP-012 — exclusion validator properties above

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | spawns interpreters/builds; replay corpus and cache-swap I/O |
| **Global state access** | builds the child environment from scratch |
| **Deterministic** | stepped clock; seeded synthetic corpus |
| **Thread safety** | test-only, single-shot |
| **Overall classification** | infrastructure |

Owning component `internal/parity` (BC-COMPONENT-MAP: par/exclusions.go (closed set, no globs) - ARCH-07); the ARCH-00 package table classifies the package infrastructure - spawns interpreters/builds; test-only, never shipped in the render path.
