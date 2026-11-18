---
document_type: domain-spec-section
level: L2
section: "bounded-contexts"
version: "1.6"
status: draft
producer: business-analyst
timestamp: 2026-11-18T08:15:29Z
phase: 1a
inputs: [.factory/specs/product-brief.md, .factory/semport/hylo-legacy/hylo-legacy-pass-8-deep-synthesis.md, docs/PLAN.md, .factory/specs/owner-decisions-log-2026-11-14.md]
input-hash: "4a28fa1"
traces_to: L2-INDEX.md
---

# Bounded Contexts

> Ten contexts (pass-8 §4, restated in domain language — no implementation homes,
> OD-115). Relations and boundary translations are the substance; the translations
> formerly marked VALID-NN were decided by owner rulings OD-118..OD-130
> (2026-11-15) — see owner-validation-list.md (resolved).

## Context map

| Ctx | Context | Domain responsibility | Phase | Key terms owned |
|-----|---------|----------------------|-------|-----------------|
| BC1 | Session Launch & Configuration | Environment, argv, settings assembly; config registry and profiles | P4 (config registry P1) | env phase, profile, `--settings`, config key |
| BC2 | Interception Transport | TLS termination for every contacted host; tunnel admission and relay | P3 | tunnel, leaf certificate, pass-through |
| BC3 | Routing & Normalization | Lane decisions R0-R5, body normalization, credential swap, SSE tap | P3 | lane, routing decision, prefix, served model, tool set |
| BC4 | Observability Ledger | The 13-event append-only record; attribution; correlation limits | P3 | ledger event, attribution, near-key |
| BC5 | Metrics Exposition | Ledger + hook log → 28 metric names; rebuild semantics | P2 | rebuild, accumulator, exposition |
| BC6 | Live Inspection | Web/TUI over one live event feed; live + in-memory ring buffer only — exact `flow_id` correlation, no ledger-backed history until P7 (OD-122); in-memory redaction | P4 | flow view, live feed, redaction |
| BC7 | Session Cockpit (status line) | Two-row render from stdin/transcript/metrics/caches, plus the `--subagent` agent-panel rows (OD-155; JSON rows, zero stdout bytes, or the 29-byte degraded line in that mode — BC-1.07.008); degraded ladder | P1 | widget, pill, thermometer, freshness ladder, degraded line |
| BC8 | Cost Accounting | Cost history, percentile colors, owned-hardware cost, backfill | P1 (backfill P6) | cost entry, percentile band, ⛏ |
| BC9 | Turn Control | Stop-hook policing: language, fake stop, Kev oracle | P4 | fake stop, verdict, colon fake |
| BC10 | Trust & Platform | CA lifecycle, doctor, per-OS platform services | P4 | trust root, doctor check |

## Relations

- **BC4 is the published language** (D7-frozen ledger): every downstream conforms —
  BC5 (exposition), dashboards, P7 readers. BC3 is the sole legitimate writer
  (post-cutover). [LEGACY-OBSERVED + DECIDED D7]
- **BC7 is a separate-ways context**: it never reads BC4 (DI-007; adopted for now per
  OD-125, which flags REVISIT at P7) — it consumes
  stdin, transcripts, BC10-adjacent platform facts, the metrics store fed by BC5
  through the export tunnel, and backend telemetry taken from the backend's own
  metrics endpoint (e.g. `vllm:*` series in VictoriaMetrics) — not the ledger
  exporter (ADV-P2-A2-20). The cockpit tolerates BC5/telemetry breakage as
  freshness degradation, never failure (SM-05, DI-008).
- BC3 → BC2: routing sits inside interception; BC3 may fail a request locally
  (CAP-004) without implicating BC2.
- BC6 shares BC3's event stream but conforms to BC4's published bytes (D16, EVT-14).
- BC9's hook log feeds BC5 tallies (substring grammar, OD-23/OD-04).
- BC1 parameterizes everything; BC10 bootstraps trust for BC2 and diagnoses BC1/BC3.

## Boundary translations

| # | Boundary | Translation | Provenance |
|---|----------|-------------|------------|
| T1 | Legacy wire names ↔ domain terms | `dgx_*` ↔ local lane; `anth_*` ↔ cloud lane; keep both vocabularies until P7 | D7 + P2r4 §3.1 (three lane vocabularies) |
| T2 | Client-view lane vs proxy-authoritative lane | The status line infers the lane from the client-reported `model.id`; the ledger records the proxy's actual decision. Both are true simultaneously; widgets must not conflate them | LEGACY-OBSERVED (P2r4 §3.1); client-view lane a distinct derived value — DECIDED OD-121 |
| T3 | Correlation translation | Ledger near-key (weak) vs internal `flow_id` (exact, ephemeral); UIs must use the latter for live views and the former for history | DECIDED OD-25 + OD-122 (BC6 history is live + ring buffer only until P7's schema) |
| T4 | Config-surface translation | `HYLO_*` env / config file / defaults encode the same typed keys; legacy `DGX_*` surface ends at cutover | DECIDED OD-05, OD-101, OD-95 |
| T5 | Parity translation | Recorded legacy inputs → identical outputs modulo the closed exclusion set (D4-EX-1, D4-EX-2, D4-EX-3, OD-30, OD-76, temp-file, cp-x03, OD-159, OD-160, OD-161, OD-166, OD-181; BC-6.03.004); harness-level, not runtime | DECIDED D4, OD-105/OD-110/OD-136, OD-169/OD-181 |
