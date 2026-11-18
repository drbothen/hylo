# Cycle lessons — phase-1-spec-crystallization (active cycle)

Lessons recorded during this cycle, numbered per category (agent, process,
infrastructure) with discovery dates. Process-gap entries are cross-listed in
STATE.md's Drift Items table with their remediation target.

See `cycles/phase-0-ingestion/lessons.md` for Phase 0 entries L-PG-01..03.

## L-PG-04 [process-gap] — Machine-check Python-result vector cells against the oracle

- **Lesson:** (discovered 2026-11-17, ADV pass-1 remediation) Behavioral-contract
  vectors whose expected values are Python results were asserted oracle-verified
  (ASM-001) while containing wrong CPython results. When ~45 vector cells were
  re-run on CPython 3.11.7 during pass-1 remediation, 8 were wrong and had to be
  corrected.
- **Remedy:** When a vector cell carries a Python-produced expected value, run it
  against the oracle interpreter at write time and record the interpreter
  version next to the vector; never copy expected values from prose or memory.

(pre-D-448(b) exemption)

## L-PG-05 [process-gap] — Adapt plugin-template vocabulary to the target language

- **Lesson:** (discovered 2026-11-17, ADV pass-1 remediation) Rust vocabulary
  from plugin templates (proptest, Send + Sync) leaked into 60+ Go spec files
  because templates were instantiated without a target-language pass.
- **Remedy:** Spec-producing steps that instantiate plugin templates include a
  target-language vocabulary check before the step completes; template trait and
  attribute names are translated to their target-language equivalents.

(pre-D-448(b) exemption)

## L-PG-06 [process-gap] — Force an isolated HOME and cwd in every brief that may run the legacy oracle

- **Lesson:** (discovered 2026-11-17, ADV pass-2 remediation) An agent ran the
  legacy oracle with the real HOME and wrote a synthetic entry into the live
  prototype's cost-history cache. The entry was removed and the live file was
  otherwise verified intact by the orchestrator — but the live prototype was
  one probe away from pollution.
- **Remedy:** Every agent brief that may run legacy forces an isolated HOME and
  cwd; oracle runs never point at the live prototype's data files.

(pre-D-448(b) exemption)

## L-PG-07 [process-gap] — Measure oracle facts on the real program, end to end

- **Lesson:** (discovered 2026-11-17, ADV pass-2 remediation) Two agents
  reported different JSON depth limits (989/990 vs 993/994) from wrapper
  probes; the wrappers had different frame depths than the program. The
  orchestrator settled it by measuring the real legacy program end to end
  (isolated HOME): limit = 999 − Python frames to `raw_decode`.
- **Remedy:** Oracle facts are measured on the real program end to end, never
  inferred from wrapper probes; when two probes disagree, re-measure on the
  real program before writing the number into a contract.

(pre-D-448(b) exemption)

## L-PG-08 [process-gap] — Mint finding ids from one owner before parallel dispatch

- **Lesson:** (discovered 2026-11-17, ADV pass-2 remediation) Parallel agents
  minted different ids for the same crash class (CP-T08 vs CP-O06..08),
  forcing reconciliation during remediation and a redundant second ruling.
- **Remedy:** Finding ids are minted by one owner before parallel dispatch;
  parallel agents consume an id allocation, they do not create overlapping id
  spaces.

(pre-D-448(b) exemption)

## L-PG-09 [process-gap] — Write non-ASCII expected bytes as \uXXXX escapes and verify on disk

- **Lesson:** (discovered 2026-11-18, ADV pass-3 remediation) An escape-decoding
  step turned valid \uXXXX escapes into raw characters in expected-output cells,
  corrupting committed BC vectors.
- **Remedy:** Non-ASCII expected bytes in vector cells are written as \uXXXX
  escapes and a script verifies the on-disk bytes after every edit; expected
  values are never decoded by hand or pasted as raw characters.

**Closes:** D-448(b) codified (strand ADV-P3-D09 systemic escape-rendering corruption)

## L-PG-10 [process-gap] — Run character-class scans as python scripts, not shell-wrapped grep

- **Lesson:** (discovered 2026-11-18, ADV pass-3 remediation) A non-English word
  reached a committed spec because the orchestrator's character scan used
  grep -P through a shell function wrapping ugrep, which silently matched
  nothing.
- **Remedy:** Character-class and non-English scans of committed specs run as
  python scripts whose result is asserted on disk; a scan that can silently
  degrade to zero matches is not a scan.

**Closes:** D-448(b) codified (strand ADV-P3-A17 hygiene scan gap P14/P21)

## L-PG-11 [process-gap] — Line-number facts in briefs must come from a numbered read

- **Lesson:** (discovered 2026-11-18, ADV pass-3 remediation) An orchestrator
  brief stated a legacy line number from a misread excerpt (SL:1238 vs the
  actual SL:1240) and agents propagated the wrong number into specs.
- **Remedy:** Line facts in agent briefs come from a numbered read (awk or
  sed -n with line numbers), never from prose excerpts; agents re-verify any
  line fact they receive before writing it into a contract.

**Closes:** D-448(b) codified (strands ADV-P3-A2-02 + ADV-P3-D05 legacy SL:1240 CLI-routing line facts)

## L-PG-12 [process-gap] — Run the sync check after adding scope, before the next adversarial pass

- **Lesson:** (discovered 2026-11-18, ADV pass-3 remediation) Pass 3 regressed
  (116 → 150 findings) because pass-2 remediation added new scope (OD-155
  `--subagent` BCs, rulings OD-156..165) without a propagation check.
- **Remedy:** After a remediation adds new scope, the sync check runs before
  the next adversarial pass dispatches; scope added without propagation is the
  documented root cause of trajectory regressions.

**Closes:** D-448(b) codified (strands ADV-P3-D04 + ADV-P3-D07 + ADV-P3-D10 OD-155/OD-156..165 scope propagation)
