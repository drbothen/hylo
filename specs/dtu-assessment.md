---
document_type: dtu-assessment
level: L3
version: "1.5"
status: draft
producer: architect
timestamp: 2026-11-17T22:30:00Z
phase: 1b
DTU_REQUIRED: false
inputs: [architecture/ARCH-03-statusline.md, architecture/ARCH-07-parity-harness.md, architecture/ARCH-09-reserved-boundaries.md, prd-supplements/interface-definitions.md, domain-spec/state-machines.md]
traces_to: architecture/ARCH-INDEX.md
input-hash: "05bc8a1"

---

# DTU Assessment: hylo P1 (status line)

## Summary

| Metric | Value |
|--------|-------|
| External dependencies identified | 5 |
| DTU clones recommended | 0 |
| Total clone story points | 0 (≈1 pt of fake-extension work folded into existing harness stories) |
| Estimated Wave 1 capacity needed | 0 points |

**Verdict: `DTU_REQUIRED: false`.** P1 has exactly one network edge (the metrics query
API, ARCH-03) and four non-network external contracts (statusLine stdin, the
`subagentStatusLine` agent-panel stdin, git state, process tables). All five are
reproducible at seam level with fakes the parity harness
already mandates — and the Tier A differential design actively requires the httptest
fake, because the legacy oracle must hit the *same* fake in-process through the
`DGX_SL_*` settings translation (ARCH-07). A Docker-packaged clone cannot serve the
oracle side and adds nothing the fakes lack. Extension vectors for each fake are
registered below so the boundary behaviors are pinned, not improvised.

Scope note: later-phase externals (api.anthropic.com proxy surface P3, exporter
scrape path P2, VictoriaMetrics write path) are out of scope for this cycle; ARCH-09
carries their boundaries.

## Integration Surface Inventory

### Inbound Data Sources (External → Product)

| # | Service | Protocol | Fidelity | DTU? | Justification |
|---|---------|----------|----------|------|---------------|
| 1 | Prometheus-compatible metrics query API (VictoriaMetrics) | HTTP GET `/api/v1/query` | L2 | No | Stateless request/response; entire boundary = a handful of response envelopes. Existing httptest fake (ARCH-07) plus the register's sample-string extension rows (defensive-parse ratification is P6 per OD-157, not P1 — pass-3 A2-16 removes the stale OD-130-as-P1 vectors); a Docker clone cannot serve the in-process legacy oracle in Tier A. |
| 2 | Claude Code statusLine stdin JSON | One JSON object on stdin per render | L3 (decode semantics only) | No | Not a network service — an upstream push contract. Its clone *is* the harness corpus (`stdin.json.tmpl` cases). Decode edges carry 101 S1 BCs and are already corpus-pinned. |
| 5 | Claude Code `subagentStatusLine` agent-panel stdin (OD-155) | One JSON object on stdin per panel render: `{"columns": N, "tasks": [{id, name, agentType, status, description, label, startTime, model, tokenCount, ...}]}` | L3 (decode + per-task render semantics, BC-1.07.003..008) | No | Not a network service — a SECOND upstream push contract, separate from the statusLine stdin (added pass-3 A2-16). Its clone is the `subagent`-family harness corpus rows (`argv` field + `stdin.json.tmpl`, ARCH-07). Compatibility with the 2.1.326 payload is ASSUMP-107-1, still to be verified by a capture before Phase 3. |

### Outbound Operations (Product → External)

None identified — P1 writes only stdout/stderr and local cache/state files (ARCH-03
effect script; ARCH-04). No external write targets exist until P2 (exporter).

### Identity & Access (Bidirectional — auth flow)

None identified — the metrics endpoint is unauthenticated in P1 (no credential seam in
`Env`, ARCH-03); there is no auth flow to clone until fleet credentials land (P6, out
of scope).

### Persistence & State (Product ↔ Storage)

None external — the four cache files and state directory are local (ARCH-04), exercised
via `CacheStore` with temp dirs in tests and `seed/` fixtures in the harness. Git
repository state is read locally; see row #3 below for its inventory treatment.

### Observability & Export (Product → Monitoring)

None identified — P1 emits no telemetry. The P2 exporter and its separate oracle pin
(`/usr/bin/python3` 3.9.6, OD-15 per ARCH-09) are explicitly out of scope.

### Enrichment & Lookup (External → Product, on-demand)

| # | Service | Protocol | Fidelity | DTU? | Justification |
|---|---------|----------|----------|------|---------------|
| 3 | git repository state | Filesystem reads: `.git` dir-or-file walk and HEAD (BC-1.02.004) — **not a subprocess** in the ported design; `Env.FileSystem`/`Cwd` seams, ARCH-03 | L1 | No | Static content behind a well-known layout; clone = a seeded directory tree (happy, shallow `.git` file, detached HEAD, missing/ corrupt `.git`) driving the `Files`/`Cwd` fakes. Real git used only in Tier A platform-family cases. |
| 4 | Per-OS process tables (window-age probe) | `ProcStarter.WindowStart() (float64, ok)` over `platform.FindAncestor` (ARCH-03; D4-EX-1) | L1 | No | Docker cannot faithfully clone host process tables on macOS/Windows anyway; the seam fake plus `TestWindowAge_D4EX1_Windows` and platform-family parity cases is the only faithful approach. |

## Dependency Summary

| # | Service | Category | Fidelity | DTU? | Points | Justification |
|---|---------|----------|----------|------|--------|---------------|
| 1 | Metrics query API (VictoriaMetrics) | Inbound | L2 | No | ≈0.5 | Envelope-matched httptest fake; extension rows are the register's sample-string/error-envelope modes (defensive-parse ratification is P6 per OD-157 — no stale OD-130-as-P1 vectors, pass-3 A2-16) |
| 2 | Claude Code statusLine stdin | Inbound | L3 (decode) | No | ≈0.5 | Fixture corpus is the clone; add one `unknown-future-field` variant |
| 3 | git repository state | Enrichment/lookup (local) | L1 | No | 0 | Seeded `.git` trees behind `Files`/`Cwd` seams; already scheduled |
| 4 | Per-OS process tables | Enrichment/lookup (local) | L1 | No | 0 | `ProcStarter` recording fake + `TestWindowAge_D4EX1_Windows`; already scheduled |
| 5 | Claude Code `subagentStatusLine` agent-panel stdin | Inbound | L3 (decode + render) | No | ≈0.5 | Second stdin push contract (OD-155); cloned by the `subagent`-family corpus rows with the new `argv` field (ARCH-07); BC-1.07.001..008 + ASSUMP-107-1 capture pending |

## Boundary Reproduction Register (what each fake must pin)

### #1 Metrics query API (VictoriaMetrics)

Public API facts (docs.victoriametrics.com, VictoriaMetrics index / key-concepts /
operator quick-start pages, cited): instant query `GET|POST /api/v1/query` with
required `query`, optional `time` (RFC3339 or unix), VictoriaMetrics-specific `step`
(look-back for missing samples, default 5m), `timeout`, plus VM extras `extra_label`,
`extra_filters[]`, `round_digits` and an extra `stats` object. Success envelope:

```json
{"status":"success","data":{"resultType":"vector","result":[{"metric":{"__name__":"m"},
  "value":[1746099757,"123"]}]},"stats":{"seriesFetched":"1","executionTimeMsec":0}}
```

The value element is a **string**, which is how special values ride through JSON; the
VM changelog (v1.77.0) separately records that bare `NaN` broke JSON parsing and
staleness markers moved to `null` — grounding the defensive-parse stance.

| # | Behavior the fake must reproduce | Contract |
|---|----------------------------------|----------|
| 1 | 200 success envelope, vector result, `[ts, "string"]` tuple | BC-1.04.001 happy path (fetch_sample parse; ADV-P1-A2-21: CP-N02 is the sparkline crash path, not this) |
| 2 | Empty `result` array (up, no data in window) → stale-ladder path, not an error | SM-05 fresh→stale→dead; OD-57 E-A |
| 3 | `"NaN"` sample string → **kept as a float**, exactly like legacy `float("NaN")` at SL:178 / BC-1.04.001 — the fake returns it, and the NaN sample then drives the CP-N01/KV and CP-N02/sparkline crash paths downstream (BC-1.04.014/.015/.016, VP-001). It is not dropped | BC-1.04.001 PC-2 (kept as float); CP-N01/N02 consumers |
| 4 | `"+Inf"` / `"-Inf"` sample strings → **P1 keeps legacy behavior** (+Inf on `v`/`f` degrades via the sparkline crash path, -Inf clamps to `▁`; BC-1.04.014); the OD-130 defensive-unknown rule takes effect after cutover, P6 only (**OD-157**) | **OD-157** (rules pass-2 A2-01: no 8th exclusion id; P1 parity unbroken) |
| 5 | Error envelope (`status:"error"`) and HTTP 500 | CP register error taxonomy |
| 6 | Connection refused / unreachable server | harness mode `down` |
| 7 | Garbage non-JSON body | harness mode `garbage` |
| 8 | Hang exceeding the total query deadline → ctx cancellation | `MetricsClient.Query` contract |
| 9 | Malformed tuples (wrong arity, non-string element) → defensive parse | IM-15 catch-list parity |

The fake matches fixtures, not PromQL: it must tolerate any query string legacy or Go
authors (queries are legacy-authored; the harness never evaluates MetricsQL). Follow-up
hook: when the owner confirms the backend soak is scored, record the one real response
capture (read-only, scrubbed into `captures/`) and pin it as a golden fixture for the
OD-130 defensive rule — a P6 activity per OD-157, not needed for P1 parity.

### #2 statusLine stdin JSON contract

Per code.claude.com (`/docs/en/statusline`): core documented fields `session_id`,
`transcript_path`, `cwd`, `model.id`, `model.display_name`, `workspace.current_dir`,
`workspace.project_dir`, `version`, `output_style.name`, `cost.total_cost_usd`,
`cost.total_duration_ms`, `context_window.*`; `workspace.repo` present only with an
`origin` remote; `rate_limits` only for eligible subscribers/gateways, only after the
first API response, with windows independently absent and dropped once `resets_at`
passes; `pr.review_state`/`pr.kind` independently absent; `prompt_cache` after first
response; `context_window.current_usage` null before first API call and after
`/compact`. Official guidance is to handle missing fields with conditional access and
nulls with fallbacks — the contract is deliberately loose and grows optional fields.

| # | Behavior the corpus must pin | Contract |
|---|------------------------------|----------|
| 1 | Field absent / null / wrong inner type → per-field degrade, never crash | CP-S01..S17, BC-1.02.x |
| 2 | ModeText decode: BOM, invalid UTF-8 → `{}` continue; `NaN`/`Infinity`/`-Infinity` tokens; trailing data; non-object top level | BC-1.01.002/.008, BC-5.02.003 |
| 3 | Recursion budget 993 accept / 994 reject at stdin | BC-1.01.002 |
| 4 | Unknown *future* field present → ignored (forward compat) | defensive-parse invariant; add one synthetic `unknown-future-field` corpus variant |
| 5 | `rate_limits` with and without dollar fields; windows independently absent | interface-definitions stdin table |

Existing corpus coverage (rows 1–3, 5) suffices; only the row-4 variant is new.

### #3 git state and #4 process tables

Seeded `.git` trees and scripted `WindowStart` outputs, respectively, as inventoried
above; no further extension beyond the platform-family cases already scheduled
(`TestWindowAge_D4EX1_Windows`; D4-EX-1 exclusions in the closed set).

## Services NOT Requiring DTU

| # | Service | Reason |
|---|---------|--------|
| 1 | Metrics query API (VictoriaMetrics) | Stateless envelope-matched fake serves both oracle and implementation in Tier A parity; Docker clone can't participate in the in-process oracle leg |
| 2 | Claude Code statusLine stdin | Upstream push contract — clone *is* the fixture corpus, already mandated by ARCH-07 |
| 3 | git repository state | Local filesystem content; seeded tree behind `Files`/`Cwd` seams is exact |
| 4 | Per-OS process tables | Host-fidelity impossible in containers on macOS/Windows; seam fake is the only faithful clone |
| 5 | Claude Code `subagentStatusLine` agent-panel stdin (OD-155) | Second upstream push contract — same reason as #2: its clone is the `subagent`-family harness corpus rows (pass-4 A2-21: row was missing from this table though present in the inventory and Dependency Summary; ASSUMP-107-1 capture still pending) |

## DTU Architecture

Not applicable this cycle — no Docker Compose structure. The seam-fake register above
replaces it; environment overrides are already contractual:

| Concern | Production | Test mechanism (existing) |
|---------|-----------|---------------------------|
| Metrics endpoint | `backends[0].metrics_url` (default `http://192.0.2.10:8428`) | httptest listener URL via typed settings translation (ARCH-07) |
| stdin payload | Claude Code per refresh | `stdin.json.tmpl` corpus cases |
| Transport hygiene | system resolver/proxy env | child env built from scratch, no `*_proxy`, `Proxy: nil` client (D14 precedent, ARCH-09) |
| Process/window age | host process table | `ProcStarter` recording fake + clock shim `HYLO_TEST_NOW` |

## Clone Development Approach

No Docker-packaged clones are developed this cycle. The register above is the clone
specification by reference: each fake's extension vectors (the sample-string,
deadline-hang and error-envelope modes for #1; the `unknown-future-field` stdin variant
for #2; the `subagent`-family rows with the `argv` field for #5) are delivered as harness stories under `internal/parity` /
`internal/statusline/testdata/` per AD-13 fixture co-location, not as separate clone
stories. Should a later cycle (P2 exporter scrape path, P3 proxy surface) introduce an
externally hosted dependency that cannot be seam-faked without losing oracle
participation, this assessment is revisited and clone stories scheduled in that cycle's
Wave 1.
