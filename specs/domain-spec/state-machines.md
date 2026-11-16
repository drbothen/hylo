---
document_type: domain-spec-section
level: L2
section: "state-machines"
version: "1.0"
status: draft
producer: business-analyst
timestamp: 2026-11-15T21:30:00Z
phase: 1a
inputs: [.factory/specs/product-brief.md, .factory/semport/hylo-legacy/hylo-legacy-pass-8-deep-synthesis.md, .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r4.md, .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r8.md, .factory/specs/owner-decisions-log-2026-11-14.md]
input-hash: "600cb42"
traces_to: L2-INDEX.md
---

# State Machines (SM-NNN)

> Lifecycles the domain distinguishes. Legacy transitions are LEGACY-OBSERVED; hylo
> deltas are DECIDED. Implementation states (locks, sockets, ports) belong to
> architecture, not here.

## SM-01 Routing decision (per eligible request)

States: **R1 not-intercepted → R2 unparseable → R3 cloud → R4 server-tools → R5
local** (R0 bridge-WS dead in production, CONV-ABS-26).
Exactly one terminal state per request; no transitions after the decision (DI-001).
R4 and R5 differ only in destination (cloud vs local); an R2 body passes unrewritten
and produces no lane events. `count_tokens` rides R3/R5 per OD-10.
[LEGACY-OBSERVED P2r2 §4.2; amended D13/OD-10]

## SM-02 Proxy process lifecycle

Legacy [LEGACY-OBSERVED P2r4 §3.1 *Addon generation*]: per-window child; addon
generations: loaded → raising-in-hook → absent-after-failed-reload (silent plain
pass-through); startup import failure exits. hylo [DECIDED OD-66/OD-50/OD-38/OD-26]:
one detached per-user proxy: `starting → serving → draining → stopped`, with client
registration and configurable idle stop (`serving ⇄ draining`), restart on demand;
**no pass-through degradation state exists** (DI-011); invalid startup config refuses
to start (DI-010); SIGHUP treated as SIGTERM with bounded drain and one error event
per remaining flow. Registration semantics (DECIDED OD-128): registration =
launch-time claim + periodic heartbeat in the state file; liveness = heartbeat
freshness; the exact mechanism is a P4 architecture detail. The domain commitment:
a client can die without taking the proxy down.

## SM-03 Upstream connection acquisition

Legacy [LEGACY-OBSERVED P2r4 §1.1-1.3]: eager connect at tunnel open; ≤ 5
connections/address/tunnel; failed connect cached for the tunnel's life; ALPN
mirrored (h1 client → h1 upstream). hylo [DECIDED OD-17/OD-94]: lazy per-lane
connects acquired **after** routing; reconnect on stale keep-alive only when nothing
sent; lanes never coupled; h1 pinned explicitly on both legs (listener and upstream).
Pass-through destinations acquire connections on demand under the same per-lane rule
— connect-on-demand everywhere, no eager upstream connect anywhere (DECIDED OD-129).

## SM-04 Status line render ladder

States: **clean render → degraded one-line (exception) → config-error line
(D4-EX-3, OD-102) → unknown-flag line (OD-112)**. Terminal for that refresh: every
refresh starts fresh; the ladder always ends exit 0 with at least one line (DI-008).
Legacy lacks the middle/hydration distinction between config-error and unknown-flag
lines (both existed as crash/import paths) — hylo splits them (DECIDED).

## SM-05 Backend health freshness ladder

States: **fresh → stale → dead**, plus **serving-down** as an overlay verdict
(fetched OK, data says the server is down). Driven by fetch attempts + TTL and the
"5 min of last-known telemetry" rule (OD-57 E-A); NaN semantics per VictoriaMetrics
documentation (CP-N01/N02) — NaN samples are dropped; +Inf/-Inf samples are treated
as unknown, like a stale sample (defensive parse) — DECIDED OD-130, with the
confirming owner capture (one real metrics response, read-only) deferred until the
owner confirms the backend soak has been scored; until then the defensive rule
stands. [LEGACY-OBSERVED P2r3 §2; sampling config DECIDED
OD-57]

## SM-06 Turn and composition state (status line)

Per session: **closed turn → open turn → (compaction boundary resets composition and
`pp` only) → rebuild counting (`↻n`) at 20,000 excess-write threshold**; wrong-shape
transcript lines are skipped, never poisoning state (D4-EX-2, OD-21/OD-32).
Poisoned legacy caches: treated as no open turn when `cur.t0` is numeric (OD-32).
[LEGACY-OBSERVED P2r1 §2.3, §8; deviations DECIDED]

Formerly open state-machine deltas now decided: SM-02's registration semantics
(OD-128) and SM-05's Inf handling (OD-130); resolutions recorded in
owner-validation-list.md (resolved 2026-11-15).
