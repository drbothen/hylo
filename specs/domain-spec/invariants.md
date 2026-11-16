---
document_type: domain-spec-section
level: L2
section: "invariants"
version: "1.0"
status: draft
producer: business-analyst
timestamp: 2026-11-15T21:30:00Z
phase: 1a
inputs: [.factory/specs/product-brief.md, .factory/semport/hylo-legacy/hylo-legacy-pass-8-deep-synthesis.md, docs/PLAN.md, .factory/specs/owner-decisions-log-2026-11-14.md]
input-hash: "3fb8cb1"
traces_to: L2-INDEX.md
---

# Domain Invariants (DI-NNN)

> Rules that must always hold in the hylo domain. "Violation behavior" names what the
> domain does when the antecedent fails — many invariants exist precisely because
> legacy violated them (those deltas are DECIDED). Anchor form: "DI-NNN is a domain
> invariant because <reason>", with provenance.

| ID | Invariant | Because / provenance | Violation behavior |
|----|-----------|----------------------|--------------------|
| DI-001 | Every request to the cloud host's `/v1/messages*` receives exactly one routing decision (R0-R5); no other request is ever rewritten. | The lane concept collapses without one-decision-per-request; scope corroborated by production counts (P2r2 §4.2, P2r8 §7). Rewrite surface narrowed by DECIDED D13 + OD-10 (`count_tokens`). | Untouched relay; no ledger events beyond pass-through classes. |
| DI-002 | Cloud-bound and Remote Control traffic passes through byte-for-byte unchanged. | Remote Control breaks otherwise (research hybrid-routing §1.1, §2.4); DECIDED D6, D13. | Diff vs legacy = parity failure; RC loss = product-killing defect. |
| DI-003 | The client always addresses the cloud host; the base URL is never repointed. | Invisible mode is the design point — DECIDED D6; peer base-URL gateways all lose RC (research hybrid-routing §1.1). | A repointed client is by definition not hylo. |
| DI-004 | Credentials never cross lanes: the backend credential only goes to the selected backend; client credentials are stripped before a local-lane forward; an unreadable credential fails closed. | DECIDED OD-06/OD-07 overriding the legacy fail-open path (pass-8 L0-01/L0-02). | Local 502 + routing-error event; replay marks as approved deviation. |
| DI-005 | The ledger is append-only JSONL: one `write()` per line on an append-descriptor, event set and field order frozen until P7, `t` naive local time at write time. | D7; writer contract P2r4 §3.2. | Consumers (exporter, dashboards) break; parity fails. |
| DI-006 | No consumer may assume request↔reply pairing in the ledger: lines interleave in write order across writers; pairing is by composite near-key only. | No flow id exists in the schema; retries are indistinguishable (P2r4 §3.3). | Replay/history views mispair — hence OD-25's reported ambiguities. |
| DI-007 | The status line never reads the ledger. Its inputs are stdin, the transcript, the metrics store and its own caches. Live per-request data may reach it only via exporter metrics or the D16 event feed. | LEGACY-OBSERVED (P2r4 §3.2) and kept deliberately — the status line stays a pure function decoupled from writer crashes. DECIDED OD-125 (permanent rule). **REVISIT at P7** (ledger redesign): allowing ledger-backed widgets then would amend DI-007 and add a BC7←BC4 dependency. | Coupling would import ledger corruption into rendering; a status-line ledger read violates the invariant until the P7 revisit (OD-125). |
| DI-008 | Rendering never fails: any fault produces the degraded ladder — one-line output, exit 0 (imports, config errors D4-EX-3, unknown flags OD-112 included). | LEGACY-OBSERVED CV-08 + DECIDED OD-102/OD-112. | Blank/nonzero output violates the client contract. |
| DI-009 | Observability never changes outcomes: diagnostic writes (decision log, hook log, flow log) are best-effort and isolated from routing, ledger and hook decisions. | DECIDED OD-45, fixing legacy note()-aborts (pass-8 L0-10). | A log failure would alter a routing result — prohibited. |
| DI-010 | Configuration precedence is file → `HYLO_*` env → default; every key is typed and validated with a stated rationale; invalid config never silently falls back to pass-through. | DECIDED D15, OD-05, OD-59, OD-102, OD-114. | Silent fallback would move billing between lanes unnoticed. |
| DI-011 | Startup with invalid config refuses to start; reload failure keeps the last good config and raises a loud error event. | DECIDED OD-26, replacing legacy's plain-pass-through degradation (pass-8 L0-07). | The silent-pass-through state is the domain's most dangerous failure. |
| DI-012 | Behavior may change versus the oracle only via named, tested deviations (D4-EX-1/2/3 + OD-110 entries); every exclusion carries its own table tests; no blanket exclusions. | DECIDED D4, OD-105, OD-110. | Unexplained diffs fail P1-P3 exit criteria. |
| DI-013 | No timeout shall cut an in-flight stream shorter than the client's API timeout; idle cuts apply only to connections with no flow in progress; pass-through has no total cap. | DECIDED OD-37/OD-42 (HY-TIMEOUT-1, HY-PASS-1), from the observed in-flight cut (P2r8 §1.1). | Mid-stream cuts lose usage and corrupt UX with no ledger trace. |
| DI-014 | Environment scoping: the CA is trusted only via the client-scoped env var (never the OS store); proxy env never reaches child processes. | DECIDED D13, D14; production harm counts in P2r8 §3. | Broken child TLS; intercepted child traffic (observed harms). |
| DI-015 | Every listener binds loopback by default; a non-loopback bind is explicit config with a warning; admission is checked separately from binding. | DECIDED OD-24/OD-27 (HY-BIND-1..6), from observed LAN exposure (P2r4 §2.2). | Silent LAN exposure of backend key or exporter. |
| DI-016 | The UI feed keeps request bodies in memory only and redacts credentials; the ledger's published bytes are not altered by UI needs. | DECIDED D16, OD-53 (metadata-only flow log). | Persisted bodies/credentials violate the credential stance. |
| DI-017 | Local-lane routing keys on a case-sensitive model-prefix match, deterministic per request; server-tool requests stay on the cloud lane. | LEGACY-OBSERVED routing R4/R5 (P2r4 §3.1); generalized to config rules at P6 (DECIDED D15, OD-111) without changing determinism. | Nondeterministic routing breaks cost attribution and parity. |

Anchor trace: DI-001/005/006/017 → CAP-002/006; DI-002/003 → CAP-001; DI-004 →
CAP-004; DI-007/008 → CAP-009; DI-009 → CAP-006/013; DI-010/011 → CAP-015; DI-013 →
CAP-005; DI-014 → CAP-012; DI-015 → CAP-017; DI-016 → CAP-016.
