---
document_type: behavioral-contract
level: L3
version: "1.1"
status: draft
producer: product-owner
timestamp: 2026-11-15T17:00:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - domain-spec/invariants.md
  - behavioral-contracts/BC-ALLOCATION.md
  - ../semport/hylo-legacy/statusline-target-design.md
  - owner-decisions-log-2026-11-14.md
input-hash: "0000000"
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
modified: []
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
     `temp-file`, `cp-x03` (the parity-class names of BC-ALLOCATION.md; `cp-x03` added by
     OD-136);
   - `case`, a case directory path relative to the corpus root;
   - `expected_output_file`, a path relative to the corpus root;
   - `table_test`, the name of a Go test function.
3. The approved deviations and their owners:

   | `id` | Approved by | Scope of the exclusion | Contract that defines the expected behavior |
   |---|---|---|---|
   | `D4-EX-1` | D4-EX-1 | ⌂ on Windows (fake probe returns a start) | BC-3.02.001 (`TestWindowAge_D4EX1_Windows*`) |
   | `D4-EX-2` | D4-EX-2, OD-21/OD-32 | wrong-shape transcript lines skipped | BC-1.03.018/019/020 (21 BC-SL-099 rows + BC-SL-100/103 rows) |
   | `D4-EX-3` | D4-EX-3, OD-102/OD-114 | config-error line | BC-2.02.001..005 (`TestConfigError_D4EX3_{Number,Boolean,URL,Enum}` + `config validate`) |
   | `OD-30` | OD-30, OD-110 | numeric sid: one string-form cost-history key | BC-1.05.006, BC-1.05.009 |
   | `OD-76` | OD-76, OD-110 | native process probe on macOS/Linux (true start in a repeated DST hour; ⌂ where localized `ps` fails) | BC-3.02.002 |
   | `temp-file` | OD-110 | Go removes temp files legacy leaks (cache-file comparison only) | BC-6.03.003 (`TestCacheStore_TempFile_CleanupOnFailedReplace`) |
   | `cp-x03` | OD-136 | degraded-line write itself fails (stdout closed); Go swallows the error and exits 0 where legacy CP-X03 exits 1 | BC-1.01.001 EC-005 (dedicated table test, name provisional — architect (OD-145)) |

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
   - `table_test` does not match `^Test[A-Za-z0-9_]+$`.
2. **Table test must exist and run.**
   - Each `table_test` must appear in `go test -list '.*'` output for its package.
   - In a full `go test` run, the harness checks the test-event stream (`-json`) and
     fails if a named test did not run or did not pass.
   - Error message: `parity: exclusion <id>/<case>: table test <name> missing|skipped|failed`.
3. **Excluded comparison.** For an excluded case, the artifacts named by the entry's
   scope are compared to `expected_output_file` instead of the oracle. For `temp-file`
   the scope is the Go cache listing; for the others it is stdout plus the named
   caches the case declares.
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
| EC-001 | Entry `{"id": "D4-EX-2", "case": "transcript/cp-t*", ...}` | Run FAIL: glob in `case` (no blanket exclusions) |
| EC-002 | Entry with `id: "OD-99"` | Run FAIL: id not in the closed set |
| EC-003 | Entry whose `table_test` names a deleted test | Run FAIL: table test missing |
| EC-004 | Excluded case where Go output now equals the oracle | Passes against its expected file only if the expected file also equals that output. Otherwise FAIL; the entry must be revisited, never silently ignored |
| EC-005 | `-update` (Tier B) run | Does not touch any `expected_output_file` of an exclusion entry |
| EC-006 | Same case listed under two different ids (e.g. a D4-EX-3 config case on Windows that also hits D4-EX-1) | Allowed. Each entry checked independently; scopes must not both claim stdout |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| Entry `{"id": "D4-EX-3", "case": "config/ttl-nan", "expected_output_file": "config/ttl-nan/expected.stdout", "table_test": "TestConfigError_D4EX3_Number"}`; Go prints the expected config-error line; test passes | Report `D4-EX-3 config/ttl-nan TestConfigError_D4EX3_Number ok` | happy-path |
| Entry for `temp-file` on `cache/sid-slash-temp` | Cache-listing scope only; stdout still compared to the oracle and equal | edge-case |
| Entry with `"case": "transcript/*"` | Run FAIL before any case: `exclusion[3]: glob not allowed in case` | error |
| Entry whose table test fails | Run FAIL: `parity: exclusion D4-EX-2/transcript/cp-t01: table test TestTranscript_D4EX2_T01 failed` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-TBD | The validator rejects every entry with a glob, an unknown id, a missing key, a missing file or a missing test | table test on the validator |
| VP-TBD | A case differs from the oracle without failing only if a valid entry lists it and its expected file matches | table test over synthetic comparator inputs |

## Traceability

| Field | Value |
|-------|-------|
| Source | OD-105 (named exclusion list D4-EX-1/2/3; each excluded case matches its own expected output in dedicated table tests; an exclusion without a test fails the harness; no blanket exclusions); OD-110 (named entries for OD-30, OD-76 + native probe, Go temp cleanup; still no blanket exclusions); design §5.4 (`exclusions.json`, entry `{id, case, expected_output_file, table_test}`; fail on missing test, differing output, or glob); OD-117 target (1); DI-012 |
| Parity class | n.a. (harness machinery) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/statusline/testdata/parity/exclusions.json`; harness exclusion validator (filled by architect) |
| Stories | TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-6.03.002 — composes with: excluded artifacts bypass the oracle comparison
- BC-6.03.003 — depends on: the `temp-file` entry
- BC-2.02.001 — depends on: D4-EX-3 entries and their table tests
- BC-1.03.019 — depends on: D4-EX-2 entries (21 rows)
- BC-1.05.006 — depends on: OD-30 entry
- BC-3.02.001, BC-3.02.002 — depend on: D4-EX-1 and OD-76 entries

## Architecture Anchors (Recommended)

- TBD (filled by architect) — parity harness exclusion list

## Story Anchor (Recommended)

TBD (filled by story-writer)

## VP Anchors (Recommended)

- TBD — exclusion validator properties above
