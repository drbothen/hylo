---
document_type: behavioral-contract
level: L3
version: "1.2.5"
status: draft
producer: product-owner
timestamp: 2026-11-17T22:00:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - domain-spec/invariants.md
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - research/general-go-port-parity-crossplatform-2026-11-14.md
  - owner-decisions-log-2026-11-14.md
input-hash: "b0c3890"
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
  - "1.2.2 2026-11-17T22:00:00Z: patch bump: case.json schema gains optional argv (+ subagent case family) per ARCH-07, sync-check SC-03"
  - "1.2.3 2026-11-18: ADV-P4 remediation D09+D11+D21 - argv minted handler-relative (design call 9, validator admits [] and [\"--subagent\"]); Bool settings translated by value (true=1/false=0); TZ=UTC pinned for both binaries on every leg (OD-171), windows leg unskipped"
  - "1.2.4 2026-11-18T22:00:00Z: pass-4 correction (item 10) - corpus root restored to the OD-148 home internal/statusline/testdata/parity/cases/ (fixtures stay with the subject package)"
  - "1.2.5 2026-11-18: pass-4 sync-check SC-11 — modified history re-spun oldest-first so the version field matches the last entry; no behavioral change"
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
     `{now, tz?, columns?, argv?, settings, metrics, seed?, transcript?, steps?}`;
   - optionally `metrics.json`, a canned VictoriaMetrics `/api/v1/query` instant-vector
     reply;
   - optionally `seed/`, files copied verbatim into each side's cache directory before
     step 0;
   - optionally a transcript generator spec, consumed by the committed Go generator.
2. `settings` is a JSON object keyed by hylo config key name (S2 key registry), e.g.
   `backends[0].metrics_url`, `backends[0].model_prefixes`. Values are strings exactly
   as an operator would export them. Every captured-session step declares its metrics
   source per step (BC-6.02.002 `metrics` key, ADV-P1-D18); the case-level `metrics`
   here is the default for generated cases.
3. `metrics` is `"canned"` (serve `metrics.json`) or one of `"down"` (closed listener),
   `"500"` (HTTP 500) or `"garbage"` (non-JSON body). Timeout-based "slow" modes are not
   allowed (research Q3b: the legacy 1.5 s timeout makes them flaky).
4. `argv` is an optional JSON array of strings: the case's **handler-relative argument
   list** — the arguments AFTER the `statusline` verb, both for the Go invocation
   (`hylo statusline <argv...>`) and for the oracle (`[python, -s, <script>] +
   <argv>`; BC-6.01.001 PC-5). Default `[]` (a plain `hylo statusline`). The P1 corpus
   validator admits only `[]` and `["--subagent"]` (orchestrator design call 9,
   ADV-P4-D09); subagent-family cases (id suffix `-sub`, ARCH-07 case grammar) carry
   `["--subagent"]`, exercising the `main_subagent` path (SL:1240) on both sides
   identically. Every other argv shape is Go-table-test territory (BC-4.01.002), never
   parity. The verb itself is never part of `argv` (ARCH-07's "full binary argv,
   default `["statusline"]`" reading is superseded — architect to align ARCH-07).

## Postconditions

1. **Template rendering.** Both sides receive the identical rendered stdin bytes. They
   therefore see identical paths, and path-derived names such as the git cache key
   (`sha1(project_dir)[:16]`, SL:405-406) are equal on both sides.
2. **Settings translation.** Each case setting is emitted once per side:
   - Legacy side: the legacy env name, quoted as provenance from SL:73-77, 89 and 444
     (`DGX_SL_VM_URL`, `DGX_SL_TTL`, `DGX_SL_ROWS`, `DGX_SL_SPARK`, `DGX_SL_GIT`,
     `DGX_SL_TRACE`, `LOCAL_MODEL_PREFIXES`; `DGX_SL_TRACE` is at SL:89).
   - Go side: the key's HYLO_* env form (OD-05; no DGX_* on the Go side).
   - **Bool value mapping (ADV-P4-D11, orchestrator design call 11):** a setting whose
     registry type is `Bool` is translated to the legacy env BY VALUE — `true` → `1`,
     `false` → `0` — never name-only: legacy treats any value except `"0"` as on
     (SL:76-77), so emitting the JSON literal `false` verbatim would turn a Go-off case
     into a legacy-on run and fabricate a divergence.
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
     probe (SL:273-275). Hermeticity rule (ADV-P2-D12 disposition): the harness REJECTS
     a case that has an unseeded `proc_start` together with a truthy `session_id` unless
     the case declares the fake process table (BC-3.02.002) — without a seed, legacy's
     `ps` subprocess falls back to `os.defpath` (SL:280) and runs the runner's real
     `ps`, and Go's native probe reads the runner's real process tree, so the case would
     be machine-dependent.
7. **Steps.** When `steps` is absent, the case is a single refresh at `now`. Otherwise
   each step may set `dt` (seconds added to the previous instant) or an absolute
   `now`, `append` (generator lines appended to the transcript), `stdin` (a replacement
   template) and `columns`. Steps run through the same runner as captured sessions
   (BC-6.02.002).
8. **Time zone.** The harness pins `TZ=UTC` for BOTH binaries on every leg (OD-171,
   ADV-P4-D21); the case schema keeps `tz?` for a later phase, but the P1 corpus
   validator rejects a non-UTC `tz` (documented limitation: POSIX-style TZ strings may
   differ between Go's zone loader and the MSVC runtime on Windows, so parity cases use
   `TZ=UTC` only). The windows-2025 leg therefore runs the naive local-time cases with
   NO skip (VP-026's `posix-only` tag removed by the architect; superseding the
   ADV-P2-D02 OS restriction). LocalZone's own verdicts (`TZ` unset / `UTC` / IANA name /
   unparseable) are Go table tests of `internal/platform` (BC-3.01.001 PC-6), never
   corpus cases.

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
| EC-007 | Case sets a non-default `statusline.theme.<role>` value | Harness FAIL: no legacy equivalent. Theme overrides are tested by Go table tests only |

## Canonical Test Vectors

| Input | Expected Output | Category |
|-------|----------------|----------|
| `case.json` `{now: 1794615009, settings: {"backends[0].model_prefixes": "claude-sonnet"}, metrics: "canned"}` + `stdin.json.tmpl` with `{{.Transcript}}` | Legacy env has `LOCAL_MODEL_PREFIXES=claude-sonnet` and `DGX_SL_VM_URL=<fake>`; Go env has the HYLO_* forms; identical rendered stdin | happy-path |
| `steps: [{dt: 2}, {dt: 18, append: <2 assistant lines>}]` | Three refreshes at `now`, `now+2`, `now+20`; compared after each | edge-case |
| `settings: {"statusline.telemetry.ttl_s": "4_0"}` with no exclusion entry | FAIL: `parity: case <name>: statusline.telemetry.ttl_s=4_0 outside Go domain without D4-EX-3 exclusion` (key name per the S2 registry, BC-2.01.004) | error |

## Verification Properties

| VP-NNN | Property | Proof Method |
|--------|----------|-------------|
| VP-009 | For every committed case, the oracle and Go receive identical stdin bytes, clock, TZ and COLUMNS, and semantically equal settings | table test over the corpus loader |
| VP-009 | Every setting key round-trips through the legacy/HYLO translation table, or the case is rejected | table test over the translation table |

## Traceability

| Field | Value |
|-------|-------|
| Source | design §5.2 case model (`stdin.json.tmpl`, settings declared once and translated — Bools by value, design call 11 — `metrics.json` or mode `down`/`500`/`garbage`, optional cache seed, transcript generator spec, `steps` inside `case.json`; out-of-domain setting legal only in a D4-EX-3 case); design §3.2 (metrics, process start, cache dir seams); research Q3b; OD-05; OD-111; OD-123 (`backends[0].*` keys); legacy provenance `legacy/dgx_statusline.py` SL:73-79, 92, 444 (env reads), SL:273-275 (`proc_start` short-circuit), SL:405-406 (git cache key); handler-relative `argv` field and `subagent` case family (sync-check SC-03, pass-3 A03, OD-155/OD-168; design call 9, ADV-P4-D09); TZ=UTC harness pin (OD-171) |
| Parity class | n.a. (harness machinery) |
| L2 Capability | CAP-009 |
| L2 Domain Invariants | DI-012 |
| Architecture Module | `internal/statusline/testdata/parity/cases/`; harness case loader and fake VictoriaMetrics (BC-COMPONENT-MAP: internal/parity/case.go (case model) — ARCH-07) |
| Stories | TBD (filled by story-writer) |

> Capability anchor rationale (OD-153): the parity harness is verification machinery whose sole purpose is proving CAP-009 byte parity (the D4 exit criterion), governed by DI-012.

## Related BCs (Recommended)

- BC-6.01.002 — composes with: the translated settings become child env entries
- BC-6.02.002 — composes with: shared step runner
- BC-6.03.004 — depends on: D4-EX-3 exclusion entries permit out-of-domain settings
- BC-2.01.002 — related to: `backends[0].model_prefixes` default `claude-sonnet`
- BC-2.02.001 — related to: D4-EX-3 config-error line expected by out-of-domain cases

## Architecture Anchors (Recommended)

- `architecture/ARCH-07-parity-harness.md` — internal/parity/case.go (case model) (parity harness case model) (BC-COMPONENT-MAP: ARCH-07 (ARCH-07-parity-harness.md))

## Story Anchor (Recommended)

TBD (filled by story-writer)

## VP Anchors (Recommended)

> Names provisional — architect (OD-145): harness flag names, the timing method, proposed
> test names and seed paths in this contract are delegated to the architect in
> create-architecture, subject to adversarial review. No behavior change.

- VP-009 — case materialization properties above

#### Purity Classification

| Property | Assessment |
|----------|-----------|
| **I/O operations** | spawns interpreters/builds; replay corpus and cache-swap I/O |
| **Global state access** | builds the child environment from scratch |
| **Deterministic** | stepped clock; seeded synthetic corpus |
| **Thread safety** | test-only, single-shot |
| **Overall classification** | infrastructure |

Owning component `internal/parity` (BC-COMPONENT-MAP: par/case.go (case model) - ARCH-07); the ARCH-00 package table classifies the package infrastructure - spawns interpreters/builds; test-only, never shipped in the render path.
