---
document_type: behavioral-contract
level: L3
version: "1.2.2"
status: draft
producer: product-owner
timestamp: 2026-11-18T01:42:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - domain-spec/invariants.md
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - owner-decisions-log-2026-11-14.md
input-hash: "db24750"
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
  - "2026-11-17T21:45:00Z patch bump + ADV-P2 pass-2 remediation (owner rulings OD-155..165)"
  - "2026-11-18T01:42:00Z ADV-P3 remediation D06+D19+D20+D38: D4-EX-3 cache halves compared asymmetrically (oracle self-consistency + Go empty-listing) making Go-writes-no-caches satisfiable; OD-159/160/161 riders named; canonical entries gain package/scope and JSON expected files; EC-006 scope-conflict rule rewritten"
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

1. The file is `internal/statusline/testdata/parity/exclusions.json`. JSON keeps the P1
   build at zero added dependencies.
2. Each entry is an object with exactly these keys:
   - `id`, one of the closed set `D4-EX-1`, `D4-EX-2`, `D4-EX-3`, `OD-30`, `OD-76`,
     `temp-file`, `cp-x03`, `OD-159`, `OD-160`, `OD-161` (the parity-class names of
     BC-ALLOCATION.md; `cp-x03` added by OD-136; `OD-159`/`OD-160`/`OD-161` added by the
     owner rulings of 2026-11-17);
   - `case`, a case directory path relative to the corpus root;
   - `expected_output_file`, a path relative to the corpus root;
   - `package`, the Go test package import path that declares `table_test` (the tests
     live in more than one package — `internal/config`, `internal/platform`,
     `internal/statusline`, `internal/parity` — so `go test -list` needs it;
     ADV-P1-D17);
   - `scope`, one of `stdout` (compares captured stdout and exit code only),
     `stdout+caches` (stdout, exit code and the named-cache listings of both sides),
     `go-cache-listing` (the Go cache listing only); default `stdout`;
   - `table_test`, the name of a Go test function.
   `expected_output_file` format (one file per entry, defined): a UTF-8 JSON object
   `{"exit": <int>, "stdout": "<literal captured stdout>", "caches": {"<side>":
   {"<filename>": "<literal file bytes>"}}}` where `<side>` is `oracle` or `go` and
   `caches` may be omitted when the entry's `scope` does not claim caches
   (ADV-P1-D17).
3. The approved deviations and their owners:

   | `id` | Approved by | Scope of the exclusion | Contract that defines the expected behavior |
   |---|---|---|---|
   | `D4-EX-1` | D4-EX-1 | ⌂ on Windows (fake probe returns a start) | BC-3.02.001 (`TestWindowAge_D4EX1_Windows*`) |
   | `D4-EX-2` | D4-EX-2, OD-21/OD-32 | wrong-shape transcript lines skipped | BC-1.03.018/019/020 (21 BC-SL-099 rows + BC-SL-100/103 rows) |
   | `D4-EX-3` | D4-EX-3, OD-102/OD-114 | config-error line | BC-2.02.001..006 + theme class BC-2.01.003 (`TestConfigError_D4EX3_{Number,Boolean,URL,Enum,Theme}` + `config validate`) |
   | `OD-30` | OD-30, OD-110 | numeric sid: one string-form cost-history key | BC-1.05.006, BC-1.05.009 |
   | `OD-76` | OD-76, OD-110 | native process probe on macOS/Linux (true start in a repeated DST hour; ⌂ where localized `ps` fails) | BC-3.02.002 |
   | `temp-file` | OD-110 | Go removes temp files legacy leaks (cache-file comparison only) | BC-6.03.003 (`TestCacheStore_TempFile_CleanupOnFailedReplace`) |
   | `cp-x03` | OD-136 | degraded-line write itself fails (stdout closed); Go swallows the error and exits 0 where legacy CP-X03 exits 1 | BC-1.01.001 EC-005 (dedicated table test, name provisional — architect (OD-145)) |
   | `OD-159` | OD-159 | Go reads files as UTF-8 on all OSes where legacy's encoding differs | stories owning the file-reading verbs (SS-01; rider: BC-1.03.001 PC-3 directional test, ADV-P3-D19) |
   | `OD-160` | OD-160 | foreign-cache shapes in the cache directories | stories owning the cache-store verbs (SS-01; riders: BC-1.02.017 EC-010, BC-1.01.008 EC-011 directional tests, ADV-P3-D19) |
   | `OD-161` | OD-161 | integer `transcript_path` → no transcript | stories owning the stdin path-field verbs (SS-01; rider: BC-1.03.015 PC-3 directional test, ADV-P3-D19) |

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
   oracle under BC-6.03.002 PC-6"): the oracle's caches are compared against the oracle's
   own previous refresh (self-consistency, asserting legacy really rendered and wrote),
   and the Go side asserts the EMPTY-listing invariant of BC-2.02.001 PC-6 ("Go writes no
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
| EC-001 | Entry `{"id": "D4-EX-2", "case": "transcript/cp-t*", "expected_output_file": "...", "package": "...", "scope": "...", "table_test": "..."}` | Run FAIL: glob in `case` (no blanket exclusions) |
| EC-002 | Entry with `id: "OD-99"` | Run FAIL: id not in the closed set |
| EC-003 | Entry whose `table_test` names a deleted test | Run FAIL: table test missing |
| EC-004 | Excluded case where Go output now equals the oracle | Passes against its expected file only if the expected file also equals that output. Otherwise FAIL; the entry must be revisited, never silently ignored |
| EC-005 | `-update` (Tier B) run | Does not touch any `expected_output_file` of an exclusion entry |
| EC-006 | Same case listed under two different ids (e.g. a macOS numeric-sid case that hits both OD-30 and OD-76's repeated-DST class, both defaulting to `stdout+caches`) | Allowed. Each entry checked independently. Conflict rule: the entries' comparison halves must not DISAGREE on an artifact — two entries on one case must declare the same scope for the same artifact, or an explicitly narrower one (`stdout` inside `stdout+caches` is fine); disagreement on any claimed artifact fails the run (ADV-P3-D38: the former "must not both claim stdout" phrasing was wrong — the OD-30/OD-76 defaults themselves claim stdout+caches) |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| Entry `{"id": "D4-EX-3", "case": "config/ttl-nan", "expected_output_file": "config/ttl-nan/expected.json", "package": "internal/statusline", "scope": "stdout", "table_test": "TestConfigError_D4EX3_Number"}`; Go prints the expected config-error line; test passes | Report `D4-EX-3 config/ttl-nan TestConfigError_D4EX3_Number ok` | happy-path |
| Entry for `temp-file` on `cache/sid-slash-temp` | Cache-listing scope only; stdout still compared to the oracle and equal | edge-case |
| Entry with `"case": "transcript/*"` | Run FAIL before any case: `exclusion[3]: glob not allowed in case` | error |
| Entry whose table test fails | Run FAIL: `parity: exclusion D4-EX-2/transcript/cp-t01: table test TestTranscript_D4EX2_T01 failed` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-012 | The validator rejects every entry with a glob, an unknown id, a missing key, a missing file or a missing test | table test on the validator |
| VP-012 | A case differs from the oracle without failing only if a valid entry lists it and its expected file matches | table test over synthetic comparator inputs |

## Traceability

| Field | Value |
|-------|-------|
| Source | OD-105 (named exclusion list D4-EX-1/2/3; each excluded case matches its own expected output in dedicated table tests; an exclusion without a test fails the harness; no blanket exclusions); OD-110 (named entries for OD-30, OD-76 + native probe, Go temp cleanup; still no blanket exclusions); design §5.4 (`exclusions.json`, entry `{id, case, expected_output_file, table_test}`; fail on missing test, differing output, or glob); OD-117 target (1); DI-012 |
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
- BC-3.02.001, BC-3.02.002 — depend on: D4-EX-1 and OD-76 entries

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
