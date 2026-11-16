---
document_type: domain-spec-section
level: L2
section: "domain-events"
version: "1.0"
near_title: ""
version_notes: ""
status: draft
producer: business-analyst
timestamp: 2026-11-15T21:30:00Z
phase: 1a
inputs: [.factory/specs/product-brief.md, .factory/semport/hylo-legacy/hylo-legacy-pass-8-deep-synthesis.md, .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r4.md, .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r8.md, .factory/specs/owner-decisions-log-2026-11-14.md]
input-hash: "600cb42"
traces_to: L2-INDEX.md
---

# Domain Events (EVT-NNN)

> Pass 2 output. Two registers: the **ledger** — the D7-frozen, legacy-named catalog
> (P2r4 §3.2, amended P2r8 §7) — and hylo's **live event stream** (D16). Event names
> are wire names frozen by D7 even where misleading.

## 1. Ledger catalog (D7-frozen; 13 legacy names)

Writer contract [LEGACY-OBSERVED]: one line per event, `t` first, then `event`, then
fields in fixed order; `json.dumps` byte rules (`ensure_ascii`, `", "`/`": "`); one
`write()` per line on an append-descriptor; write failure swallowed; **multi-writer**
(one per window, legacy); `t` = naive local wall time at 1 s resolution taken at write
time. hylo adds an internal `flow_id` on the event stream only — never in the ledger
(OD-25).

| ID | Event (wire name) | Lane | Trigger | Key fields (after `t, event`) | Provenance |
|----|-------------------|------|---------|--------------------------------|------------|
| EVT-01 | `dgx_request` | local | Routing decision R5 | attribution + `model_served` (= requested model — naming trap), `req_bytes` (characters) | LEGACY-OBSERVED |
| EVT-02 | `dgx_reply` | local | Response on local lane, any status | `status, duration_s` + full attribution + optional tap fields | LEGACY-OBSERVED |
| EVT-03 | `dgx_usage` | local | Only after EVT-02 when tapped | SSE usage found → attribution + `in_tok` (whole prompt), `out_tok`, `stop_reason` [+ `cache_read_tok`] | LEGACY-OBSERVED; SSE-only tap (non-streamed local replies contribute no usage event) preserved through parity — DECIDED OD-126, P6 revisit config-gated |
| EVT-04 | `dgx_upstream_error` | local | Error hook on local lane | `error` (≤ 300 chars) + attribution | LEGACY-OBSERVED |
| EVT-05 | `anth_request` | cloud(+st) | R3 / R4 | attribution + `lane` | LEGACY-OBSERVED |
| EVT-06 | `anth_reply` | cloud(+st) | Response on cloud lane | attribution + `status, duration_s` + optional usage + 4 cache fields | LEGACY-OBSERVED |
| EVT-07 | `anth_usage` | cloud(+st) | Tapped usage | `lane`, attribution, `model` (= requested), `in_tok` (uncached only), 4 cache fields (5m is derivationally wrong on stream — derive 5m = write − min(1h, write)) | LEGACY-OBSERVED |
| EVT-08 | `anthropic_upstream_error` | any non-backend host | Error hook, `/v1/messages*` | `error` + attribution; identifies the **host**, not the lane (CONV-ABS-14). Name says "anthropic" yet covers any non-backend host in `/v1/messages*` — a D7-frozen semantic trap | LEGACY-OBSERVED |
| EVT-09 | `anth_ratelimit` | cloud | Headers changed since last snapshot for the session in this process | `session`, `headers {suffix: value}` in wire order | LEGACY-OBSERVED |
| EVT-10 | `bridge_ws_connect` | cloud | Upgrade on the legacy bridge host — dead in production (CONV-ABS-26); Remote Control actually runs on the cloud host | `host` | LEGACY-OBSERVED |
| EVT-11 | `bridge_ws_close` | cloud | At the 101 upgrade response, not at close; duration always 0.0 — misleading name | `duration_s` | LEGACY-OBSERVED |
| EVT-12 | `ws_closed` | — | Never (guard never set) — dead, reproduced as-is until P7 | `duration_s` | LEGACY-OBSERVED |
| EVT-13 | `anthropic_reply` | cloud | Historical alias of `anth_reply` (pre-2026-11-10); readers alias it | — | LEGACY-OBSERVED |

Reader rule [LEGACY-OBSERVED, P2r4 §3.2]: treat `path`, `req_bytes`, cache fields,
`lane`, attribution as optional; alias EVT-13→EVT-06; derive 5m-cache writes; treat
EVT-08 as current; interpret `t` as naive local (DST-ambiguous one hour each autumn);
never assume a request has a reply, usage or error event.

## 2. Live event stream (D16) and side logs

| ID | Event/register | Producer → consumer | Notes |
|----|----------------|---------------------|-------|
| EVT-14 | Live feed event (per flow step, internal `flow_id`) | proxy → ledger-format-compatible feed, UIs | Shares the event vocabulary with the ledger but must not change its bytes (D16, OD-25); ring-buffer retention — UI history is live + in-memory ring buffer only, ledger-backed history waits for P7's schema (DECIDED OD-122); ring-buffer size is a config key (D15), and the UI states where its history begins |
| EVT-15 | Diagnostic registers: decision log (lane decisions as data — OD-40), metadata-only flow log (OD-53), hook log (repr grammar, OD-04) | proxy/hook → doctor, UIs, exporter tallies | Best-effort per DI-009; flow log size-capped, query-string-free, private dir |

Ordering: the only ordering guarantee inside one lane is write order within a process;
the live stream carries causal order per `flow_id` (EVT-14). The exporter tallies
consume the ledger and hook log (EVT-15) but not vice versa.
