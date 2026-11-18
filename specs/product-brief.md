---
document_type: product-brief
level: L1
version: "1.2.7"
status: draft
producer: product-owner
timestamp: 2026-11-22T02:00:00Z
phase: 1a
inputs:
  - CLAUDE.md
  - docs/PLAN.md
  - .factory/specs/research/domain-hybrid-routing-claude-code-2026-11-14.md
  - .factory/planning/market-intel.md
  - .factory/specs/owner-decisions-log-2026-11-14.md
input-hash: "64f7f9d"
traces_to: docs/PLAN.md
---

# Product Brief: hylo

## What Is This?

hylo is one static Go binary (one per OS) that gives a single Claude Code session two lanes:
requests for chosen models (routing rules in config) run on the user's own AI hardware, the
rest go to Anthropic — switched per request by an invisible TLS-intercepting proxy, with a
status line showing which lane served what. It replaces a hand-built Python/mitmproxy stack
with one cross-platform binary and one config file, and is described as "for Claude Code —
not affiliated with Anthropic" (D1, D6; CLAUDE.md; docs/PLAN.md §1).

**Scope ruling (owner, 2026-11-15):** this brief and the L2 domain spec are product-level —
they describe all of hylo. The PRD, behavioral contracts, verification properties, and
architecture detail produced in this Phase 1 cycle specify **P1 (the status line) only**;
later phases enter the pipeline individually via Feature Mode.

## Who Is It For?

| Persona | Pain Point | Current Workaround |
|---------|-----------|-------------------|
| PRIMARY — the owner: a Claude Code subscriber with a dedicated local inference server (vLLM-class) on the LAN, who wants some models served locally inside the same session | Local models in Claude Code today mean an `ANTHROPIC_BASE_URL` gateway (which disables Claude Code Remote Control) or a hand-built Python/mitmproxy stack: one proxy per window, ~25 environment variables, macOS-only (hybrid-routing research §1.1–1.2; PLAN §3–4) | The Python prototype (`legacy/`), in daily production use |
| SECONDARY (arrives in P6) — other Claude Code users with local inference (llama.cpp, Ollama, LM Studio, SGLang) | Want hybrid routing without losing Remote Control | Base-URL gateways (lose Remote Control) or nothing |

## Scope

Capability areas below are product-level, not features; Phase 1 decomposes them into numbered
requirements (this cycle: P1 scope only).

### In Scope

- Per-request lane routing through the invisible TLS-intercepting proxy, intercepting all
  Claude Code traffic (D13) with no proxy settings leaking to child processes (D14);
  Remote Control keeps working (D6).
- The lane-aware status line.
- Custom agent-panel rows in the status line via its `--subagent` mode (ported into P1
  scope by owner ruling OD-155, 2026-11-17, superseding OD-14; contracts BC-1.07.*).
- The append-only JSONL ledger and Prometheus exporter; ledger format and metric names frozen
  until P7 (D7).
- Launcher (`hylo run`), Stop hook, `doctor`, and local-CA management (`hylo ca`).
- One config file with profiles: typed, validated keys with documented rationale; config file
  → `HYLO_*` override → default; no `DGX_*` aliases (D15, OD-05); explicit per-OS paths (OD-95).
- Any Anthropic- or OpenAI-compatible backend as the local lane (lands in P6).
- A web UI and a terminal UI reading one live event feed from the proxy (D16).

### Out of Scope

- The GPU-serving side: vLLM/LMCache launchers, VictoriaMetrics rules, Grafana dashboards,
  benchmarks (they remain in the private home-lab repository as one example backend).
- Kev (the fake-stop model) — enters only as an optional external URL for the Stop hook (D11).
- The visible `ANTHROPIC_BASE_URL` router — history only (D6).
- Reading the Claude.ai OAuth token for usage widgets (market-intel R7).

## Success Criteria

| Outcome | Metric | Target |
|---------|--------|--------|
| Parity (P1–P3, D4) | Unexplained byte/decision diffs vs `legacy/` over the full fixture corpus plus the owner's recorded real inputs — the synthetic corpus replayed in CI on all 3 OSes, the owner's recorded inputs replayed locally on the owner's Mac (captures are git-ignored and never leave it) | 0; differences only via the closed exclusion set pinned in BC-6.03.004 (rulings OD-105, OD-110) |
| Status line speed (P1) | p95 wall time per render on the owner's Mac over the fixture corpus, excluding the metrics HTTP wait | <= 25 ms (measured legacy baseline 2026-11-15: median 84.5 ms, p90 101 ms on a synthetic input — no transcript, metrics fetch failing fast — of which ~25 ms is interpreter start) |
| Cutover (P5) | Owner's windows on hylo; rollbacks during the 2-week rollback window | 100% of windows on hylo; 0 rollbacks |
| Proxy overhead (P3) | Deferred — measure the prototype first, then set the number in Feature Mode | No baseline yet |

Notes:

- Parity: "unexplained" means anything not on the closed exclusion set of BC-6.03.004
  (D4-EX-1, D4-EX-2, D4-EX-3, OD-30, OD-76, temp-file, cp-x03, OD-159, OD-160, OD-161,
  OD-166, OD-181);
  every exclusion carries its own table tests (OD-105, OD-110, OD-169, OD-181). Rationale: D4 — parity is
  the definition of done for P1–P3.
- Speed: a labeled JUDGMENT CALL (target ≈3× faster; a static binary removes interpreter
  start). CI reports per-OS timing, but the target binds only on the owner's Mac. The one
  exception is stated here and in the spec: the large-transcript fixture — the one corpus
  case whose transcript exceeds 524,288 bytes (512 KiB), however many lines it holds — is
  exempt from the 25 ms p95 target, but its p95 must be at most 100 ms — the ceiling
  fails when p95 > 100.0 ms (OD-191; 4× the
  target, well under the refresh interval).
- Cutover: "0 rollbacks" is a labeled judgment call; PLAN P5 keeps the Python prototype
  runnable for 2 weeks as the rollback path.
- What P1 success means: byte parity on the owner's real recorded inputs plus the synthetic
  fixture corpus in CI; daily live use starts at the instant P5 cutover (OD-96 as amended by
  OD-107).

## Constraints & Integration Points

- Go >= 1.26; Go standard library first (`crypto/tls`, `net/http`, `httputil`); every
  dependency needs a stated reason (PLAN §6).
- macOS, Linux, Windows from day one (D5); OS-specific code confined to `internal/platform`.
- Invisible mode only (D6): the client keeps pointing at `api.anthropic.com`; trust via
  `NODE_EXTRA_CA_CERTS` scoped to the Claude Code process; only `POST /v1/messages` and
  `POST /v1/messages/count_tokens` are ever rewritten (D13); Remote Control bridge traffic
  passes through unchanged.
- Parity first (D4): the Go port reproduces `legacy/` behavior on recorded inputs before any
  behavior change or generalization.
- Config over code (D15): no magic numbers or hard-coded hosts/models/prices in logic; hylo's
  cache location uses its real OD-95 path from P1 (OD-101, explicit owner exception to
  "defaults equal legacy/ until cutover" for that key).
- Public-repo hygiene (D2): synthetic or script-scrubbed test fixtures only; no personal or
  infrastructure details in content or history; no "Claude" in the name or logo.
- Distribution: GitHub Releases first; Homebrew tap / Scoop / `go install` as follow-ups (D12).
- Binding decision set, cited not restated: D1–D16 (docs/PLAN.md §2, §10) and the owner
  decision log (`.factory/specs/owner-decisions-log-2026-11-14.md`): OD-05 (env/config
  surface), OD-95 (paths), OD-96 as amended by OD-107 (P1 success criterion), OD-101 (cache
  path from P1).

## Overflow Context (Optional -- Reference Only)

### Phase plan (docs/PLAN.md §7 — parity first, D4)

| Phase | Work | Exit criterion |
|---|---|---|
| P0 | Repo + scrubbed history, license, README, CI matrix (macOS/Linux/Windows), release tooling | Owner approves scrub report; CI green on all 3 OSes |
| P1 | `hylo statusline` — lowest risk: the render reads stdin, transcript, metrics, its own caches and the environment seams (AD-03), never the ledger | Golden tests: Python and Go render byte-identical output for recorded stdin fixtures and real transcripts (incl. compaction, >512 KB lines, rebuilds) |
| P2 | `hylo exporter` | Same metric names, labels, values as the Python exporter on the same ledger file |
| P3 | `hylo proxy` — the hard part; internal event stream (feeds ledger now, UIs later) | Recorded-request replay: identical routing decisions (as data), rewritten bodies, ledger lines vs the Python addon |
| P4 | `hylo run`, `hook stop`, `doctor`, `ca`, `ui` (web UI, D16) | A full working session on each OS; Remote Control works |
| P5 | Full cutover, no shadow week; Python kept runnable 2 weeks for rollback; migration table from the env inventory | 2 weeks without rollback; dashboards unchanged (D7) |
| P6 | Generalize: backends in config (Anthropic-/OpenAI-compatible), routing rules in config, pluggable telemetry, configurable cost basis; `hylo top`; `hylo cost backfill` | A second example backend (e.g. Ollama on a laptop) works end to end with only config |
| P7 | Redesign ledger and metrics (D7, after it works) | Owner-approved new schema + migration for the dashboards |

### Prior art

- `legacy/` — the frozen Python prototype under version control until cutover (D10); the
  parity oracle for P1–P3, removed at cutover.
- Base-URL routers — all lose Remote Control since Claude Code 2.1.196 (hybrid-routing §1.1):
  musistudio/claude-code-router (~38k stars), LiteLLM (~63k), 1rgs/claude-code-proxy,
  fuergaosi233/claude-code-proxy, luohy15/y-router (archived).
- Endpoint-preserving interceptors, hylo's actual peer group (§1.2): closest peer
  cablate/model-relay (HTTPS-proxy mode with local CA; reports Remote Control works);
  KarpelesLab/teamclaude (most detailed Remote Control pass-through path list; its
  account-rotation use is the pattern Anthropic's Usage Policy targets — do not copy that
  pattern); peter-wagstaff/claude-hybrid-router; Screddyice/backdoor; aeroxy/claude-proxy;
  CLIProxyAPI + community mitmproxy sidecar.
- Status line peers (market-intel §1): claude-hud (28.9k stars), ccusage statusline (19.4k),
  ccstatusline (13.6k), CCometixLine (3.5k), claude-powerline (1.2k). The one existing
  lane-aware indicator is the model-relay + coralline pair — a window-level pill without
  backend telemetry.
- Differentiation cluster with no observed occupant in any surveyed tool (market-intel §4;
  absence-of-evidence over READMEs/docs checked 2026-11-15): the backend telemetry strip
  (health/queue/KV/throughput/TTFT/power from a metrics store), owned-hardware `⛏` cost with
  per-lane percentile-from-history cost colors, composition-bytes and `⌂` window-age widgets.
  NOT differentiators — do not claim: the lane pill (model-relay + coralline exists),
  pace-projected plan-limit coloring (three peers ship it), "single Go binary" alone.
- Positioning (OD-97, approved in principle; written at P6): lead claim "lane-aware with
  backend telemetry and owned-hardware cost"; an honest Alternatives section crediting
  model-relay + coralline and the incumbents; never "first/only".

### Business frame

Personal/community open-source tool, Apache-2.0 (D8), no revenue model; adoption potential is
proxied by peer star counts (no TAM figures asserted). Market intelligence assessment
2026-11-15: GO with high confidence (`.factory/planning/market-intel.md`).

### Deferred

- Proxy-overhead success number: set in P3 via Feature Mode after measuring the prototype
  (no baseline exists yet).
