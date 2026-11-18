---
document_type: behavioral-contract
level: L3
version: "1.2.9"
status: draft
producer: product-owner
timestamp: 2026-11-21T09:00:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - domain-spec/invariants.md
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - semport/hylo-legacy/hylo-legacy-pass-5-deep-conventions-r5.md
  - owner-decisions-log-2026-11-14.md
input-hash: "f1d024f"
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
  - "2026-11-18T01:42:00Z ADV-P3 remediation D04+D26: oracle argv allows --subagent for the subagent corpus family (OD-155 supersedes OD-14); Architecture Module anchor corrected to internal/parity"
  - "2026-11-18T23:00:00Z (1.2.2): ADV-P4 remediation D09 — case.json argv minted as the HANDLER-RELATIVE list (after the verb), default [], P1 validator admits [] and [\"--subagent\"] only (design call 9); PC-5/VP-034 aligned"
  - "2026-11-19T03:00:00Z (1.2.3): ADV-P6 remediation D16/OD-185 — PC-4 extended: resolved oracle patch recorded AND measured constants self-checked before the first case (committed probe measures decode/dumps/dump boundaries 994/994/995 and unicodedata.unidata_version 14.0.0; fail closed printing the resolved version); the 3.11.x floating pin stands (OD-185 withdraws the pass-5 exact-3.11.7 call)"
  - "2026-11-19T08:30:00Z (1.2.4): ADV-P7 remediation D04 (orchestrator call 7) — PC-4 self-check probe redefined as the ONE end-to-end definition: the probe drives the real oracle (case argv, temp HOME/cwd) and asserts the laws' own constants at the pinned sites — stdin decode 993 accepted/994 rejected, session-cache save (json.dump, s=4) 991 writes/992 skips, subagent wire (json.dumps, s=3) 991 renders — replacing the inconsistent helper-scope triple (994/994/995); values measured this burst (CPython 3.11.7, unidata_version 14.0.0); VP-006 and ARCH-07 to copy"
  - "2026-11-21T06:00:00Z (1.2.5): ADV-P10 remediation D02 (orchestrator call 2) — PC-5 states the one subagent-family rule: an id of the form subagent-<nnn>[-<variant>] is the only shape that receives argv [\"--subagent\"]; the erroneous 'older -sub shorthand' notation removed (there is no -sub suffix rule)"
  - "2026-11-21T07:00:00Z (1.2.6): ADV-P11 remediation A07 (orchestrator call 8) + B08 (call 15) — new PC-7 defines the oracle-dependent test set by ONE named mechanism, the build tag oracle (//go:build oracle) on every test needing the Python oracle (Tier A corpus, shim canary, four-cache swap, any other); plain test step, coverage and release exclude exactly that set; PC-4's self-check probe adds the normpath NUL-retention probe (posixpath.normpath('a\\0b') and ntpath.normpath('a\\0b') both keep the NUL, returning 'a\\x00b', orchestrator-measured CPython 3.11.7), grounding BC-1.02.022"
  - "2026-11-21T09:00:00Z (1.2.7): pass-11 residual (orchestrator call, binding) — PC-7 respelled from the minted `oracle` build tag to the single ORACLE_TESTS -run/-skip pattern of the ARCH-07 OD-145 table (plain test/coverage/release pass `-skip $ORACLE_TESTS`; the dedicated Tier A job runs `-run $ORACLE_TESTS`; a new oracle-dependent test extends the pattern); no member change — the same three named tests"
  - "2026-11-22T00:00:00Z (1.2.8): ADV-P12 remediation A08 BC half (orchestrator call 6) — PC-7's ORACLE_TESTS membership completed: TestParityTierC_DiffFuzz (drives both sides) and TestTiming (reports the CPython oracle median, BC-6.04.002 PC-2) join the three pass-11 members, pattern constant now five alternates; the Tier A job, the timing job and the nightly fuzz job each install Python and -run their own member(s); plain test/coverage/release keep -skip over the whole pattern"
  - "2026-11-23T00:00:00Z (1.2.9): ADV-P13 remediation D01 (orchestrator call 2) — PC-3's version-probe regex is matched after the ONE open CRLF→LF conversion of BC-6.03.002 PC-1 on the Windows legs (the conversion is defined once for every comparison of the ORACLE's stdout there, not scoped to the case comparator), so the `\\n$` anchor holds on every leg"
deprecated: null
deprecated_by: null
replacement: null
retired: null
removed: null
removal_reason: null
---

# Behavioral Contract BC-6.01.001: Oracle runs via explicit absolute CPython 3.11.x path, never PATH; invoked with -s, never -I/-E

## Description

The parity harness runs the legacy oracle (`legacy/dgx_statusline.py`) only through an
interpreter path given explicitly as a harness setting. That path must be absolute and
must resolve to CPython 3.11.x. The harness never looks Python up on `PATH`. The argv is
fixed to `<python> -s <legacy script>`. The flags `-I`, `-E` and `-S` are never passed,
because each one stops `PYTHONPATH`/`site` from loading the clock shim (BC-6.01.003).

## Preconditions

1. The harness setting `HYLO_PARITY_PYTHON` is read from the environment of the
   `go test` process. It is a test-harness setting, not a D15 config key; the product
   binary never reads it.
2. The legacy script is resolved from the repository root as
   `legacy/dgx_statusline.py` and converted to an absolute path before exec.
3. CI sets `HYLO_PARITY_PYTHON` to the absolute interpreter path reported by
   `actions/setup-python` for CPython 3.11 (OD-108). The research Q7 recipe
   `HYLO_PARITY_PYTHON=python` is superseded and invalid.

## Postconditions

1. **Absolute path only.** If `HYLO_PARITY_PYTHON` is set and
   `filepath.IsAbs(value)` is false (e.g. `python`, `python3.11`, `./py`), the Tier A
   package fails (not skips). The message is
   `parity: HYLO_PARITY_PYTHON must be an absolute path (OD-104/OD-108), got "<value>"`.
2. **No PATH discovery.** The harness execs the value as given, through
   `exec.Cmd{Path: <value>}` or `exec.Command` with an absolute first argument. It never
   calls `exec.LookPath`, never runs a shell, and never falls back to `python3`/`python`
   when the setting is unset or invalid.
3. **Version check.** Before the first oracle case of a run, the harness runs
   `<value> -s -c "import sys,platform; print(platform.python_implementation(), *sys.version_info[:3])"`
   under the child environment of BC-6.01.002. Stdout must match
   `^CPython 3 11 [0-9]+\n$` — on the Windows legs after the ONE open CRLF→LF
   conversion of BC-6.03.002 PC-1, which is defined once for every comparison of the
   ORACLE's stdout there (pass-13 orchestrator call 2), so the `\n$` anchor holds on
   every leg. Anything else, including a non-zero exit, fails the run with
   the observed string in the message.
4. **Resolved patch recorded, measured constants self-checked (OD-185; pass-7 D04).**
   The patch number from step 3 (e.g. `3.11.7`) is written into the Tier B golden
   metadata when goldens are regenerated (BC-6.03.001; design risk RK-4). It is also
   printed once per Tier A run. Because the measured constants pinned in this spec set
   (the JSON depth laws of BC-5.02.003/BC-5.02.006 and the OD-170 Unicode 14.0 tables)
   were taken on CPython 3.11.7 while CI installs the latest 3.11.x patch (OD-104,
   OD-185), the harness then self-checks the resolved oracle before the first case.
   ONE definition (pass-7 orchestrator call 7): the committed probe drives the REAL
   oracle END TO END — the same argv as every case (PC-5), an isolated temp HOME and
   cwd, deep stdin serialized by concatenation — and asserts the pinned constants at
   the pinned sites, not helper-scope surrogates:
   - **stdin decode** (BC-5.02.003 law, `F = 6`): a `--subagent` stdin document of
     total nesting 993 renders its task row (accepted); 994 renders zero rows
     (rejected).
   - **session-cache save** (BC-5.02.006 `json.dump` law, `s = 4`): a `rate_limits`
     chain whose saved document nests 991 writes the `"rl"` member; 992 skips the deep
     write (the later flat save still persists the file, so the observer is the
     `"rl"` member, not the file's existence).
   - **subagent wire** (BC-5.02.006 `json.dumps` law, `s = 3`): an id chain of 990
     (wire object 991, stdin document 993) renders its row — the attainable boundary;
     the next chain overruns the stdin decoder first (document 994 → zero rows).
   - **normpath NUL retention** (BC-1.02.022; pass-11 B08, orchestrator call 15):
     `posixpath.normpath('a\0b')` and `ntpath.normpath('a\0b')` both KEEP the NUL,
     returning `'a\x00b'` (orchestrator-measured on CPython 3.11.7) — a pre-gh-106242
     oracle that truncated at the NUL fails here instead of silently diverging from
     the BC-1.02.022 `a\0b` → `a\0b` vector.
   The probe also prints `unicodedata.unidata_version` (pinned `14.0.0`). Any mismatch
   fails the run closed, printing the resolved version string; a reviewed spec
   amendment re-pins the constants when a future 3.11.x patch shifts an internal
   boundary. Measured under this method (pass-7 D04, CPython 3.11.7, default
   recursion limit 1000): decode 993 accepted / 994 rejected, save 991 writes / 992
   skips, wire 991 renders, normpath NUL retained in both flavors, `unidata_version`
   `14.0.0` — identical to the laws'
   constants, as the one definition requires. VP-006 and ARCH-07 state these same
   constants.
5. **Exact argv for every oracle refresh:**
   `[<value>, "-s", <abs>/legacy/dgx_statusline.py]` followed by the case's
   **handler-relative argv** — the `argv` field of `case.json`, which lists arguments AFTER
   the `statusline` verb and defaults to `[]` (orchestrator design call 9, ADV-P4-D09; the
   P1 corpus validator admits only `[]` and `["--subagent"]`, the latter for the
   `subagent` case-id family of ARCH-07's grammar — an id of the form
   `subagent-<nnn>[-<variant>]`, the only shape that receives that argv (ADV-P10-D02,
   orchestrator call 2; there is no `-sub` suffix rule) — per OD-155 which
   supersedes OD-14, exercising the `main_subagent` path, SL:1240,
   exactly as the Go side does). No other interpreter flags, no `-X` options; the oracle
   never receives the verb itself, and any other argv shape is Go-table-test territory
   (BC-4.01.002), never parity.
6. **Unset locally means skip; unset in CI means fail.** If the setting is unset and the
   CI marker `CI=true` is absent, Tier A skips with
   `parity: HYLO_PARITY_PYTHON unset; Tier A (live differential) skipped`. Tier B still
   runs without Python. If the setting is unset and `CI=true` is present, Tier A fails.
7. **Oracle-dependent test set: one named mechanism (ADV-P11-A07, orchestrator call 8; pass-11 residual respell to the ARCH-07 OD-145 binding; membership completed pass-12 call 6).**
   The oracle-dependent test set — the Tier A corpus suite
   (`TestParityTierA_Corpus`), the clock-shim canary (`TestParityCanary_ShimLoaded`,
   BC-6.01.003), the four-cache swap (`TestParityCacheSwap_FourCaches`, BC-6.02.004),
   the Tier C differential fuzz (`TestParityTierC_DiffFuzz`, BC-6.04.003) and the
   timing target (`TestTiming`, BC-6.04.002, which reports the CPython oracle
   median) — is selected by ONE named mechanism, the
   `ORACLE_TESTS` pattern constant
   (`^(TestParityTierA_Corpus|TestParityCanary_ShimLoaded|TestParityCacheSwap_FourCaches|TestParityTierC_DiffFuzz|TestTiming)$`,
   ARCH-07 OD-145 table): the plain test step, the coverage job and the release job pass
   `-skip $ORACLE_TESTS` and therefore exclude exactly that set, while the dedicated
   Tier A job, the timing job and the nightly fuzz job each install Python and
   `-run` their own member(s) (pass-12 call 6; BC-6.04.001 PC-3). The interpreter rules
   above are unchanged inside an oracle-bearing run (unset locally skips per PC-6; unset
   with `CI=true` fails per PC-6). There is no second selector mechanism and no build
   tag: a new oracle-dependent test extends the `ORACLE_TESTS` pattern, never a second
   mechanism.

## Invariants

1. The oracle interpreter is identical for every case and step of one harness run. The
   harness reads the setting once.
2. `-I`, `-E` and `-S` never appear in any oracle argv. A unit test of the argv builder
   asserts this for every case shape.
3. The harness never edits `legacy/` (D10). The shim lives under
   `internal/statusline/testdata/pyhooks/`.

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | `HYLO_PARITY_PYTHON=python` (the superseded research recipe) | Tier A fails with the absolute-path message; no lookup is attempted |
| EC-002 | Absolute path to CPython 3.12.x or 3.9.x | The version check fails, naming the observed version; no case runs |
| EC-003 | Absolute path to a non-CPython implementation (e.g. PyPy 3.11) | The version check fails (`platform.python_implementation()` is not `CPython`) |
| EC-004 | Absolute path that does not exist or is not executable | The run fails with the exec error; no PATH fallback |
| EC-005 | Windows absolute path such as `C:\hostedtoolcache\...\python.exe` | Accepted (`filepath.IsAbs` is true on Windows); same argv shape |
| EC-006 | Unset locally (`CI` not `true`) | Tier A skipped with the documented message; Tier B runs |
| EC-007 | Unset in CI (`CI=true`) | Tier A fails; CI cannot pass silently without the oracle |
| EC-008 | A future refactor adds `-I` to "harden" the oracle (pass-8 §8.2 wording) | The argv-builder unit test fails; the shim canary (BC-6.01.003) also fails |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `HYLO_PARITY_PYTHON=/opt/py311/bin/python3.11` (CPython 3.11.7) | Version probe prints `CPython 3 11 7`; oracle argv = `[/opt/py311/bin/python3.11, -s, <abs>/legacy/dgx_statusline.py]` | happy-path |
| Setting unset, `CI` unset | Tier A `t.Skip` with `parity: HYLO_PARITY_PYTHON unset; Tier A (live differential) skipped` | edge-case |
| `HYLO_PARITY_PYTHON=python3` | FAIL: `parity: HYLO_PARITY_PYTHON must be an absolute path (OD-104/OD-108), got "python3"` | error |
| Absolute path to CPython 3.12.4 | FAIL: version check, observed `CPython 3 12 4` | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-034 | For every case/step shape, the oracle argv equals `[abs python, "-s", abs script]` followed by the case's handler-relative argv (`[]` or `["--subagent"]` in P1, design call 9) and contains none of `-I`, `-E`, `-S` | table test on the argv builder |
| VP-034 | No harness code path calls `exec.LookPath` or a shell to start the oracle | manual review + `go vet`-style grep test |
| VP-034 | A non-absolute or non-3.11 interpreter never runs an oracle case | table test |

## Traceability

| Field | Value |
|-------|-------|
| Source | OD-104 (CPython 3.11.x oracle, explicit interpreter, never PATH); OD-108 (CI passes setup-python's absolute path; research Q7 recipe superseded); OD-109 (`-s`, never `-I`); design §3.2 "Interpreter" row, §7.1 T4/T5; P5r5 §B.4 P1 pin set ("`-s` ..., never `-E`/`-I`") |
| Parity class | n.a. (harness machinery) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/parity` parity harness (`*_parity_test.go`) (BC-COMPONENT-MAP: internal/parity/oracle.go (explicit interpreter, -s) — ARCH-07; ADV-P3-D26) |
| Stories | TBD (filled by story-writer) |

> Capability anchor rationale (OD-153): the parity harness is verification machinery whose sole purpose is proving CAP-009 byte parity (the D4 exit criterion), governed by DI-012.

## Related BCs (Recommended)

- BC-6.01.002 — composes with: the env builder that the version probe and every oracle run use
- BC-6.01.003 — depends on: `-s` keeps `PYTHONPATH` active, so the clock shim loads; the canary detects violations
- BC-6.03.001 — related to: the resolved patch version is recorded in Tier B golden metadata
- BC-6.04.001 — related to: CI installs CPython 3.11 on all three OSes and passes the absolute path

## Architecture Anchors (Recommended)

- `architecture/ARCH-07-parity-harness.md` — internal/parity/oracle.go (explicit interpreter, -s) (parity harness oracle runner) (BC-COMPONENT-MAP: ARCH-07 (ARCH-07-parity-harness.md))

## Story Anchor (Recommended)

TBD (filled by story-writer)

## VP Anchors (Recommended)

- VP-034 — oracle argv and interpreter-resolution properties above

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | spawns interpreters/builds; replay corpus and cache-swap I/O |
| **Global state access** | builds the child environment from scratch |
| **Deterministic** | stepped clock; seeded synthetic corpus |
| **Thread safety** | test-only, single-shot |
| **Overall classification** | infrastructure |

Owning component `internal/parity` (BC-COMPONENT-MAP: par/oracle.go (explicit interpreter, -s) - ARCH-07); the ARCH-00 package table classifies the package infrastructure - spawns interpreters/builds; test-only, never shipped in the render path.
