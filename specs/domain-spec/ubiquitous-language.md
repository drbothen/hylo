---
document_type: domain-spec-section
level: L2
section: "ubiquitous-language"
version: "1.6"
status: draft
producer: business-analyst
timestamp: 2026-11-18T05:40:00Z
phase: 1a
inputs: [.factory/specs/product-brief.md, .factory/semport/hylo-legacy/hylo-legacy-pass-8-deep-synthesis.md, .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r4.md]
input-hash: "5bdadee"
traces_to: L2-INDEX.md
---

# Ubiquitous Language

> The domain's vocabulary with the legacy→domain term mapping. Wire names (`dgx_*`,
> `anth_*`) are D7-frozen; domain terms are what specs and UIs use. Disputed terms →
> owner-validation-list.md.

## 1. Core domain terms

| Term | Definition | Provenance |
|------|-----------|------------|
| **Lane** | Where a request is served: local lane or cloud lane (cloud lane/server-tools for R4). Client-view lane (`dgx`/`anth`/None) is inferred by the status line from stdin `model.id`, and may differ in certainty, not in truth, from the proxy's decision | P2r4 §3.1; client-view lane as distinct derived value DECIDED (OD-121); server-tools naming DECIDED (OD-119) |
| **Local lane** | Requests served by the backend. Legacy wire name: `dgx_*` events, implicit (no `lane` key) | LEGACY-OBSERVED |
| **Cloud lane** | Requests served by Anthropic. Legacy: `anth_*` events, `lane: "anthropic"` | LEGACY-OBSERVED |
| **Cloud lane/server-tools** | R4 server-tool requests routed to Anthropic — a sub-outcome of the cloud lane, not a third lane. Legacy logs `lane: "anthropic-server-tools"` | LEGACY-OBSERVED; naming DECIDED (OD-119) |
| **Backend** | The user's local inference server (legacy: "the DGX"). N backend entries in config from the start; exactly one validated entry through P5; fleet activated at P6 | LEGACY-OBSERVED; term DECIDED (OD-120); config/fleet model DECIDED (OD-123) |
| **Backend health** | Fresh/stale/dead + serving-down overlay, from the metrics store | LEGACY-OBSERVED (SM-05) |
| **Invisible mode** | Client keeps addressing the cloud host; a TLS-intercepting proxy routes per request; RC survives (D6) | DECIDED D6 |
| **Routing decision** | R0-R5; the per-request lane outcome (SM-01) | LEGACY-OBSERVED |
| **Prefix rule** | Case-sensitive `startswith` on the requested model id; the only routing key through P5; config rules from P6 | LEGACY-OBSERVED; generalization DECIDED OD-111 |
| **Served model / requested model** | `model_served` field actually records the REQUESTED model (frozen naming trap, AP-6); the served alias is the name the backend knows | LEGACY-OBSERVED AP-6 |
| **Attribution** | The (project, user, session, ...) tuple copied into reply/error events | LEGACY-OBSERVED |
| **Near-key** | Composite correlation key `(session, path, model_req, req_bytes)` ±1 s — ambiguous on client retries | LEGACY-OBSERVED (P2r4 §3.3) |
| **Flow / flow_id** | One request + outcomes; exact correlation via the internal event stream only | DECIDED OD-25 |
| **Ledger** | The append-only JSONL of 13 legacy-named events (D7-frozen) | DECIDED D7 |
| **Degraded line / ladder** | One-line output, exit 0, for any fault (DI-008); the degraded line itself is exactly 29 bytes (BC-1.01.001) — the config-error and unknown-flag rungs render longer lines. Carve-out: the `--subagent` agent-panel mode (OD-155) prints JSON rows on success and zero stdout bytes for zero tasks, unparseable stdin, enabled=false and config errors (OD-168: diagnostic on stderr); a catalogued render fault there (CP-A01..A05) still reaches the ladder's bottom rung — the same 29-byte line (BC-1.07.008) | LEGACY-OBSERVED + DECIDED OD-102/OD-155/OD-156/OD-168 |
| **Config-error line** | `hylo: config error: <key>=<value> (<reason>)`, exit 0 (D4-EX-3) | DECIDED OD-102 |
| **Widget** | One status line visual element with rule-level tests | LEGACY-OBSERVED (STATUSLINE-WIDGETS) |
| **Freshness ladder** | fresh/stale/dead + serving-down (SM-05) | LEGACY-OBSERVED |
| **Fake stop / Kev / verdict** | Optional Stop-hook oracle mediating turn completion; median-of-3, `p < 0.40`; regex fallback | LEGACY-OBSERVED; optional DECIDED D11 |
| **Composition** | Byte-share of context since the last compaction boundary (`▤❙◈`) | LEGACY-OBSERVED |
| **Plan window** | The 5h/7d subscription usage windows, computed by the status line from stdin `rate_limits` when a refresh carries them, else from the session cache's last-seen `rl` (shown-unless-stale, kept RL_KEEP = 1800 s, legacy `effective_rl` SL:297-312) — captured headers stay in the ledger (ADV-P2-A2-19, ADV-P5-A2-27) | LEGACY-OBSERVED |
| **Approved deviation / exclusion list** | Named, individually tested byte differences vs the oracle; the closed id set is D4-EX-1, D4-EX-2, D4-EX-3, OD-30, OD-76, temp-file, cp-x03, OD-159, OD-160, OD-161, OD-166 (BC-6.03.004) | DECIDED OD-105/OD-110/OD-136, OD-169 |
| **Parity** | Byte/decision equality with the frozen prototype on recorded inputs; definition of done P1-P3 (D4) | DECIDED D4 |
| **Rebuild (exporter)** | Full rescan of ledger + hook log into exporter state | LEGACY-OBSERVED; trigger DECIDED OD-39 |
| **Exposition** | The 28-name Prometheus text rendering on `/metrics` | LEGACY-OBSERVED |
| **Owned-hardware cost (`⛏`)** | Cash cost of serving on the local lane vs list-price cloud cost | LEGACY-OBSERVED |
| **Percentile bands** | Personal p75/p95 per-lane cost colors from 30-day history | LEGACY-OBSERVED |

## 2. Legacy → domain term mapping

| Legacy (`legacy/`) | Domain term | Notes |
|---|---|---|
| "the DGX", `DGX_UPSTREAM`, `DGX_KEY_FILE`, `DGX_SERVED_MODEL` | Backend (url, credential, served model alias) | Fleet from P6 (DECIDED OD-123) |
| `dgx_*` events, `dgx` lane value | Local-lane events / local lane | Wire names frozen (D7) |
| `anth_*` events, `anth` lane value | Cloud-lane events / cloud lane | Wire names frozen (D7) |
| `LOCAL_MODEL_PREFIXES` | Prefix rule → `backends[0].model_prefixes` | OD-111 default `claude-sonnet`; key lives under the backend entry per OD-123 (supersedes top-level singleton placement) |
| `claude-dgx` (launcher) | `hylo run` | OD-115 product surface |
| `dgx_preflight.py` | `hylo doctor` | CAP-014 |
| `dgx_proxy.py` trust CLI | `hylo ca` | CAP-014 |
| `tools/backfill_cost_history.py` | `hylo cost backfill` | P6 |
| `~/dgx-llm-obs.jsonl` | `paths.ledger` | D15 key |
| `--subagent` / `subagentStatusLine` | Agent-panel status-line rows, ported in P1 (config off switch) | OD-155 (supersedes OD-14); CAP-009 |

## 3. Overloaded-term disambiguation (canonical readings)

- **Session** — Claude Code's `session_id`; raw form for the session-cache file name,
  sanitized for the mix cache (OD-03). Never the same thing as a Claude.ai account or
  an OS user (DECIDED OD-118, OD-120).
- **Window** — always qualified: **plan window** (5h/7d usage), **client window** (a
  terminal window running the client; legacy had one proxy per client window),
  **process-age window (`⌂`)**: the age of the client process behind the status line,
  surviving `/clear` (DECIDED OD-118).
- **Cache** — always qualified: **prompt-cache fields** (usage fields in events:
  cache_read_tok et al., distinct from files), **status-line caches** (the session,
  mix, git, and cost-history files), **leaf cache** (CA certificates), **cost
  history** (the shared per-session cost file; ownership DECIDED OD-124: a
  status-line-owned shared artifact — the status line owns the format; `cost
  backfill` and the one-time cutover copy (OD-106) honor it as guests).
- **Cache fields** — prompt-cache usage fields in events (cache_read_tok etc.);
  distinct from status-line caches. Cache-write 5m value is derivational on streams
  (EVT-07 note).
- **Lane (client view)** — the status line's `dgx`/`anth` inference; modeled as a
  distinct derived value object — widgets state which view they render (DECIDED
  OD-121). The proxy decision stays authoritative for ledger/BC8 history.
