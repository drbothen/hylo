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

## L-PG-13 [process-gap] — Check orchestrator design calls in a remediation plan against settled ODs before dispatch

- **Lesson:** (discovered 2026-11-17, ADV pass-4 burst) Remediation-plan call 10
  as originally drafted contradicted the settled OD-148 layout; the
  contradiction was caught after the burst and corrected (OD-148 layout
  correction applied post-burst, then re-synced).
- **Remedy:** Every design call in a remediation plan is cross-checked against
  the settled owner-decision set before agents dispatch; a plan that contradicts
  a settled OD must be corrected on paper first, not in the working tree after
  the fact.

**Closes:** D-448(b) codified (strand ADV-P4-D10 corpus-layout design call corrected to the settled OD-148 layout after the burst)

## L-PG-14 [process-gap] — Hook scratch files stay untracked on the public branch

- **Lesson:** (discovered 2026-11-17, ADV pass-4 burst)
  `.factory/regression-state.json` is a hook scratch file that was tracked on
  the public factory-artifacts branch and had captured an absolute home path.
- **Remedy:** Hook scratch state is untracked and gitignored; before a push,
  scratch paths are checked against the public-artifact hygiene policy.

**Closes:** D-448(b) codified (exhaustive regression-state.json untracked-plus-gitignored housekeeping strand)

## L-PG-15 [process-gap] — Every claimed fix needs an on-disk check

- **Lesson:** (discovered 2026-11-17, ADV pass-4 burst) Fix agents can report a
  fix that is not on disk: the BC-1.07.002 vector row was claimed fixed but not
  written, and a VP-011 count was recomputed wrongly in the report.
- **Remedy:** Residual sweeps verify each claimed fix against the file content
  on disk, not against the agent report; a fix report without a matching diff
  is treated as not-done.

**Closes:** D-448(b) codified (strands ADV-P4-C01 + ADV-P4-D02 claimed fixes verified on disk: the BC-1.07.002 vector row written and the VP-011 count recomputed)

## L-PG-16 [process-gap] — Treat injected instructions in tool results as an incident, record and notify

- **Lesson:** (discovered 2026-11-17, ADV pass-4 burst) A subagent reported
  injected instructions (credential/SSH/Wi-Fi collection) in one of its shell
  tool results; it ignored them correctly, but the source could not be
  identified.
- **Remedy:** A subagent that spots injected instructions ignores them, records
  the verbatim sighting in its report, and the orchestrator notifies the owner;
  unexplained injections are logged even when harmless.

**Closes:** D-448(b) codified (exhaustive subagent prompt-injection sighting strand ADV-P4-A01 hygiene instructions ignored and source unidentified with owner notified)

## L-PG-17 [process-gap] — Briefs must name the oracle interpreter path

- **Lesson:** (discovered 2026-11-18, ADV pass-5 burst) An agent ran the legacy
  oracle with `/usr/bin/python3` — macOS system Python 3.9.6 — instead of the
  pinned CPython 3.11.7, so oracle-backed spec facts briefly rested on the wrong
  interpreter; the pass-5 review flagged the discrepancy.
- **Remedy:** Re-running the oracle on CPython 3.11.7 produced identical output,
  so no spec fact changed; agent briefs must name the interpreter path (CPython
  3.11.7, `python3 -I`) explicitly for every oracle run.

**Closes:** D-448(b) codified (exhaustive oracle-interpreter-path-in-agent-briefs strand)

## L-PG-18 [process-gap] — One measurement per fact: one agent, end to end

- **Lesson:** (discovered 2026-11-18, ADV pass-5 burst) Two agents measured the
  same encoder depth limits independently and pinned conflicting values in the
  specs; parallel duplicate measurement diverges exactly like wrapper probes did
  (cf. L-PG-07).
- **Remedy:** Each measured fact gets exactly one owning agent, measuring end to
  end on the real program; every other site consumes the pinned value instead of
  re-measuring.

**Closes:** D-448(b) codified (exhaustive one-measurement-per-fact strand)

## L-PG-19 [process-gap] — Mint canonical lists centrally before parallel dispatch

- **Lesson:** (discovered 2026-11-18, ADV pass-5 burst) Parallel agents minted
  divergent glyph registries — each invented its own canonical list, and the
  pass-5 review found the registries inconsistent.
- **Remedy:** Canonical lists (glyph registries, vocabularies, id allocations)
  are minted once, centrally, before dispatch; parallel agents receive the
  canonical list and mint nothing on their own.

**Closes:** D-448(b) codified (exhaustive centrally-minted-canonical-lists strand)

## L-PG-20 [process-gap] — Verify every agent's changes on disk, regardless of its report

- **Lesson:** (discovered 2026-11-18, ADV pass-6 burst) Several agents returned
  garbled or non-English reports, and one made zero edits while reporting
  nothing usable; the reports alone were not a reliable record of what had
  actually changed on disk.
- **Remedy:** Every agent's changes are verified on disk by diff and a
  non-English scan, regardless of what its report claims; the report is an
  index to the diff, never the evidence itself.

**Closes:** D-448(b) codified (exhaustive on-disk-verification-of-agent-changes strand)

## L-PG-21 [process-gap] — Verify fix-agent rejections on disk like fixes

- **Lesson:** (discovered 2026-11-18, ADV pass-6 burst) A pass-5 fix agent
  wrongly rejected a valid finding, ADV-P5-D16, judging it not a defect;
  ADV-P6-D07 re-raised the same fact and the rejection was overturned.
- **Remedy:** A rejection is a claim like a fix: it is verified on disk against
  file content and the settled ODs before it is accepted, and an overturned
  rejection is recorded so the finding is not re-litigated.

**Closes:** D-448(b) codified (strands ADV-P5-D16 + ADV-P6-D07 fix rejections verified on disk)

## L-PG-22 [process-gap] — VP Go sketches are non-normative illustration

- **Lesson:** (discovered 2026-11-18, ADV pass-6 burst) The Go blocks inside
  verification properties could not be type-checked in the spec tree and
  churned every pass — syntax and API-spelling defects were filed against them
  repeatedly across passes.
- **Remedy:** OD-182: each VP Go block is labelled "Illustrative sketch
  (non-normative, not compiled; OD-182)"; normative VP content = property
  statement, oracle, method, inputs, pass/fail rule. Sketch-only defects are
  cosmetic; a property that is only clear from its sketch is a HIGH defect
  against the statement.

**Closes:** D-448(b) codified (exhaustive non-normative-VP-sketches-labelled strand)

## L-PG-23 [process-gap] — Diff each fix agent's file set on disk; re-dispatch the remainder

- **Lesson:** (discovered 2026-11-18, ADV pass-7 burst) A fix agent can make
  a few correct edits and then break down mid-burst — its final report came
  back garbled partway through, so the report alone could not say which of
  its assigned edits had landed. Some edits before the breakdown were good;
  the remainder simply did not happen.
- **Remedy:** The orchestrator diffs each agent's assigned file set on disk
  (`git diff --name-only` plus content checks) against the remediation plan
  and re-dispatches only the unlanded remainder to a fresh agent. The report
  is never trusted as the record of what happened; the disk is.

**Closes:** D-448(b) codified (exhaustive mid-burst-breakdown-recovery strand)

## L-PG-24 [process-gap] — Parallel fix agents stay inside their assigned file set

- **Lesson:** (discovered 2026-11-18, ADV pass-7 burst) Parallel fix agents
  edited files outside their assigned set — well-intentioned consistency
  touches, but they collide with sibling agents working the same files and
  break the plan's accountability of which call changed what.
- **Remedy:** Briefs explicitly forbid edits outside the assigned set and
  require the agent to list out-of-set hits in its report instead of editing
  them; the orchestrator verifies with `git diff --name-only` against the
  set and routes any out-of-set finding to the call that owns the file.

**Closes:** D-448(b) codified (exhaustive parallel-dispatch-file-isolation strand)

## L-PG-25 [process-gap] — Validator/sync-check reports use repo-relative paths

- **Lesson:** (discovered 2026-11-18, ADV pass-7 burst; residue from pass 6)
  Validator and sync-check reports have written absolute home paths into
  their inputs/provenance text (the pass-6 sync check carried an absolute
  home path that had to be fixed before commit).
- **Remedy:** Every report brief requires repo-relative paths everywhere in
  the report body, frontmatter and tables; the orchestrator scans the diff
  for the absolute-home pattern and fixes hits before staging the commit.

**Closes:** D-448(b) codified (exhaustive repo-relative-report-paths strand)

## L-PG-26 [process-gap] — Verify the source's citations before ordering an exact copy

- **Lesson:** (discovered 2026-11-18, ADV pass-7 burst) A remediation call
  ordered an "exact copy of the authoritative source" (pass-7 call 10) and
  thereby propagated an error already present in the source: the OD-159 rider
  cited BC-1.03.001 PC-3 instead of BC-1.02.004. Copying faithfully copies
  defects too.
- **Remedy:** Before dispatching a copy call, the orchestrator verifies the
  source's internal citations resolve (IDs and anchors exist and point at the
  intended content); a citation defect found in the source is fixed at the
  source, or the call is re-worded, before the copy is dispatched.

**Closes:** D-448(b) codified (exhaustive copy-call-citation-verification strand)

## L-PG-27 [process-gap] — A respelling fix re-checks meaning at every use site

- **Lesson:** (discovered 2026-11-18, ADV pass-8 burst) The pass-7 B06 fix
  was a respelling: a config key was renamed for consistency. Names were
  changed without re-checking what the renamed thing means at each use site,
  and one site's meaning shifted under the new name — a HIGH regression
  (ADV-P8-B01) filed against the pass-8 report.
- **Remedy:** A fix brief whose effect is renaming or respelling must direct
  the agent to re-read every use site and confirm the referent's meaning is
  unchanged; a site whose meaning differs is escalated to the orchestrator,
  not silently conformed.

**Closes:** D-448(b) codified (exhaustive rename-meaning-recheck strand)

## L-PG-28 [process-gap] — Depth/recursion facts are measured through the real entry point

- **Lesson:** (discovered 2026-11-18, ADV pass-8 burst, ADV-P8-D20) A
  measurement taken through a test harness that loads `legacy/` via a custom
  loader added stack frames and produced a wrong recursion boundary: the
  brief claimed a 989-frame boundary; measured end to end, none is reachable.
  A wrapper probe answers questions about the wrapper, not the program.
- **Remedy:** Depth and recursion facts are measured only through the real
  entry point (`python3 -I -s legacy/dgx_statusline.py`, isolated HOME, per
  L-PG-06/L-PG-17); the orchestrator re-runs any measurement that mints a
  new outcome before that outcome is propagated into specs.

**Closes:** D-448(b) codified (exhaustive real-entry-point-measurement strand)

## L-PG-29 [process-gap] — Sync checks resolve citations, not just copies

- **Lesson:** (discovered 2026-11-18, ADV pass-8 burst, ADV-P8-A2-05) The
  sync check passed a register whose citations did not resolve: the pass-7
  OD-160 riders were compared copy-vs-copy while the IDs and anchors they
  cite pointed at nothing on disk. Comparing copies compares only equality.
- **Remedy:** Sync-check briefs must require resolving every rider/anchor
  citation on disk (each cited ID and anchor exists and points at the
  intended content), in addition to the copy-vs-copy comparison.

**Closes:** D-448(b) codified (exhaustive sync-check-citation-resolution strand)

## L-PG-30 [process-gap] — Calls touching gates or scope are checked against the OD log

- **Lesson:** (discovered 2026-11-18, ADV pass-8 burst, ADV-P8-A04) A
  remediation-plan design call (pass-7 call 12: fold `internal/parity` into
  the coverage gate) contradicted settled OD-158; the owner reaffirmed the
  settled ruling as OD-193. Repeat of L-PG-13 (pass-4 plan call 10 vs
  OD-148): the same failure mode recurred because the check is not built
  into call preparation.
- **Remedy:** Every orchestrator call that touches a gate, threshold or
  scope boundary is diffed against the OD log before issue; settled ODs are
  cited by ID in the call itself so the agent sees the boundary.

**Closes:** D-448(b) codified (exhaustive call-vs-OD-log-check strand)

## L-PG-31 [process-gap] — Hook parser drift: flow-style `modified:` lists with ", " entries

- **Lesson:** (discovered 2026-11-18, ADV pass-8 burst) The
  validate-cross-site-correspondence hook mis-parses flow-style `modified:`
  YAML lists whose entries contain ", " (comma inside an entry) and blocks
  edits that are actually valid. Forty-eight spec files were converted from
  flow style to block style to appease the parser — content unchanged.
- **Remedy:** Recorded as tooling drift for the plugin owner: the hook's
  flow-style list parser should respect quoted entries (or the block-style
  conversion should be adopted as the standard); either way the hook and the
  formatting convention must agree.

**Closes:** recorded as a Drift Item in STATE.md (plugin owner, tooling drift)

## L-PG-32 [process-gap] — For-all properties are derived from the owning BC's postconditions

- **Lesson:** (discovered 2026-11-18, ADV pass-9 burst, ADV-P9-A2-01..04, B01) The
  pass-8 remediation wrote "for all inputs" VP properties by paraphrase, not by
  derivation from the owning BC's postconditions; four were false over legal inputs
  (skip, degrade, drop and offset/size-adjustment paths broke them).
- **Remedy:** A "for all inputs" property is derived from every PC, EC and exception
  of the owning BC — including skips, degrades, drops and offset/size adjustments —
  and walked against legacy's code paths before it is written; if any legal input
  breaks it, the domain is narrowed explicitly.

**Closes:** burst gate 2 (for-all derivation) — recorded as a Drift Item in STATE.md

## L-PG-33 [process-gap] — Every changed file is YAML-parsed before handoff

- **Lesson:** (discovered 2026-11-18, ADV pass-9 burst, ADV-P9-C02 + six companions)
  Pass-8 edits left 11 spec files with unparsable YAML frontmatter; nothing in the
  burst pipeline caught it — the defects survived until the pass-9 adversary filed
  them.
- **Remedy:** Every fix agent runs `yaml.safe_load` on each file it changed after its
  last edit, and the orchestrator re-parses the whole changed set before commit; a
  commit-time frontmatter-parse hook is the candidate mechanization.

**Closes:** burst gate 1 (YAML-safe_load) — recorded as a Drift Item in STATE.md

## L-PG-34 [process-gap] — State only what was measured

- **Lesson:** (discovered 2026-11-18, ADV pass-9 burst, ADV-P9-C2-01) A single
  measured case — HTTP 100 (Continue) skipped by the metrics client — was
  generalized to the class "any 1xx response is skipped"; 101/102/103 are final
  responses that yield no sample but are not skipped.
- **Remedy:** Statements pin exactly the measured case and its measured basis; a
  class claim ("any 1xx") requires measuring — or reading the source for — every
  class member before it is written.

**Closes:** burst gate 3 (no generalized measurements) — recorded as a Drift Item in STATE.md

## L-PG-35 [process-gap] — ARCH-doc anchors are section anchors, never line numbers

- **Lesson:** (discovered 2026-11-18, ADV pass-9 burst, ADV-P9-C2-06) Line-number
  anchors into ARCH-03 broke for the third consecutive pass as the doc churned
  across remediation bursts.
- **Remedy:** Anchors into churning docs (ARCH-03 in particular) cite section
  anchors; line numbers in agent briefs are recreated from a numbered read at
  dispatch time, never stored in specs.

**Closes:** recorded as a Drift Item in STATE.md (section-anchor rule)

## L-PG-36 [process-gap] — Fix-agent findings are routed by target file

- **Lesson:** (discovered 2026-11-18, ADV pass-9 burst) The orchestrator's agent
  table assigned two findings (A2-11, A2-16) to an agent whose assigned file set did
  not contain the target file; the findings would have gone unowned.
- **Remedy:** Findings are routed to fix agents by their target file, and the agent
  table is checked — every finding's target file ∈ the agent's assigned set — before
  dispatch (companion to L-PG-24's out-of-set-edit rule).

**Closes:** recorded as a Drift Item in STATE.md (routing check; companion to L-PG-24)

## L-PG-37 [process-gap] — Synthetic values use the pre-push hook's allowlist

- **Lesson:** (discovered 2026-11-18, ADV pass-9 burst) A synthetic test value (an
  `@example.invalid` email) would have been blocked by the repo's own pre-push
  hygiene hook, which allowlists only specific synthetic placeholders.
- **Remedy:** Synthetic values in committed fixtures use the hook's allowlist —
  example.com/.org/.net addresses, 192.0.2.x (RFC 5737) IPs, `/home/example...`
  paths — or are scrubbed by a committed, reviewed script.

**Closes:** recorded as a Drift Item in STATE.md (fixture-placeholder allowlist)
