---
document_type: behavioral-contract
level: L3
version: "1.2.16"
status: draft
producer: product-owner
timestamp: 2026-11-21T07:00:00Z
phase: 1a
inputs:
  - domain-spec/L2-INDEX.md
  - domain-spec/invariants.md
  - behavioral-contracts/BC-ALLOCATION.md
  - semport/hylo-legacy/statusline-target-design.md
  - research/general-go-port-parity-crossplatform-2026-11-14.md
  - owner-decisions-log-2026-11-14.md
input-hash: "70bf910"
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
  - "2026-11-18T00:00:00Z (1.2.3): ADV-P4 remediation D09+D11+D21 - argv minted handler-relative (design call 9, validator admits [] and [\"--subagent\"]); Bool settings translated by value (true=1/false=0); TZ=UTC pinned for both binaries on every leg (OD-171), windows leg unskipped"
  - "2026-11-18T22:00:00Z (1.2.4): pass-4 correction (item 10) - corpus root restored to the OD-148 home internal/statusline/testdata/parity/cases/ (fixtures stay with the subject package)"
  - "2026-11-18T23:30:00Z (1.2.5): pass-4 sync-check SC-11 — modified history re-spun oldest-first so the version field matches the last entry; no behavioral change"
  - '2026-11-19T00:10:00Z (1.2.6) ADV-P5 remediation D03+D21 — placeholder substitution only inside JSON string values with JSON-escaped path insertion (Windows \U/\t round-trip table test); Bool settings mapped by parsed value through the BC-2.01.005 grammar (operator strings, not JSON literals); outside-grammar Bool verbatim only in D4-EX-3 cases'
  - "2026-11-19T02:00:00Z (1.2.7): sync-check adv-p5 closure (SC-15) — 1.2.6 entry requoted single-quoted (the Windows path-escape spelling is not a YAML double-quoted-scalar escape); no behavioral change"
  - "2026-11-19T03:20:00Z (1.2.8): ADV-P6 remediation D05 / orchestrator call 3 — PC-8 gains the OD-76 disposition: the difference-table rows (America/Chicago repeated-DST hour, identical-row epochs) close the exclusion as Go table tests, never parity corpus cases; the corpus validator keeps rejecting non-UTC tz, so the corpus stays UTC-only"
  - "2026-11-19T17:00:00Z (1.2.9): ADV-P7 remediation D14+D17 - subagent cases identified by the ARCH-07 `subagent` case-id family, not a bare id suffix; stale 'architect to align ARCH-07' note closed (ARCH-07:135 already aligned); provenance SL:92 corrected to SL:89 (SL:92 is a comment); PC-8 LocalZone legs gain `empty` (five legs, BC-3.01.001 PC-6)"
  - "2026-11-19T21:00:00Z (1.2.10): ADV-P8 remediation D10 — PC-8 OD-76 closure widened: no D1-D4 corpus case at all (corpus UTC-only), matching BC-3.02.002 and orchestrator call 16"
  - "2026-11-20T12:30:00Z (1.2.11): pass-8 residual (C2-05 seam) - the metrics fake respelled: one fake VictoriaMetrics server per case is a raw net.Listener fake (DTU-3), not httptest, whose server canonicalises headers into a map and trims values; serving both sides unchanged"
  - "2026-11-20T18:30:00Z (1.2.12): ADV-P9 remediation D01+D12 (orchestrator calls 7+8) — PC-8 tail: exclusions.json carries NO OD-76 entry at all (rider-test closure); PC-6/PC-8 binding to the capture-replay seeding rule of BC-6.02.002 stated"
  - "2026-11-21T06:00:00Z (1.2.13): ADV-P10 remediation D01+D02+D04 (orchestrator calls 1, 2, 4) — PC-5 gains the run-time injection rule (DGX_SL_VM_URL / HYLO_BACKENDS_0_METRICS_URL always injected, case value wins on the Go side); PC-4 states the one subagent-family rule (id of the form subagent-<nnn>[-<variant>], argv [\"--subagent\"] for exactly that family; the erroneous '-sub shorthand' notation removed here and from the 1.2.9 entry); PC-6/PC-7 gain the every-sid seeding rule (fixed synthetic proc_start for EVERY session id any step's stdin uses; validator rejects a case whose step introduces an unseedable sid; no replay ever consults the real process tree)"
  - "2026-11-21T07:00:00Z (1.2.14): ADV-P11 remediation D02 (orchestrator call 3) + D01 (call 2) — PC-5: a case metrics URL wins on BOTH sides (oracle DGX_SL_VM_URL and hylo HYLO_BACKENDS_0_METRICS_URL get the same value), and the validator admits it only as a placeholder resolving to the fake server, optionally with a path suffix — one value per key, no non-fake URL (the 1.5 s timeout ban holds); PC-6: the canonical temp-file case cache-003 is named as the fake-table branch's first P1 consumer, its session-cache target intentionally unseeded"
  - "2026-11-22T00:00:00Z (1.2.15): ADV-P12 remediation D02 propagation (orchestrator call 2, superseding pass-11 call 2) - PC-6 hermeticity rule: the admission branch is the conditional fake PATH (EMPTY bin directory), not a fake process table; the cache-003 paragraph states the two-sided no-probe design (oracle FileNotFoundError at SL:293-294; Go child at HYLO_STATUSLINE_WINDOW_AGE_MAX_DEPTH=0)"
  - "2026-11-25T00:00:00Z (1.2.16): ADV-P14 remediation D11 (orchestrator call 17) — the stale 'fake-table branch' term respelled to the conditional fake PATH declaration (there is no fake process table, pass-12 call 2)"
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
     `{{.ProjectDir}}`, `{{.Transcript}}`) are replaced with absolute per-case paths.
     Placeholder substitution rule (ADV-P5-D03, owner call 9): a placeholder is
     substituted ONLY inside a JSON string value of the template, and the inserted
     path is JSON-escaped (backslashes and control bytes escaped per the JSON string
     grammar) before insertion — never spliced raw. A Windows table test proves a
     path containing `\U` and `\t` byte sequences round-trips (raw insertion would
     alter or invalidate the JSON, letting both sides decode `{}` and pass while
     testing nothing);
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
   ADV-P4-D09); subagent-family cases — a case of the `subagent` family of the ARCH-07
   case-id grammar, i.e. an id of the form `subagent-<nnn>[-<variant>]` — carry
   `["--subagent"]`: the validator gives argv `["--subagent"]` to exactly that family
   and to no other id shape (ADV-P10-D02, orchestrator call 2 — there is no `-sub`
   suffix rule; the former "-sub shorthand" notation was erroneous and is removed),
   exercising the `main_subagent` path
   (SL:1240) on both sides identically. Every other argv shape is Go-table-test
   territory (BC-4.01.002), never
   parity. The verb itself is never part of `argv` (ARCH-07's "full binary argv,
   default `["statusline"]`" reading is superseded; ARCH-07's case grammar is the
   aligned authority — pass-7 D17 closes the former "architect to align" note).

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
     registry type is `Bool` is translated to the legacy env BY PARSED VALUE, never
     name-only and never as a bare JSON literal: the operator-supplied string is parsed
     through the BC-2.01.005 Bool grammar (`true|1|yes` → true, `false|0|no` → false,
     byte-exact, case-sensitive, no trimming) and the legacy env receives `1` for the
     true family and `0` for the false family — legacy treats any value except `"0"`
     as on (SL:76-77), so emitting anything else verbatim would turn a Go-off case
     into a legacy-on run and fabricate a divergence (ADV-P5-D21). A value outside the
     six-string grammar is legal only in a `D4-EX-3` boolean-class case (PC 4), where
     the operator string passes verbatim to BOTH sides and the ruled config-error
     divergence is the scenario under test.
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
5. **Metrics source.** One fake VictoriaMetrics server (raw `net.Listener` — not httptest, whose server canonicalises headers into a map and trims values; DTU-3) per case
   serves both sides:
   - legacy reaches it through `DGX_SL_VM_URL`;
   - Go reaches it through `backends[0].metrics_url`;
   - **Run-time injection (ADV-P10-D01, orchestrator call 1; both-sides rule pass-11
     call 3).** The fake's port is only
     known at run time, so a case cannot declare it: the harness ALWAYS injects the fake
     server's URL into BOTH children — `DGX_SL_VM_URL=<fake>` for the oracle and
     `HYLO_BACKENDS_0_METRICS_URL=<same fake>` for Go (unconditional members of
     BC-6.01.002's exact key sets) — unless the case itself sets the metrics URL, in
     which case the case value is used on BOTH sides: the oracle's `DGX_SL_VM_URL` AND
     hylo's `HYLO_BACKENDS_0_METRICS_URL` get the same case value, so the two sides
     never query different servers. The validator admits a case metrics URL only as a
     PLACEHOLDER that resolves to the fake server (optionally with a path suffix) —
     never a routable non-fake URL, which would bring back the 1.5 s timeout flakiness
     Pre-3 bans — and one value per key;
   - the handler checks that the request path is `/api/v1/query`.
6. **Seeds.**
   - `seed/` files are copied byte for byte into the legacy cache dir
     (`<case-home>/.cache/dgx-llm/`) and into the Go cache dir (`<case>/hylo-cache/`)
     under the same file names.
   - A seeded `proc_start` in `statusline-<sid>.json` makes both sides skip the process
     probe (SL:273-275). Hermeticity rule (ADV-P2-D12 disposition; every-sid rule
     ADV-P10-D04, orchestrator call 4): the harness REJECTS a case that has an unseeded
     `proc_start` together with a truthy `session_id` unless the case declares the
     conditional fake `PATH` (an EMPTY `bin` directory; BC-6.01.002 PC-1; there is NO
     fake process table, pass-12 call 2) — without a seed or the empty-dir `PATH`,
     legacy's `ps` subprocess falls back
     to `os.defpath` (SL:280) and runs the runner's real `ps`, and Go's native probe
     reads the runner's real process tree, so the case would be machine-dependent. The
     seeding covers EVERY session id a case or capture uses: the harness seeds a fixed
     synthetic `proc_start` for every `session_id` that any step's stdin of the case or
     capture uses (a step's replacement stdin template may change the sid mid-sequence,
     e.g. `/clear`), and the case-load validator rejects a case whose step introduces a
     sid it cannot seed. NO replay ever consults the real process tree. The conditional fake
     `PATH` declaration's first P1 consumer is the canonical `temp-file` case
     `cache-003` (sid
     `../x`): its session-cache target stays INTENTIONALLY unseeded — seeding
     `statusline-../x.json` would create the directory `statusline-..`, legacy's
     `os.replace` would then succeed and no temp file would leak, defeating the case
     (pass-12 call 2) — and the declared empty-dir fake `PATH` satisfies the rule
     without a seed: the oracle's `ps` subprocess raises `FileNotFoundError` on the
     empty directory (caught at SL:293-294, no probe), and the Go child runs at
     `HYLO_STATUSLINE_WINDOW_AGE_MAX_DEPTH=0` (zero probes), so neither side reads the
     real process tree.
7. **Steps.** When `steps` is absent, the case is a single refresh at `now`. Otherwise
   each step may set `dt` (seconds added to the previous instant) or an absolute
   `now`, `append` (generator lines appended to the transcript), `stdin` (a replacement
   template) and `columns`. A step's replacement `stdin` template may introduce a NEW
   `session_id`; that sid is seeded exactly like the case's base sid (PC-6 every-sid
   rule, ADV-P10-D04). Steps run through the same runner as captured sessions
   (BC-6.02.002).
8. **Time zone.** The harness pins `TZ=UTC` for BOTH binaries on every leg (OD-171,
   ADV-P4-D21); the case schema keeps `tz?` for a later phase, but the P1 corpus
   validator rejects a non-UTC `tz` (documented limitation: POSIX-style TZ strings may
   differ between Go's zone loader and the MSVC runtime on Windows, so parity cases use
   `TZ=UTC` only). The windows-2025 leg therefore runs the naive local-time cases with
   NO skip (VP-026's `posix-only` tag removed by the architect; superseding the
   ADV-P2-D02 OS restriction). LocalZone's own verdicts (`TZ` unset / `UTC` / IANA name /
   `empty` / unparseable — the five legs BC-3.01.001 PC-6 lists) are Go table tests of
   `internal/platform` (BC-3.01.001 PC-6), never
   corpus cases. The OD-76 difference-table rows — including the America/Chicago
   repeated-DST hour and the identical-row epochs I1/I2, which are Chicago values
   (BC-3.02.002 Pre-3, CTV) — close the exclusion as GO TABLE TESTS run under
   `TZ=America/Chicago`, never parity corpus cases (orchestrator call 3, ADV-P6-D05):
   the repeated DST hour cannot exist in UTC, the corpus validator rejects non-UTC
   `tz` values, so the OD-76 closed-set entry's parity half carries NO D1-D4 case at all
   (widened from "no D1 case" by pass-8 D10 / orchestrator call 16 — D2-D4 work under UTC
   but never enter the corpus either) and the corpus stays UTC-only — ADV-P9-D01 /
   orchestrator call 7: with no case to name, `exclusions.json` carries no `OD-76` entry
   at all (PC-1 of BC-6.03.004 requires an entry's `case` to name an existing directory);
   the id is closed by its rider test alone. Capture replays (BC-6.02.002) follow this
   PC's seeding rule exactly as corpus cases do (ADV-P9-D12, orchestrator call 8).

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
| `case.json` `{now: 1794615009, settings: {"backends[0].model_prefixes": "claude-sonnet"}, metrics: "canned"}` + `stdin.json.tmpl` with `{{.Transcript}}` | Legacy env has `LOCAL_MODEL_PREFIXES=claude-sonnet` and `DGX_SL_VM_URL=<fake>`; Go env has the HYLO_* forms, including `HYLO_BACKENDS_0_METRICS_URL=<same fake>`; identical rendered stdin | happy-path |
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
| Source | design §5.2 case model (`stdin.json.tmpl`, settings declared once and translated — Bools by value, design call 11 — `metrics.json` or mode `down`/`500`/`garbage`, optional cache seed, transcript generator spec, `steps` inside `case.json`; out-of-domain setting legal only in a D4-EX-3 case); design §3.2 (metrics, process start, cache dir seams); research Q3b; OD-05; OD-111; OD-123 (`backends[0].*` keys); legacy provenance `legacy/dgx_statusline.py` SL:73-79, 89, 444 (env reads; the pass-6 provenance cited SL:92, a comment line — SL:89 is the env read, pass-7 D17), SL:273-275 (`proc_start` short-circuit), SL:405-406 (git cache key); handler-relative `argv` field and `subagent` case family (sync-check SC-03, pass-3 A03, OD-155/OD-168; design call 9, ADV-P4-D09); TZ=UTC harness pin (OD-171) |
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
