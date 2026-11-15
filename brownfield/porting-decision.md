---
artifact_type: brownfield-porting-decision
source_language: "Python 3 (CPython 3.12.10 proxy/preflight, 3.11.7 status line/hook/backfill, 3.9.6 exporter; stdlib-only) plus a zsh 5.9 launcher"
target_language: "Go — go.mod floor `go 1.26.0` (project floor 'Go >= 1.26' per docs/CLAUDE.md; research rec Q1: go 1.26.0 + toolchain go1.27.4); standard library first"
needs_semport: true
porting_scope: modules # P1 only: hylo statusline + its parity harness; not the full codebase
decided_at: 2026-11-15
producer: architect
workflow_step: detect-cross-language-porting (workflows/brownfield.lobster:252)
cycle_scope: "Phase 1 spec work, P1 only (market-intel GO approved by owner 2026-11-15)"
inputs:
  - docs/PLAN.md
  - docs/RESUME.md
  - .factory/semport/hylo-legacy/hylo-legacy-pass-8-deep-synthesis.md
  - .factory/specs/owner-decisions-log-2026-11-14.md
  - .factory/specs/research/general-go-port-parity-crossplatform-2026-11-14.md
  - .factory/planning/market-intel.md
input-hash: "76a999d"
---

# Porting decision — Python/zsh to Go

Brownfield step `detect-cross-language-porting` (architect, 2026-11-15). This document records
whether the port needs semantic-porting analysis (`needs_semport`), and maps the whole program
port so every later semport step can see what is in and out of scope for the current cycle.

## 1. Decision

| Field | Value | Basis |
|---|---|---|
| Port requested? | **Yes — explicit, owner-requested** | docs/PLAN.md approved 2026-11-14: "rewrite it in **Go**" (preamble); docs/CLAUDE.md: "hylo is a public Go project … being ported from a working Python prototype (`legacy/`)"; the owner asked for "the Python→Go translation plan" as the next spec step (this cycle's task) |
| `source_language` | Python 3 + zsh 5.9 launcher | Component interpreters: CPython 3.12.10 (proxy, preflight), 3.11.7 (status line, hook, backfill), 3.9.6 (exporter oracle, per OD-15); zsh 5.9 launcher (pass-8 §2.8) |
| `target_language` | Go | D1 (docs/PLAN.md §2: Go module `github.com/drbothen/hylo`, binary `hylo`); floor per docs/CLAUDE.md ("Go ≥ 1.26") and research Q1 (go.mod `go 1.26.0`, CI on 1.26.x + 1.27.x) |
| `needs_semport` | **true** | Byte-parity port of 137 byte-exact BCs across a language boundary with 22 catalogued Python-behavior pitfalls (pass-8 §1 finding 1, §5 rank 2; market-intel risk R3) — translation-strategy analysis is required, not optional |
| `porting_scope` | **modules** — P1 only | docs/PLAN.md §7 P1 row; docs/RESUME.md "Next phase: P1 — Go skeleton + `hylo statusline` at parity"; market-intel frontmatter `scope: P1 (hylo statusline) only` |

## 2. Migration signal (why this is a port, not a rewrite)

- The whole program is a language migration by plan: "Phase 1 is scoped to P1 = `hylo statusline`
  at byte parity" (this cycle's owner instruction); PLAN D4 makes parity the definition of done
  ("port to Go with identical behavior, validate against the Python version, *then* generalize").
- The source is frozen and read-only: `legacy/` is the scrubbed post-review prototype; the status
  line to port is the post-2026-11-13-review version, "port it, not an earlier one" (docs/RESUME.md
  "How we got here"). `legacy/` stays runnable until cutover for the parity harness (D10).
- Market-intel gate: **GO** for P1 approved 2026-11-15, with feature_type = cli (no design-system
  extraction) and README positioning deferred to P6 (market-intel §6.3; owner gate this cycle).

## 3. Program-level map — every `legacy/` file, its hylo target and phase

Whole-port visibility per docs/PLAN.md §4 ("Scope — what moves, and what each becomes") and §7
(phases). **IN SCOPE** marks the current Phase 1 cycle; everything else is OUT OF SCOPE for this
cycle but remains in the program map.

| legacy/ source (lines) | Becomes in hylo | Phase | This cycle |
|---|---|---|---|
| `legacy/dgx_statusline.py` (1,245; 742 stmts) | `hylo statusline` → `cmd/hylo` dispatch + `internal/statusline` | **P1** | **IN SCOPE** (minus `--subagent`, §4.1) |
| Parity harness (new; PLAN §8; RESUME step 3) | fixture corpus + pinned CPython oracle + clock shim + fake metrics store | **P1** | **IN SCOPE** (§4.4) |
| Go skeleton + CI matrix (RESUME steps 1–2) | `go.mod`, `cmd/hylo` dispatch, `.github/workflows/ci.yml` (3 OSes) | **P1** | **IN SCOPE** |
| `legacy/dgx_ledger_exporter.py` (414) | `hylo exporter` → `internal/ledger` (exporter) | P2 | OUT OF SCOPE |
| `legacy/deploy/*.plist` (2 LaunchAgents + `ssh -R` tunnel) | per-OS service units in `internal/platform`; tunnel documentation only | P2 (SV BCs per pass-8 §8.1) | OUT OF SCOPE |
| `legacy/dgx_proxy.py` (764) | `hylo proxy` → `internal/proxy`, `internal/ledger` (writer), `internal/events` | P3 | OUT OF SCOPE |
| `legacy/.mitmenv` venv (mitmproxy 12.3.1 runtime; absent from tree, OD-47) | `internal/proxy` (transport) + `internal/ca` | P3 | OUT OF SCOPE |
| `legacy/dgx-proxy-coordinator.sh` (50; unwired) | built into `hylo proxy` / `hylo run` (state file + lock, OD-19) | P3/P4 | OUT OF SCOPE |
| `legacy/claude-dgx` (zsh launcher, 185) | `hylo run` (+ config profiles) | P4 | OUT OF SCOPE |
| `legacy/auto_continue.py` (275) | `hylo hook stop` → `internal/hook` | P4 | OUT OF SCOPE |
| `legacy/dgx_preflight.py` (41) | `hylo doctor` → `internal/platform` | P4 | OUT OF SCOPE |
| `legacy/tools/backfill_cost_history.py` (121) | `hylo cost backfill` | P6 (OD-36; see §4.5) | OUT OF SCOPE |
| `web/` React UI + `hylo top` (new, D16) | `internal/ui`, `web/` | P4 (ui) / P6 (top) | OUT OF SCOPE |
| Docs: `STATUSLINE-WIDGETS.md`, `STATUSLINE-REVIEW-2026-11-13.md`, `ROLLBACK.md` | `docs/` reference | P0 done / ongoing | reference only |
| `opus_router.py` (visible mode, 230; removed in scrub) | history only (D6) | dropped | OUT OF SCOPE |

Phase BC distribution for the whole port: 232 BCs = P1 103, P2 28, P3 44, P4 39, unscheduled 13
(pass-8 §9.3, §8.1; registers P3r4 §7 + r5–r8).

## 4. P1 in-scope detail

### 4.1 Source files and functions in scope

Exactly one legacy source file is ported this cycle: **`legacy/dgx_statusline.py`** (1,245 lines,
742 statements; pass-8 §5 rank 2), minus the `--subagent` mode. Function-family inventory (BCs
and feature IDs from pass-8 §3.4 F-SL-01..F-SL-15; source lines from research §2b):

1. **Guard and degraded ladder** — any exception → 29-byte degraded line, exit 0; import-time env
   crash excepted (BC-SL-001, -087; F-SL-01; research pitfall P27).
2. **Stdin, width grammar, trim** — strict stdio, invalid stdin → `{}`; `COLUMNS` grammar; row 2
   iff `ROWS >= 2` and width rule; trim to code-point visible width after SGR strip
   (`visible()` SL:153, `trim_to_fit` SL:1195) (BC-SL-002..005, -054, -055, -076, -090; F-SL-02/03).
3. **Row 1 widgets** — lane pill, model, project, branch (git cache, TTL 5 s, SL:402-411); context
   thermometer, composition percentages (banker's `round`, SL:1171), cache-hit; plan-limit windows
   with pace, absolute colour bands, countdown, 1.15 gate, smoothing; lines, timer, API time,
   window age `⌂` (process-ancestry walk, SL:278-295); tokens, `$`, `$/h`, pick (displaced cost),
   mine (last turn) (BC-SL-006..027, -038, -056..064, -071, -080..083, -085, -093, -096; F-SL-04..08).
4. **Cost history and percentile colouring** — read + p75/p95 colours (SL:217-237)
   (BC-SL-028, -029, -079, -101, -102; F-SL-09).
5. **Transcript parser** — incremental; 512 KB read window, long-line completion, `splitlines`
   (SL:1059), message-id dedup (last 256), rebuild counter at 20,000 excess, compaction reset,
   turn machine (BC-SL-030..039, -065..067, -069, -072, -088, -094, -095; F-SL-10).
6. **Row 2 telemetry** — VictoriaMetrics fetch with TTL and KEEP_DEAD (SL:168-184), history
   points, freshness ladder, health dot, queue, KV, throughput, sparkline, TTFT p95, power,
   idle `☾`, pick `⛏` (BC-SL-040..051, -053, -073..075, -084, -086, -091, -092; F-SL-11).
7. **Four cache writers in the exact legacy format** — session (raw sid in name, SL:190-206), mix
   (`mixv6` marker, sanitized sid, SL:999-1153), git, cost-history; atomic writes, side-effect
   order (BC-SL-052, -070, -077, -078; F-SL-12; pass-8 §8.2 item 5).
8. **Approved-difference edges inside the parity phase** — D4-EX-2: skip wrong-shape transcript
   lines like invalid JSON (BC-SL-098/099 replacing BC-SL-068; 21 table tests; OD-21, OD-32
   edges; BC-SL-103 poisoned-cache reader rule) (F-SL-13); D4-EX-1: `⌂` allowed on Windows
   (BC-SL-023/080) via `internal/platform.ProcessStart` (L1-04).
9. **Goldens** — row goldens A/B/C (BC-SL-089), cost-colour goldens (BC-SL-101), trim breakpoints
   (BC-SL-090) (F-SL-15; pass-8 §8.2 item 7).

**Excluded from the file port:** `--subagent` rows and `subagentStatusLine` (SL:845-936,
BC-SL-097; OD-14 ruled "do not port"; docs/RESUME.md "not ported"; market-intel §6.2 item 2).
The legacy CLI flag may remain recognized-but-unported only if the P1 spec says so; default is
not ported.

### 4.2 Go packages they land in (docs/PLAN.md §6 layout)

| Package | P1 content |
|---|---|
| `cmd/hylo` | subcommand dispatch (`hylo statusline`, `hylo version`), stdlib `flag` (RESUME step 1) |
| `internal/statusline` | the port target: widgets, parser, caches, telemetry client (PLAN §6; pass-8 BC7/BC8 rows) |
| `internal/config` | P1 subset of the registry: the 62 status-line CFG rows plus `LOCAL_MODEL_PREFIXES`, `COLUMNS`, env grammar (pass-8 §8.2 item 3; D15; OD-01/OD-05 typing) |
| `internal/platform` | `ProcessStart` per-OS ancestry (macOS sysctl / Linux `/proc` / Windows Toolhelp32; D4-EX-1, L1-04, research Q4a); explicit paths (OD-95) |
| `internal/pyfmt`, `internal/pyjson`, `internal/pystr`, `internal/pytime` | Python-semantics parity helpers **before any widget**: banker's round, CPHP float `//`/`%`, NaN-ordering max/min, `repr(float)`, `json.dumps` length (63-case oracle BC-SL-096), code-point len/slice, lenient `fromisoformat` (pass-8 §1 finding 1, §8.2 item 2, L1-01; market-intel risk R3 mitigation; research Q2) |
| `internal/statusline/testdata/` + harness tree | synthetic fixtures, pyhooks clock shim, fake VictoriaMetrics (DTU-3), goldens (RESUME steps 3–4; research Q3) |

Dependency budget P1: zero non-stdlib runtime dependencies except `golang.org/x/sys` for the
window-age probe (research Q5; Q4a).

### 4.3 Behavioral contracts P1 must satisfy

- **BC-SL family: 103 BCs** (BC-SL-001..BC-SL-103; composition 97 BX + 4 D4-EX-2 + 2 OD — pass-8
  §5 rank 2, §8.1, §9.3). This is the P1 acceptance register; draft IDs ride along as `legacy_id`
  if renumbered (pass-8 §8.1).
- Within the family: BC-SL-097 is OOS (OD-14); BC-SL-068 is replaced by BC-SL-098/099 (D4-EX-2);
  OD-21, OD-30, OD-32, OD-55 refine edges (owner-decisions-log rows OD-14, OD-21, OD-30, OD-32,
  OD-55).
- Exit criterion (docs/PLAN.md §7 P1): "the Python and Go versions render byte-identical output
  for a corpus of recorded stdin fixtures and real transcripts (incl. compaction, >512 KB lines,
  rebuilds)" — fixtures synthetic-only in the public repo (docs/RESUME.md step 4).

### 4.4 Parity harness — in-scope deliverable

The harness is a first-class P1 component, not test scaffolding (PLAN §8; pass-8 L1-03; RESUME
step 3). In scope: pinned CPython oracle (production minor — research O1), extended
`sitecustomize` clock shim freezing `time.time`/`strftime`/`localtime`/`gmtime` (OD-58 mode 1),
strict UTF-8 stdio, TZ grid, temp `HOME`/`USERPROFILE`, seeded `proc_start`, fake VictoriaMetrics
including NaN/±Inf and the idle/pick series, multi-step sequences, cache-swap tests, and the
three-tier golden strategy (Tier A live differential = gate; Tier B committed Linux-generated
goldens; Tier C nightly differential fuzz — research Q3b/Q3c).

### 4.5 `tools/backfill_cost_history.py` — OUT for P1

The backfill is **out of scope for P1** and is scheduled for **P6**: docs/PLAN.md §7 P6 moves
"hylo cost backfill" out of §4's list "with the configurable cost basis", and OD-36 rules
"backfill in P6 (owner pkg of cost-history), legacy script runnable until then". P1 ports only
the status line's *read* side of `cost-history.json` (BC-SL-028/-029/-101/-102); the Go writer
must reproduce the legacy cache format so caches interchange (pass-8 AP-16, §8.2 item 5; ruling
Q-b). Until P6 the legacy script remains the seeding path.

## 5. Explicit non-goals for P1

- Exporter (P2), proxy (P3), run/hook/doctor/ca/ui (P4), cutover (P5), generalization (P6),
  ledger/metrics redesign (P7) — docs/PLAN.md §7.
- `hylo cost backfill` (P6, OD-36) — §4.5 above.
- `--subagent` / `subagentStatusLine` rows (OD-14; Claude Code 2.1.323 removed the render site).
- stdin `version` cache key — deferred until after parity (owner gate this cycle; market-intel
  question 2 answered "no … until parity").
- README positioning and peer Alternatives section — deferred to P6 (owner gate this cycle;
  market-intel §6.3).
- Design-system extraction — feature_type = cli (owner gate this cycle).
- Generalized backends, routing-in-config, pluggable telemetry (P6); ledger `flow_id`/offset (P7).
- Any behavior change, however small, unless an owner-approved deviation (D4; the only approved
  P1 deviations are D4-EX-1 and D4-EX-2 with their OD refinements).

## 6. Constraints carried forward (settled; do not reopen)

| Constraint | Effect on the port | Source |
|---|---|---|
| D4 parity first | byte parity is the P1 definition of done; a parity diff is the acceptance oracle | docs/PLAN.md §2; docs/CLAUDE.md "Parity first (D4)" |
| D5 three OSes | macOS/Linux/Windows from day one; OS code in `internal/platform` with build tags; CI on all three | docs/PLAN.md §2; docs/CLAUDE.md "Engineering" |
| D7 ledger/metric names frozen | status line reads the frozen metric store; no renaming | docs/PLAN.md §2 |
| D10 `legacy/` kept until P5 | the harness runs the Python side read-only; no edits to `legacy/` | docs/PLAN.md §10 |
| D15 config over code | every threshold/color/path a config key; defaults equal legacy literals until cutover; typed values, no `DGX_*` aliases (OD-05); HYLO_* names generated from the registry (OD-01) | docs/PLAN.md §10; owner-decisions-log OD-05, OD-01, OD-74 |
| Synthetic fixtures only | public-repo hygiene; scrub script committed; no real transcripts in `testdata/` | docs/CLAUDE.md "Public-repo hygiene"; docs/RESUME.md step 4 |
| No stdin `version` key before parity | session cache schema stays legacy (`mixv6`, raw-sid session cache name) | owner gate 2026-11-15; OD-03 |
| Success criterion | the owner's own daily use on his setup — byte parity on the owner's windows — beyond CI green | owner gate 2026-11-15; docs/PLAN.md §7 P1 |

## 7. Inputs for the semport-translation step

- **What semport-analyze should analyze** (source paths):
  `legacy/dgx_statusline.py` (whole file — it is the entire P1 port surface), witnessed by
  `docs/STATUSLINE-WIDGETS.md` (behavior spec) and `docs/STATUSLINE-REVIEW-2026-11-13.md` (why
  each rule exists), against the Phase 0 canonical registers: BC index (P3r4 §7 + r5–r8, SL
  subset), thresholds (P4r7 §B — 79 status-line thresholds of 147), conventions/env/determinism/
  pitfalls (P5r3 §B + r4/r5 — 22 pitfalls PR-01..PR-22), all consolidated in pass-8 §8.2.
- **Translation constraints to carry into the strategy:** the pitfall register PR-01..PR-22 and
  the research catalogue P1–P27 (banker's rounding, `json.dumps` separator/`ensure_ascii` lengths,
  code-point semantics, NaN ordering in `max`/`min`, naive local time, CPHP float divmod, arm64
  FMA no-fuse conversions, implicit-raise→degraded paths); the `errDegraded` top-level contract;
  committed CPython-generated expectation tables per helper; the 21 wrong-shape table tests of
  D4-EX-2.
- **Target language and floor:** Go, `go.mod` `go 1.26.0` (+ `toolchain go1.27.4`), stdlib first,
  `golang.org/x/sys` the one justified runtime dependency in P1 (research Q1, Q5).
- **Parity definition of done:** Tier A byte-identical differential vs the pinned CPython oracle
  across the synthetic corpus on ubuntu/macos/windows CI; Tier B goldens (generated from Python
  output on Linux) green on all OSes; a table test for every rule fixed in the status line review;
  Tier C differential fuzz clean for an owner-picked number of nights; then the owner's daily use
  (docs/PLAN.md §7 P1, §8; research Q3c; owner gate 2026-11-15).
- **Downstream semport steps:** the translation-plan output should land under
  `.factory/semport/` (registry pattern `semport-artifact`), building on the Phase 0 corpus in
  `.factory/semport/hylo-legacy/`.

## 8. Tensions for the owner (listed, not resolved)

1. **BC-SL-087 grammar vs OD-05 no-aliases.** BC-SL-087 pins the import-time env-crash contract
   over `DGX_SL_*` names; OD-05 removed `DGX_*` aliases (HYLO_* + config only). The P1 spec must
   re-express that crash grammar over HYLO_* keys; which parts of the legacy grammar survive the
   rename is a spec decision, not a reopened ruling.
2. **Helper-package granularity.** pass-8 names four helpers (`pyfmt`, `pyjson`, `pystr`,
   `pytime`; §8.2 item 2, L1-01); the research folds the same functions into one
   `internal/pyfmt` (Q2 recommendation). Either satisfies R3; the translate step picks one.
3. **Oracle version pin.** The P1 oracle is the production prototype's interpreter (3.11.7 per
   pass-8 §2.8), but the exact production minor is still research open-question O1; OD-15 sets a
   *different* oracle (python3 3.9.6) for the P2 exporter. Harness pins must respect both.
4. **Two approved differences inside a byte-parity phase.** D4-EX-1 (⌂ on Windows) and D4-EX-2
   (wrong-shape-line skip) must be excluded from the parity diff explicitly and pinned by their
   own table tests, or the Tier A gate will report them as failures (pass-8 §6.2, L3-01/L3-02).
5. **Cache location in P1.** Parity and cost-history inheritance favor keeping the legacy cache
   directory in P1 (research Q4c recommendation), while OD-95 approves hylo-owned paths built in
   `internal/platform`; the move is deferred (P6 migration) rather than resolved here.
6. **Registry gap.** `artifact-path-registry.yaml` has no `brownfield/{filename}` entry; this
   file's path is workflow-canonical (brownfield.lobster:252) but unregistered — registering it
   is state-manager's call.
