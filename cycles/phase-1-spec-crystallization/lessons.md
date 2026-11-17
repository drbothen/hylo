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

## L-PG-05 [process-gap] — Adapt plugin-template vocabulary to the target language

- **Lesson:** (discovered 2026-11-17, ADV pass-1 remediation) Rust vocabulary
  from plugin templates (proptest, Send + Sync) leaked into 60+ Go spec files
  because templates were instantiated without a target-language pass.
- **Remedy:** Spec-producing steps that instantiate plugin templates include a
  target-language vocabulary check before the step completes; template trait and
  attribute names are translated to their target-language equivalents.
