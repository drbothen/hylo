---
document_type: domain-spec-section
level: L2
section: "state-machines"
version: "1.5"
status: draft
producer: business-analyst
timestamp: 2026-11-18T02:41:14Z
phase: 1a
inputs: [.factory/specs/product-brief.md, .factory/semport/hylo-legacy/hylo-legacy-pass-8-deep-synthesis.md, .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r4.md, .factory/semport/hylo-legacy/hylo-legacy-pass-2-deep-domain-r8.md, .factory/specs/owner-decisions-log-2026-11-14.md]
input-hash: "1d0cf11"
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

Evaluation order per refresh mirrors the PRD error taxonomy (E-CLI-001 outranks
E-CFG-001): **(1) unknown-flag line (OD-112)** — checked first among render-ladder
rungs (the `--subagent` mode-routing check precedes all flag handling; see the
carve-out below); **(2) config-error
line (D4-EX-3, OD-102)** — checked at step 0, before any render; **(3) render
success, else the degraded one-line fallback**. Terminal for that refresh: every
refresh starts fresh; the ladder always ends exit 0 with at least one line (DI-008) —
except in the `--subagent` agent-panel mode (carve-out below).
Legacy conflated the config-error and unknown-flag conditions — both surfaced as
crash/import paths; hylo splits them into distinct rungs (DECIDED).

Carve-out — `--subagent` agent-panel mode (OD-155): membership of `--subagent`
anywhere in `argv[1:]` routes to the agent-panel renderer before any flag handling,
including the unknown-flag check (legacy SL:1240-1241; BC-1.07.001). Inside that mode the
ladder does not apply: the output is JSON lines or zero bytes — zero tasks
(BC-1.07.004 PC6), unparseable stdin (BC-1.07.003), enabled=false (BC-1.07.002 PC2)
and config errors (OD-168: zero bytes on stdout, diagnostic on stderr) each print
nothing on stdout — always exit 0.

## SM-05 Backend health freshness ladder

States: **fresh → stale → dead**, plus **serving-down** as an overlay verdict
(fetched OK, data says the server is down). Driven by fetch attempts + TTL and the
"5 min of last-known telemetry" rule (OD-57 E-A); NaN samples are kept as floats, as
in legacy (ADV-P1-A2-02; CP-N01/N02) — those NaN values drive the catalogued crash
paths, reproduced per BC-1.04.014..016. +Inf/-Inf handling: P1 reproduces legacy
behaviour per BC-1.04.014 (+Inf degrades the sample, -Inf clamps to `▁`);
OD-130's treat-as-unknown rule takes effect only from P6 (DECIDED OD-157), with the
confirming owner capture (one real metrics response, read-only) deferred until the
owner confirms the backend soak has been scored. [LEGACY-OBSERVED P2r3 §2; sampling config DECIDED
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
