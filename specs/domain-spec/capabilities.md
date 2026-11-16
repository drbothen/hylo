---
document_type: domain-spec-section
level: L2
section: "capabilities"
version: "1.0"
status: draft
producer: business-analyst
timestamp: 2026-11-15T21:30:00Z
phase: 1a
inputs: [.factory/specs/product-brief.md, .factory/semport/hylo-legacy/hylo-legacy-pass-8-deep-synthesis.md, docs/PLAN.md, .factory/specs/owner-decisions-log-2026-11-14.md]
input-hash: "3fb8cb1"
traces_to: L2-INDEX.md
---

# Capabilities (Pass 2: verbs)

> What the domain does — not how. Grounded in the product brief "In Scope" and the
> Phase 0 feature set (pass-8 §3); no implementation mapping (OD-115). Delivery
> phases per docs/PLAN.md §7.

| ID | Capability | Business rule (→ DI) | Phase | Pri |
|----|-----------|----------------------|-------|-----|
| CAP-001 | **Invisible interception transport** | Terminates TLS for every host Claude Code contacts; client keeps talking to the Anthropic host; trust only via a Claude Code-scoped CA env var (DI-003, DI-014) | P3-P4 | P0 |
| CAP-002 | **Per-request lane routing** | Eligible requests (cloud host + `/v1/messages*`) get exactly one routing decision; model-prefix match sends selected models to the local lane (R0-R5); `count_tokens` handled per OD-10 (DI-001, DI-017) | P3; generalized P6 | P0 |
| CAP-003 | **Local-lane request normalization** | Tool-set rebuild + block filtering keeps the backend compatible without touching cloud requests (DI-001) | P3 | P0 |
| CAP-004 | **Backend credential handling** | Credential resolved before retargeting; failure → local error, never forward; client credentials stripped on the local lane (DI-004) | P3 | P0 |
| CAP-005 | **Response relaying + SSE usage tap** | Streams responses; taps usage/cache/stop-reason from SSE events without altering them; buffers only where legacy does; non-streamed local replies contribute no usage event — legacy behavior preserved through parity, P6 revisit config-gated (OD-126) | P3 | P0 |
| CAP-006 | **Observability ledger** | Every lane decision, reply and usage observation lands as an append-only JSONL event (13 legacy-named events, D7-frozen); diagnostic side-logs never affect outcomes (DI-005, DI-006, DI-009) | P3 | P0 |
| CAP-007 | **Plan-limit capture** | Cloud rate-limit headers captured on change per session, powering plan-window widgets (DI-001) | P3 | P0 |
| CAP-008 | **Metrics exposition** | 28 metric names recomputed from the whole ledger + hook log on `/metrics`; exposition bytes are part of parity | P2 | P1 |
| CAP-009 | **Lane-aware status line** | Pure function of stdin + transcript + metrics + caches; always exits 0, degraded ladder instead of failure (DI-007, DI-008); two rows: session/lane row and backend strip | P1 | P0 |
| CAP-010 | **Backend telemetry strip** | Health, queue, KV, throughput, TTFT, power, idle from the metrics store, with a freshness ladder (fresh/stale/dead/serving-down) | P1 | P1 |
| CAP-011 | **Cost accounting** | Per-lane cost history with personal p75/p95 percentile coloring; owned-hardware cost; the cost-history format is status-line-owned — backfill honors it as a guest (OD-124); backfill rebuilds history from the ledger (P6) | P1; backfill P6 | P1 |
| CAP-012 | **Session launch and environment scoping** | Builds the client environment, argv and settings; proxy env and CA scoped to the client only — never leaked to children (DI-014) | P4 | P0 |
| CAP-013 | **Turn control** | Stop-hook policing of language and fake stops, with the optional Kev oracle and regex fallback (DI-009 bounds its side effects) | P4 | P1 |
| CAP-014 | **Trust management and diagnostics** | `ca` (install/rotate) and `doctor` (reachability, key readability, CA state, legacy-root detection, config validation) | P4 | P0 (ca) / P1 (doctor) |
| CAP-015 | **Configuration management** | Typed keys, file→env→default precedence, validate-on-load, last-good reload, one-line error rendering, never pass-through on failure (DI-010, DI-011) | P1 (env+defaults) → P4 (file) | P0 |
| CAP-016 | **Live inspection UIs** | Web + terminal UIs reading one live event feed from the proxy; live + in-memory ring buffer only — exact `flow_id` correlation, no ledger-backed history until P7's schema (OD-122); bodies memory-only, credentials redacted (DI-016) | P4 | P1 |
| CAP-017 | **Shared proxy lifecycle** | One detached proxy per user, state file + lock, client registration, idle stop, restart on demand, bounded drain (SM-02) | P4 | P0 |
| CAP-018 | **Generalized backend fleet** | N backend entries in config from the start — P6 activates the fleet — with per-backend credential, CA and routing rules (OD-123) | P6 | P2 |

## Why each capability exists (anchor justification)

- **CAP-001..007** cover the interception/routing/observation core because the brief
  grounds hylo's reason to exist there ("Per-request lane routing through the
  invisible TLS-intercepting proxy", "The append-only JSONL ledger and Prometheus
  exporter") — brief In Scope; LEGACY-OBSERVED features F-PX-01..F-PX-12 (pass-8 §3.2).
- **CAP-009..011** cover the cockpit because the brief names "The lane-aware status
  line" as a scope item and the differentiation cluster (market-intel §4; statusline
  research §A.4) shows the backend strip + owned-hardware cost + per-lane percentiles
  are the unoccupied niche.
- **CAP-012, CAP-014, CAP-017** cover launch/trust/lifecycle because invisible mode
  and D14 make them product prerequisites, not conveniences (D6, D13, D14; OD-66).
- **CAP-013** exists because the prototype's fake-stop hook is part of the owner's
  daily loop (pass-8 §3.5) and the brief keeps it in scope.
- **CAP-016** exists by explicit owner decision (D16; memory: "fancy-but-decluttered
  web UI + TUI"). It must not disturb the ledger's bytes (DI-005).
- **Resolved validations (2026-11-15).** All formerly PROPOSED elements were decided
  by owner rulings OD-118..OD-130 (owner-validation-list.md, resolved): CAP-002's
  routing stays out of cloud-failover behavior for now (OD-127 — if ever adopted, a
  P6 opt-in config visible on the status line, with the billing caveat); CAP-005
  keeps the SSE-only usage tap through parity (OD-126); CAP-016 history scope per
  OD-122; CAP-018 config cardinality per OD-123.

## Differentiator traceability (seeds PRD §6)

| Differentiator | Backed by | Provenance |
|---|---|---|
| Backend telemetry strip (health/queue/KV/throughput/TTFT/power) | CAP-010, CAP-006 | research statusline §A.4 (unique among surveyed peers) |
| Owned-hardware `⛏` cost with per-lane percentile-from-history colors | CAP-011, CAP-009 | research statusline §A.4 |
| Composition `▤❙◈` and `⌂` window-age widgets | CAP-009 | research statusline §A.4 |
| Lane-aware with plan-limit capture in one binary | CAP-002, CAP-007, CAP-009 | research hybrid-routing §1.3 (pill peers exist — no "first/only" claim, OD-97) |
| Append-only ledger + Prometheus exporter of per-lane usage | CAP-006, CAP-008 | research hybrid-routing §1.3 |
| Not differentiators: lane pill alone, pace coloring, "single Go binary" | — | brief Prior art; OD-97 |
