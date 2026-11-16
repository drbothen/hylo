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
  - research/general-go-port-parity-crossplatform-2026-11-14.md
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

# Behavioral Contract BC-6.02.003: Case model: stdin template + translated settings + metrics mode + seeds + steps

## Description

A parity case is one directory that fully determines both runs. It holds:

- an stdin template whose paths are filled in from the per-case temp tree;
- settings declared once and translated into each side's own names;
- a metrics source, either a canned VictoriaMetrics reply or a failure mode;
- optional cache seeds;
- an optional transcript generator spec;
- an optional list of steps.

The harness materializes a case identically for the oracle and for Go. The only
differences are the ones the design prescribes: the env names and the cache
directory.

## Preconditions

1. A case directory contains:
   - `stdin.json.tmpl`, a JSON template whose placeholders (`{{.CaseDir}}`,
     `{{.ProjectDir}}`, `{{.Transcript}}`) are replaced with absolute per-case paths;
   - `case.json`, with
     `{now, tz?, columns?, settings, metrics, seed?, transcript?, steps?}`;
   - optionally `metrics.json`, a canned VictoriaMetrics `/api/v1/query` instant-vector
     reply;
   - optionally `seed/`, files copied verbatim into each side's cache directory before
     step 0;
   - optionally a transcript generator spec, consumed by the committed Go generator.
2. `settings` is a JSON object keyed by hylo config key name (S2 key registry), e.g.
   `backends[0].metrics_url`, `backends[0].model_prefixes`. Values are strings exactly
   as an operator would export them.
3. `metrics` is `"canned"` (serve `metrics.json`) or one of `"down"` (closed listener),
   `"500"` (HTTP 500) or `"garbage"` (non-JSON body). Timeout-based "slow" modes are not
   allowed (research Q3b: the legacy 1.5 s timeout makes them flaky).

## Postconditions

1. **Template rendering.** Both sides receive the identical rendered stdin bytes. They
   therefore see identical paths, and path-derived names such as the git cache key
   (`sha1(project_dir)[:16]`, SL:405-406) are equal on both sides.
2. **Settings translation.** Each case setting is emitted once per side:
   - Legacy side: the legacy env name, quoted as provenance from SL:73-79, 92 and 444
     (`DGX_SL_VM_URL`, `DGX_SL_TTL`, `DGX_SL_ROWS`, `DGX_SL_SPARK`, `DGX_SL_GIT`,
     `DGX_SL_TRACE`, `LOCAL_MODEL_PREFIXES`).
   - Go side: the key's HYLO_* env form (OD-05; no DGX_* on the Go side).
   - `backends[0].model_prefixes` is always emitted on both sides, even when the case
     does not set it. If the case leaves it unset, the harness emits the legacy
     production value `claude-sonnet`. A case that tests the unset-prefix behavior
     (`◨ ?`) sets an explicit empty value (OD-111; design T3).
3. **Untranslatable settings fail.**
   - A setting with no legacy counterpart fails the case with
     `parity: case <name>: setting <key> has no legacy equivalent`. Examples:
     `statusline.theme.*` at a non-default value, or `paths.cache_dir`, which the harness
     owns.
   - An unknown key fails the case.
4. **Out-of-domain values only in D4-EX-3 cases.** A value outside the Go key's typed
   domain is legal only when the case is listed under a `D4-EX-3` exclusion entry
   (BC-6.03.004). Examples: TTL `nan`, `4_0`, an unknown trace. Otherwise the harness
   fails with `parity: case <name>: <key>=<value> outside Go domain without D4-EX-3
   exclusion`.
5. **Metrics source.** One fake VictoriaMetrics server (`httptest`, DTU-3) per case
   serves both sides:
   - legacy reaches it through `DGX_SL_VM_URL`;
   - Go reaches it through `backends[0].metrics_url`;
   - the handler checks that the request path is `/api/v1/query`.
6. **Seeds.**
   - `seed/` files are copied byte for byte into the legacy cache dir
     (`<case-home>/.cache/dgx-llm/`) and into the Go cache dir (`<case>/hylo-cache/`)
     under the same file names.
   - A seeded `proc_start` in `statusline-<sid>.json` makes both sides skip the process
     probe (SL:273-275).
7. **Steps.** When `steps` is absent, the case is a single refresh at `now`. Otherwise
   each step may set `dt` (seconds added to the previous instant) or an absolute
   `now`, `append` (generator lines appended to the transcript), `stdin` (a replacement
   template) and `columns`. Steps run through the same runner as captured sessions
   (BC-6.02.002).
8. **Time zone.** `tz` defaults to `UTC`. Naive-timestamp cases run under the P1 pin
   set: `UTC`, `America/Chicago` and `Europe/London` (P5r5 §B.4).

## Invariants

1. A case is hermetic. Re-running it produces identical inputs to both sides on any OS
   (Windows root-path variants are BC-6.03.001's concern).
2. Settings are declared exactly once per case. No case carries a hand-written DGX_*
   or HYLO_* env list.
3. Git layouts (`.git` directory, worktree pointer file, detached HEAD) are created at
   test time from the case spec. A committed directory named `.git` would not be
   tracked as ordinary files (design §5.2).

## Edge Cases

| ID | Description | Expected Behavior |
|----|-------------|-------------------|
| EC-001 | Case sets `backends[0].model_prefixes` to `""` | Legacy gets `LOCAL_MODEL_PREFIXES=` (empty); Go gets the explicit empty list; both render `◨ ?` (SL:444) |
| EC-002 | Case omits `backends[0].model_prefixes` | Both sides get `claude-sonnet` explicitly; the legacy default `""` is never relied on |
| EC-003 | Case sets TTL `nan` and is not on the exclusion list | Harness FAIL (out-of-domain without D4-EX-3) |
| EC-004 | Case sets TTL `nan` and is a listed D4-EX-3 case | Runs. The Go output is checked against the case's expected file (config-error line), not against the oracle |
| EC-005 | `metrics: "slow"` | Harness FAIL: unknown metrics mode |
| EC-006 | Seed contains a legacy-written poisoned mix cache (BC-SL-100) | Copied to both sides; the reader behavior is compared (D4-EX-2 entries apply where listed) |
| EC-007 | Case sets a non-default `statusline.theme.sgr.*` value | Harness FAIL: no legacy equivalent. Theme overrides are tested by Go table tests only |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `case.json` `{now: 1794615009, settings: {"backends[0].model_prefixes": "claude-sonnet"}, metrics: "canned"}` + `stdin.json.tmpl` with `{{.Transcript}}` | Legacy env has `LOCAL_MODEL_PREFIXES=claude-sonnet` and `DGX_SL_VM_URL=<fake>`; Go env has the HYLO_* forms; identical rendered stdin | happy-path |
| `steps: [{dt: 2}, {dt: 18, append: <2 assistant lines>}]` | Three refreshes at `now`, `now+2`, `now+20`; compared after each | edge-case |
| `settings: {"statusline.telemetry.ttl_s": "4_0"}` with no exclusion entry | FAIL: `parity: case <name>: statusline.telemetry.ttl_s=4_0 outside Go domain without D4-EX-3 exclusion` (key name per the S2 registry, BC-2.01.004) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-TBD | For every committed case, the oracle and Go receive identical stdin bytes, clock, TZ and COLUMNS, and semantically equal settings | table test over the corpus loader |
| VP-TBD | Every setting key round-trips through the legacy/HYLO translation table, or the case is rejected | table test over the translation table |

## Traceability

| Field | Value |
|-------|-------|
| Source | design §5.2 case model (`stdin.json.tmpl`, settings declared once and translated, `metrics.json` or mode `down`/`500`/`garbage`, optional cache seed, transcript generator spec, `steps`; out-of-domain setting legal only in a D4-EX-3 case); design §3.2 (metrics, process start, cache dir seams); research Q3b; OD-05; OD-111; OD-123 (`backends[0].*` keys); legacy provenance `legacy/dgx_statusline.py` SL:73-79, 92, 444 (env reads), SL:273-275 (`proc_start` short-circuit), SL:405-406 (git cache key) |
| Parity class | n.a. (harness machinery) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/statusline/testdata/cases/`; harness case loader and fake VictoriaMetrics (filled by architect) |
| Stories | TBD (filled by story-writer) |

## Related BCs (Recommended)

- BC-6.01.002 — composes with: the translated settings become child env entries
- BC-6.02.002 — composes with: shared step runner
- BC-6.03.004 — depends on: D4-EX-3 exclusion entries permit out-of-domain settings
- BC-2.01.002 — related to: `backends[0].model_prefixes` default `claude-sonnet`
- BC-2.02.001 — related to: D4-EX-3 config-error line expected by out-of-domain cases

## Architecture Anchors (Recommended)

- TBD (filled by architect) — parity harness case model

## Story Anchor (Recommended)

TBD (filled by story-writer)

## VP Anchors (Recommended)

> Names provisional — architect (OD-145): harness flag names, the timing method, proposed
> test names and seed paths in this contract are delegated to the architect in
> create-architecture, subject to adversarial review. No behavior change.

- TBD — case materialization properties above
