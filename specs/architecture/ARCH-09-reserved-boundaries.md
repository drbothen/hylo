---
document_type: architecture-section
level: L3
section: "reserved-boundaries"
version: "1.0"
status: draft
producer: architect
timestamp: 2026-11-16T00:00:00Z
phase: 1b
inputs: [prd.md, research/peer-tool-lessons-2026-11-14.md, semport/hylo-legacy/statusline-target-design.md]
traces_to: ARCH-INDEX.md
input-hash: "d7ab04e"
---

# ARCH-09 — Reserved package boundaries (P2-P7), no design

> Packages named in PLAN §6 for later phases. Boundaries only: the P1 skeleton must
> not block them. Each row lists the known constraints the skeleton must respect.

| Package (future) | Phase | Known constraints the P1 skeleton must not block |
|---|---|---|
| `internal/exporter` | P2 | Metric names, labels and values match the Python exporter on the same ledger file (D7); separate exporter oracle `/usr/bin/python3` 3.9.6 empty env (OD-15) — the harness interpreter setting is status-line-specific and must not be reused as the exporter oracle pin |
| `internal/proxy` | P3 | D13 intercept-all-Claude-traffic (rewrite surface only `POST /v1/messages` + `count_tokens` on api.anthropic.com; CA unconstrained, trusted only via `NODE_EXTRA_CA_CERTS`, never an OS store); D14 no proxy env leakage to children; HTTP/1.1-only explicit on both transports with `proxy.http2.enabled` default off (OD-94); connect-on-demand, never-couple-lanes (OD-17, OD-129); WebSocket passthrough + SSE flush; loop detection (peer lesson L4); binding loopback by default (DI-015); ledger writes honor D7 field order — P1's pyfmt `Strftime` reservation supports the ledger `t` field |
| `internal/ledger` | P3 | Append-only JSONL, one `write()` per line, event set and field order frozen until P7 (D7, DI-005); consumers never assume request-reply pairing (DI-006); status line never reads the ledger (DI-007, OD-125, REVISIT P7) |
| `internal/run` / `internal/hook` / `internal/doctor` / `internal/ca` | P4 | `hylo run` shim sets env on the claude process only (D14 mechanism (f)); SessionStart unset hook via `CLAUDE_ENV_FILE` (D14 (a)); hylo-owned commands construct HTTP clients with `Proxy: nil` (D14 (b) — the P1 metrics client already does this, keeping it the precedent); doctor reports residual leaks; CA key protection (directory 0700 / key 0600 / NTFS DACL, DPAPI option), rotation, no `trust install` port by default (peer report §2.2); OD-11: doctor detects legacy mitmproxy CA in login keychain |
| `internal/events` (shared feed) | P3/P4 | One live event stream feeds ledger writer and UIs (D16); request bodies in memory only, credentials redacted (DI-016) |
| `internal/ui` (+ `web/`) / `internal/top` | P4/P6 | UIs are live + in-memory ring buffer only (OD-122); ring-buffer size is a config key (D15); bound to localhost with per-launch access token; `go:embed` of the built web app, Node is build-time only (D16); UI states where its history begins |
| `internal/multibackend` (fleet activation) | P6 | N backends in config (name, url, protocol flavor, credential, CA, routing rules) — the P1 `backends[0]` validator function is the only code to widen (OD-123); per-backend passthrough/credential options P6-gated (OD-06/OD-07); opt-in cloud failover with status-line indicator (peer lesson L6, OD-127); telemetry sources pluggable, cost basis configurable (OD-13: prices in config by model pattern) |

Boundary rules for the P1 skeleton:

1. No reserved-subsystem names may be imported by the P1 render path (and none exist
   yet — the registry collision test keeps the key namespace clean for
   `routing.*`, `proxy.*`, `paths.ledger`, `ui.*` key families already ruled).
2. The config registry `Class` field and `LoadOptions.FileLayer` extension point are
   the only P4 seams pre-provisioned (OD-107); `backends[]` widening happens in one
   validator (OD-123).
3. DI-007 (status line never reads the ledger) is enforced architecturally in P1 by the
   read-scope of `Env` (ARCH-03) having no ledger seam at all.
4. Peer-lesson dispositions that touch P1 bytes: none — L1-L6 all land P3/P4/P6; the
   P1 metrics client's `Proxy: nil` transport is D14-(b) precedent, output-neutral.

OD-1 and OD-2 (peer report; now D13/D14 in PLAN §10) constrain P3/P4 as listed; they
impose no P1 byte constraints beyond the transport precedent above.

## Mapping

No BCs this cycle (reserved subsystems S7-S12, PRD §1.6). Serves story-writer guard:
no P1 story may create reserved-package code; Feature Mode brings the phase detail.
