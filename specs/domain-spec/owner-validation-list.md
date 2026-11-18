---
document_type: spec-open-questions
level: L2
section: "owner-validation-list"
version: "1.3"
status: resolved
producer: business-analyst
timestamp: 2026-11-18T03:35:34Z
phase: 1a
inputs: [.factory/specs/product-brief.md, .factory/semport/hylo-legacy/hylo-legacy-pass-8-deep-synthesis.md, .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r4.md, .factory/specs/owner-decisions-log-2026-11-14.md]
input-hash: "b7714d2"
traces_to: L2-INDEX.md
---

# Owner Validation List

> Genuinely open items for owner conversation; per the task, nothing here was asked
> of anyone by this agent. Grouped by class; stakes: **HIGH** = would change a P1 BC
> or the architecture skeleton. Each item: item / proposed resolution / alternatives /
> source evidence. All other PROPOSED content in the spec was marked inline.
>
> **RESOLVED 2026-11-15: the owner ruled on all 13 items.** Resolution lines below
> carry the outcome and OD id (VALID-01..13 → OD-118..OD-130); the shards carry the
> rulings inline. Evidence retained unchanged.

## A. Terms

### VALID-01 — Overloaded "window" and "session" (LOW)

**Resolution (2026-11-15): ADOPTED as proposed — OD-118.** Qualified readings in
ubiquitous-language §3 are canonical.

- **Item.** "Window" means a 5h/7d plan window, a terminal window, and the `⌂`
  process-age widget; "session" spans session id, cache keys, and the ledger's
  `session` attribution field.
- **Proposed resolution.** Adopt the qualified readings in ubiquitous-language §3:
  plan window / client window / process-age window (`⌂`); session id (raw/sanitized
  cache-key forms per OD-03).
- **Alternatives.** Rename `⌂`'s caption to "client uptime"; keep ad-hoc usage.
- **Evidence.** P2r1 §3; OD-03; pass-8 F-SL-07; brief Success Criteria ("100% of
  windows on hylo" = client windows).

### VALID-02 — Third lane name (LOW)

**Resolution (2026-11-15): ADOPTED as proposed — OD-119.** Cloud lane/server-tools,
a sub-outcome of the cloud lane, not a third lane.

- **Item.** Legacy recognizes a third outcome — server-tool requests routed to
  Anthropic (R4) — logged as `lane: "anthropic-server-tools"`.
- **Proposed resolution.** Call it **cloud lane/server-tools**, a sub-outcome of the
  cloud lane, not a third lane.
- **Alternatives.** Promote it to a lane of its own; or "server-tools detour".
- **Evidence.** P2r4 §3.1 lane row (three vocabularies), routing R4; D13 keeps
  server-tools on Anthropic.

### VALID-03 — "Backend" as the domain term (LOW)

**Resolution (2026-11-15): ADOPTED as proposed — OD-120.** Backend for the server,
local lane for the lane.

- **Item.** The legacy code and config say DGX; the domain needs a generic term.
- **Proposed resolution.** **Backend** for the server, **local lane** for the lane.
  Pass-8 L0 items already use `backend.*` config keys.
- **Alternatives.** "Inference server", "home inference node", "local model server".
- **Evidence.** brief In Scope ("any Anthropic- or OpenAI-compatible backend");
  pass-8 L0-01..L0-03 key names; OD-111 prefix key.

## B. Entities and relationships

### VALID-04 — Client-view lane is a distinct derived value (LOW)

**Resolution (2026-11-15): ADOPTED as proposed — OD-121.** Client-view lane is a
distinct derived value object; widgets state which view they render.

- **Item.** The status line's lane is inferred from the client's stdin `model.id`,
  not the proxy's decision — two truths, one term.
- **Proposed resolution.** Model **client-view lane** as a derived value object;
  widgets state which view they render. The proxy decision stays authoritative for
  ledger/BC8 history.
- **Alternatives.** One lane concept, sources merged at P1 (rejection: the status
  line must not depend on ledger truth, cf. VALID-08).
- **Evidence.** P2r4 §3.1 lane vocabularies; bounded-contexts T2.

### VALID-05 — BC6 (Live Inspection) history source (HIGH)

**Resolution (2026-11-15): ADOPTED — OD-122.** P4 web UI and P6 terminal UI are live
+ in-memory ring buffer only (exact `flow_id` correlation); ledger-backed history
waits for P7's schema (OD-25). Ring-buffer size is a config key (D15); the UI states
where its history begins.

- **Item.** Is ledger-backed history in scope for the UIs, or live-only?
- **Proposed resolution.** P4 UIs are **live + in-memory ring buffer only** (exact
  `flow_id` correlation, EVT-14); any ledger-backed history view waits for P7's
  schema (`flow_id` + UTC offset, OD-25) because near-key history inherits retry
  ambiguity (DI-006).
- **Alternatives.** Ship ledger-backed history in P4 using near-key correlation and
  report ambiguous pairs UI-side (heavier, inherits DI-006 ambiguity).
- **Evidence.** P2r4 §3.3; OD-25; D16; pass-8 L0-05.

### VALID-06 — Backend fleet cardinality (HIGH)

**Resolution (2026-11-15): ADOPTED — OD-123.** N backends in config from the start
(name, url, protocol flavor, credential, CA, routing rules); P1-P5 run with exactly
one entry, validated — zero or more than one entry is a config error until P6; P6
activates the fleet. For P1 the status line's metrics URL and model-prefix keys live
under the backend entry (`backends[0].metrics_url`, `backends[0].model_prefixes`),
not as top-level singletons.

- **Item.** The domain model needs a cardinality ruling: one backend entity or a
  config-defined fleet?
- **Proposed resolution.** Model **N backends in config** (name, url, protocol
  flavor, credential, CA, routing rules) from the start; P1-P5 instantiate one,
  P6 activates the fleet (CAP-018). Shapes the config-registry skeleton and the
  routing entity once, instead of a P6 retrofit.
- **Alternatives.** Model one backend through P5 and generalize at P6 (cheaper now,
  risks reshaping keys at P6, contra D15 stability).
- **Evidence.** brief In Scope (P6 fleets); OD-20 (series list as "P6 backend
  contract"); OD-41b (per-backend `ca_file`/client cert); ENT-09.

### VALID-07 — Cost-history ownership (LOW)

**Resolution (2026-11-15): ADOPTED as proposed — OD-124.** Cost history is a
status-line-owned shared artifact; backfill and the one-time cutover copy (OD-106)
honor the format as guests.

- **Item.** cost-history.json is written by the status line and (in P6) rebuilt by
  `cost backfill`; a parse failure historically wiped it (AP-16).
- **Proposed resolution.** Cost history is a **status-line-owned shared artifact**:
  the status line owns the format; backfill and the one-time cutover copy (OD-106)
  honor the format as guests.
- **Alternatives.** Promote it to a small published language like the ledger (D7)
  with its own freeze rule.
- **Evidence.** P2r1 §3.5; AP-16; OD-106; BC8.

## C. Invariants

### VALID-08 — Elevate "status line never reads the ledger" (DI-007) to a permanent rule (HIGH)

**Resolution (2026-11-15): ADOPTED FOR NOW WITH A REVISIT FLAG — OD-125.** DI-007 is
in force; live per-request data may reach the status line only via exporter metrics
or the D16 event feed. Marked **REVISIT at P7** (ledger redesign); the revisit flag
is recorded in invariants.md next to DI-007.

- **Item.** LEGACY-OBSERVED: the status line never reads the ledger (P2r4 §3.2). Kept
  as DI-007; is it permanent domain law or an accidental decoupling?
- **Proposed resolution.** Permanent: it keeps the P1 render a pure function and the
  cockpit failure-independent (DI-008 holds even when the ledger writer is broken).
- **Alternatives.** Allow ledger-backed widgets at P7 (would amend DI-007 and add a
  BC7←BC4 dependency).
- **Evidence.** P2r4 §3.2; DI-007; pass-8 §4 ("BC7 is a separate ways context").

### VALID-09 — Usage capture on non-streamed responses (LOW)

**Resolution (2026-11-15): ADOPTED as proposed — OD-126.** Legacy behavior preserved
through parity (P1-P5); revisit at P6 with per-backend rules (small, config-gated).

- **Item.** Legacy taps usage from SSE only; a non-streamed local reply contributes
  no usage event. Sources are silent on whether that is desired.
- **Proposed resolution.** Preserve legacy behavior through parity (P1-P5); revisit
  at P6 with per-backend rules (small, config-gated).
- **Alternatives.** Treat as a defect to fix at cutover (changes BC8/BC4 semantics).
- **Evidence.** P2r4 §3.2 EVT-03 trigger ("SSE only"); CAP-005.

### VALID-10 — Opt-in cloud failover when the local lane fails (LOW)

**Resolution (2026-11-15): ADOPTED as proposed — OD-127.** Out of the domain model
for now; adopt (if ever) as P6 opt-in config, visible on the status line, with the
billing caveat.

- **Item.** When the backend errors, should requests retry on the cloud lane? No OD
  governs this; pass-8 ranks it a trade-off (L2-01).
- **Proposed resolution.** Keep out of the domain model for now; adopt (if ever) as
  P6 opt-in config, visible on the status line, with the billing caveat.
- **Alternatives.** Never (pure parity stance); or automatic failover (touches the
  policy risk the hybrid-routing research §4.1 records).
- **Evidence.** pass-8 L2-01; peer lessons L6; research hybrid-routing §4.1.

## D. State machines

### VALID-11 — Proxy registration semantics (LOW)

**Resolution (2026-11-15): ADOPTED as proposed — OD-128.** Registration = launch-time
claim + periodic heartbeat in the state file; liveness = heartbeat freshness; exact
mechanism is a P4 architecture detail; domain commitment: a client can die without
taking the proxy down.

- **Item.** SM-02's "clients registered" state needs a concrete mechanism (OD-66 says
  state file + lock; the heartbeat is unspecified).
- **Proposed resolution.** Registration = launch-time claim + periodic heartbeat in
  the state file; liveness = heartbeat freshness. Exact mechanism is a P4
  architecture detail; the domain commitment is "a client can die without taking the
  proxy down".
- **Alternatives.** Lease-based liveness; explicit `hylo run` shutdown handshake.
- **Evidence.** OD-66/OD-50; SM-02.

### VALID-12 — Pass-through connection acquisition (LOW)

**Resolution (2026-11-15): ADOPTED as proposed — OD-129.** Connect-on-demand for
pass-through too, same never-couple rule; no eager upstream connect anywhere.

- **Item.** OD-17 speaks of routed lanes; pass-through legs also needed a rule after
  the eager-connect removal.
- **Proposed resolution.** Connect-on-demand for pass-through too, same never-couple
  rule; no eager upstream connect anywhere.
- **Alternatives.** Keep eager connect for pass-through only (favors legacy byte
  behavior in error timing over lane independence).
- **Evidence.** OD-17; SM-03; P2r4 §1.2-1.3.

### VALID-13 — Telemetry Inf handling (LOW)

**Resolution (2026-11-15): ADOPTED WITH OWNER AMENDMENT — OD-130.** Treat
+Inf/-Inf telemetry samples as unknown, like a stale sample (defensive parse). A real
capture of one metrics response from the owner's backend (read-only) is taken only
after the owner confirms the backend soak has been scored. **Amended by OD-157:
OD-130 applies only from P6 — P1 keeps legacy ±Inf behaviour (parity per BC-1.04.014:
+Inf on the `v`/`f` traces degrades the sample, while +Inf on the `k` trace is safe
(fixed top); -Inf clamps to the U+2581 light-shade glyph); the defensive
rule stands from the P6 switch on (SM-05).**

- `+Inf`/`-Inf` samples in the metrics response: VictoriaMetrics documentation says
  NaN is dropped; Inf handling is open (CP-N02). Proposed: pin with the owner
  capture listed in pass-8 §11 ("one VictoriaMetrics response ... idle box"); until
  then, treat Inf as a stale-sample unknown (defensive parse).
- Alternatives: clamp Inf to the freshest finite sample; render a distinct verdict.
- Evidence: P2r3 §2 CP-N01/N02; pass-8 §11 owner-capture wish; SM-05.

## Summary

| Class | Count | HIGH items |
|---|---|---|
| Terms | 3 | — |
| Entities & relationships | 4 | VALID-05, VALID-06 |
| Invariants | 3 | VALID-08 |
| State machines | 3 | — |
| **Total** | **13** | **3** |

**HIGH items (verbatim proposals):**
- **VALID-05:** P4 UIs are live + in-memory ring buffer only; ledger-backed history
  waits for P7's schema (OD-25).
- **VALID-06:** N backends in config from the start; P1-P5 instantiate one, P6
  activates the fleet.
- **VALID-08:** "Status line never reads the ledger" is permanent domain law.

---

**Outcome (2026-11-15): all 13 items resolved — ADOPTED: OD-118..OD-124, OD-126..
OD-129; ADOPTED FOR NOW WITH A REVISIT FLAG (P7): OD-125; ADOPTED WITH OWNER
AMENDMENT: OD-130.** Shards updated accordingly; zero unresolved PROPOSED markers
remain in the spec.
