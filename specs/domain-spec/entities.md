---
document_type: domain-spec-section
level: L2
section: "entities"
version: "1.3"
status: draft
producer: business-analyst
timestamp: 2026-11-18T08:15:29Z
phase: 1a
inputs: [.factory/specs/product-brief.md, .factory/semport/hylo-legacy/hylo-legacy-pass-8-deep-synthesis.md, .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r4.md]
input-hash: "fd334b7"
traces_to: L2-INDEX.md
---

# Entities (Pass 1: nouns)

> Product-level, implementation-independent (OD-115). Legacy field names kept where
> D7 freezes them; domain names per `ubiquitous-language.md`. Entity catalogue source:
> P2r4 §3.1 (amended by P2r8 §7) unless cited otherwise.

## 1. Core entities

| ID | Entity | Description / key attributes | Provenance |
|----|--------|------------------------------|------------|
| ENT-01 | **Lane** | Where a request is served: local lane, cloud lane, cloud lane/server-tools. Client view: `dgx`/`anth` derived from stdin `model.id`. Three legacy vocabularies (proxy, status line, backfill) — see ubiquitous-language | LEGACY-OBSERVED (P2r4 §3.1); server-tools naming DECIDED (OD-119); client-view lane DECIDED (OD-121) |
| ENT-02 | **Routing Decision** | The per-request outcome: R0 bridge-WS, R1 not intercepted, R2 unparseable body, R3 cloud, R4 server-tools, R5 local. Exactly one per eligible request | LEGACY-OBSERVED (P2r2 §4.2); scope amended DECIDED D13, OD-10 |
| ENT-03 | **Request Body** | Consumed JSON: `model`, `metadata.user_id`, `tools[]`, `messages[].content[].type`. Non-object/unparseable → never rewritten | LEGACY-OBSERVED (P2r2 §4.1) |
| ENT-04 | **Normalized Tool Set** | Rebuilt only when `changed`: duplicates collapse (last definition, first slot), nameless/non-dict tools dropped, non-six-type blocks dropped | LEGACY-OBSERVED (P2r2 §4.3) |
| ENT-05 | **Flow Attribution** | `project, user, session, meta_user_id, model_req, req_bytes (characters!), path [, lane]`; copied into every reply/error event of the flow | LEGACY-OBSERVED (P2r4 §3.1) |
| ENT-06 | **Flow** | One request + its reply/error + optional usage, paired by composite near-key `(session, path, model_req, req_bytes)` ±1 s; carries an internal `flow_id` in hylo's live event stream (never written to the ledger) | Flow=near-key LEGACY-OBSERVED (P2r4 §3.3); `flow_id` DECIDED (OD-25) |
| ENT-07 | **Ledger Event** | One of 13 legacy-named events (EVT-01..EVT-13); `t` naive local time, 1 s resolution; append-only JSONL line | LEGACY-OBSERVED (P2r4 §3.2); frozen DECIDED D7 |
| ENT-08 | **Rate-limit Snapshot** | `{suffix: value}` set of `anthropic-ratelimit-unified-*` headers, wire first-occurrence order, logged on change per session | LEGACY-OBSERVED (P2r3 §1.3) |
| ENT-09 | **Backend** | The local inference server (legacy: the DGX). Config entry: `name`, `url`, protocol flavor (Anthropic-/OpenAI-compatible from P6), credential, CA, routing rules; the status line's `metrics_url` and `model_prefixes` keys live under the entry (P1: `backends[0].metrics_url`, `backends[0].model_prefixes` — not top-level singletons) | LEGACY-OBSERVED single instance; N-backends-in-config model DECIDED (OD-123; brief In Scope, P6; OD-20) |
| ENT-10 | **Backend Credential** | Bearer key from a key file (legacy) / config-resolved secret (hylo). Must resolve **before** retargeting; failure → fail closed | legacy path LEGACY-OBSERVED; fail-closed DECIDED (OD-06/OD-07) |
| ENT-11 | **Health Sample / History Point** | One telemetry observation `{name or up:<job>: value}`; point `{t, v, k, f, p}` — only `t` is guaranteed; a missing series omits its key, `p` appears only while preemptions are active — from the metrics store recording-rule series (18 series) | LEGACY-OBSERVED (P2r1 §4; P2r3 §2; OD-20 series list) |
| ENT-12 | **Session** | A Claude Code session: id (raw for the session cache name, sanitized for the mix cache — OD-03), owning status-line caches and rate-limit state | LEGACY-OBSERVED; raw/sanitized split DECIDED (OD-03) |
| ENT-13 | **Transcript Record** | JSONL `{type, subtype, timestamp, message{id, usage, content[]}}`; blocks text/thinking/tool_use/tool_result/image; 512 KB window, 256-id dedup | LEGACY-OBSERVED (P2r1 §2) |
| ENT-14 | **Status-Line Caches** | Session cache (`rl, rl_ts, fetch_ts, up, ts, sample, hist, proc_start`), mix cache (16 keys, `mixv6`), git cache (`{ts, branch}`), cost history (`sessions[sid] = {lane, usd, api_ms, ts, src}`) | LEGACY-OBSERVED (P2r1 §3); cache dir relocated DECIDED (OD-101, OD-95) |
| ENT-15 | **Configuration** | Typed, validated key registry: config file, overridden by `HYLO_*` env, then the key's default (PLAN §6: env overrides file); every key has type, range, rationale; errors are one-line degraded output (D4-EX-3) — except in the `--subagent` agent-panel mode, where a config error prints zero stdout bytes with the diagnostic on stderr (OD-168) | DECIDED (D15, OD-05, OD-102, OD-113, OD-114, OD-95, OD-168) |
| ENT-16 | **Profile** | A coherent config overlay selecting backend/routing per user (default) or per window via `--profile` (P6 option) | DECIDED (OD-51, OD-74) |
| ENT-17 | **Trust State** | The local CA (keypair, leaf certs) + its installation surface: `NODE_EXTRA_CA_CERTS` scoped to Claude Code; legacy also a login-keychain root (to be detected/removed) | LEGACY-OBSERVED; hylo shape DECIDED (D13, OD-41c) |
| ENT-18 | **Hook Decision** | Stop-hook outcome: allow, or block-with-context (language reminder, fake stop); rendered as `hookSpecificOutput` + a repr-grammar log line | LEGACY-OBSERVED (P2r2 §6.4-6.5) |
| ENT-19 | **Kev Verdict** | Median of ≤ 3 oracle calls, verdict `p < 0.40`; optional; regex fallback when absent | LEGACY-OBSERVED; optionality DECIDED (D11, OD-75) |
| ENT-20 | **Exporter State** | 19 keyed accumulators + 3 dict states + 5 scalars recomputed from the whole ledger + hook log; exposition is a pure function of (ledger bytes, hook-log bytes, TZ, session limit) | LEGACY-OBSERVED (CONV-ABS-13; P2r2 §5.1) |

## 2. Relationships and aggregates

- **Flow aggregate (ENT-06):** attribution + request/reply/usage/error are consistent
  within a flow; the ledger cannot express the grouping (near-key only) — the live
  event stream can (internal `flow_id`). [LEGACY-OBSERVED + DECIDED OD-25]
- **Session (ENT-12) 1—* Flow (ENT-06); Session 1—1 each cache of ENT-14; Session
  1—0..1 rate-limit snapshot state (ENT-08).** [LEGACY-OBSERVED]
- **Backend (ENT-09) 1—* Flow; Backend 1—0..1 Credential (ENT-10); Backend 1—*
  Health Samples (ENT-11).** Config declares N backend entries from the start;
  P1-P5 run with exactly one entry — zero or more than one is a config error until
  P6; P6 activates the fleet. [DECIDED OD-123]
- **Configuration (ENT-15) 1—* Profiles (ENT-16); Configuration parameterizes every
  capability.** [DECIDED D15]
- **Exporter State (ENT-20) is derived solely from Ledger Events (ENT-07) + hook log**
  — a rebuild-not-increment republish model. [LEGACY-observed; trigger detail DECIDED OD-39]

## 3. Value objects and enums

| Value object | Values / constraint | Provenance |
|---|---|---|
| Lane value | local / cloud / cloud-server-tools (proxy view); `dgx`/`anth`/None (client view) | LEGACY-OBSERVED |
| Routing decision code | R0..R5 (one per request) | LEGACY-OBSERVED |
| Freshness verdict | fresh / stale / dead, plus serving-down | LEGACY-OBSERVED (P2r3 §2) |
| Config scalar types | typed booleans (true/false/1/0/yes/no), number, duration s, URL, enum, list (comma-encoded in env) | DECIDED (OD-05, OD-74, OD-114) |
| Stop reason / stream stop reason | pass-through strings from the SSE tap; never invented | LEGACY-OBSERVED |
| Timestamps | ledger `t` = naive local, 1 s (D7); caches may carry NaN/Infinity tokens | LEGACY-OBSERVED |

All relationship claims and the Flow aggregate definition feed bounded-contexts.md
(BC3→BC4 boundary) and invariants.md (DI-005, DI-006).
