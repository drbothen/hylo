# hylo — migration plan (approved 2026-11-14)

Break `claude-dgx` and all of its client-side components and documentation out of
the owner's private home-lab repository into a new **public** repository, **`github.com/drbothen/hylo`**;
rewrite it in **Go**; make it **configurable**; and generalize it from "the DGX" to
**any local AI backend**. Approved by the owner on 2026-11-14; Phase 0 (this repository, with its scrubbed history) was executed the same day.

## 1. The name

**hylo** — pronounced **HY-loh** (/ˈhaɪ.loʊ/).

**Etymology.** A coined blend of **hy**brid + **lo**cal: one Claude Code session whose
requests run partly on your own hardware (the local lane) and partly at Anthropic (the cloud
lane), switched per request. The name was chosen on 2026-11-14 after three rounds
(lane / railway / road metaphors, then short words, then coined words); the runners-up were
`byway` (a side road off the main highway) and `locum` (a substitute doctor standing in for
the regular one).

It also echoes the Greek **ὕλη (*hýlē*)**: "wood, timber", and in philosophy "matter, the
physical stuff" (as in *hylomorphism*, form + matter). That resonance is a bonus rather than
the source: hylo is about running models on your own *matter* — the machine in the room.

Checks (2026-11-14): no collision with any command, shell builtin or Homebrew formula on
the owner's machine; `drbothen/hylo` free; ~500 GitHub repositories use the word, none as a
Claude Code router. The word "Claude" is deliberately absent from the name (public project,
Anthropic trademark); the README will say "for Claude Code — not affiliated with Anthropic".

## 2. Decisions already made (owner, 2026-11-14)

| # | Decision |
|---|---|
| D1 | Name `hylo`; repo `drbothen/hylo`; Go module `github.com/drbothen/hylo`; binary `hylo` |
| D2 | **Public** repository |
| D3 | **Carry over these files' git history**, minus secrets and personal/infrastructure details (§5) |
| D4 | **Parity first**: port to Go with identical behavior, validate against the Python version, *then* generalize |
| D5 | Platforms: **macOS, Linux, Windows** |
| D6 | **Invisible mode only** (TLS-intercepting proxy; keeps Claude Code Remote Control working). The visible `ANTHROPIC_BASE_URL` router (`opus_router.py`) is not ported |
| D7 | **Keep the ledger format and metric names** to start (existing Grafana boards keep working); redesign after hylo works |

## 3. Goals and non-goals

**Goals:** one static `hylo` binary per platform; one config file instead of ~25 env vars;
behavior identical to `claude-dgx` at cutover (proven by side-by-side tests); then any
Anthropic-compatible local server (vLLM, SGLang, llama.cpp) and OpenAI-compatible ones
(Ollama, LM Studio, …) as backends.

**Non-goals (for now):** the GPU-serving side (vLLM/LMCache launchers, VictoriaMetrics rules,
Grafana dashboards, benchmarks — they stay in the private home-lab repository as one example backend); Kev (the
fake-stop model — an optional external URL, not part of the move); the visible router (D6);
Claude Code's custom agent-panel rows (removed in Claude Code 2.1.323 — not ported).

## 4. Scope — what moves, and what each becomes

| Today (private home-lab repo) | Lines | Becomes in hylo |
|---|---|---|
| `claude-dgx` (zsh launcher: settings, headers, profiles, safe/sandbox modes) | 185 | `hylo run` (+ `hylo` config profiles) |
| `dgx_proxy.py` (mitmproxy addon: TLS interception, routing, request normalization, SSE usage tap, ledger, `anth_ratelimit`) | 764 | `hylo proxy` — Go TLS-intercepting proxy, **one per user** (today: one Python proxy per window, 8 running) |
| `dgx-proxy-coordinator.sh` (singleton/port discovery) | 50 | built into `hylo proxy` / `hylo run` |
| `dgx_statusline.py` (two-row status line, cost history) | 1,245 | `hylo statusline` |
| `tools/backfill_cost_history.py` | 121 | `hylo cost backfill` |
| `dgx_ledger_exporter.py` + 2 LaunchAgents (`ssh -R` tunnel) | 414 | `hylo exporter` + per-OS service units (launchd / systemd user unit / Windows scheduled task) |
| `auto_continue.py` (Stop hook: fake-stop via Kev, regex fallback, English policing) | 275 | `hylo hook stop` (Kev = optional config URL) |
| `dgx_preflight.py` (reachability / macOS Local Network check) | 41 | `hylo doctor` |
| Docs: `STATUSLINE-WIDGETS.md`, `STATUSLINE-REVIEW-2026-11-13.md`, client parts of `OBSERVABILITY-*.md`, `ROLLBACK.md` | — | `docs/` in hylo (reference, decisions, config reference) |
| `opus_router.py` (visible mode) | 230 | history only (D6) |

## 5. Phase 0 — repository and history (scrubbed)

**Measured 2026-11-14:** 18 of the source repository's 82 commits touch the files above (first:
2026-11-10). A scan of **every historical version** of them found:

| Category | Found | Action |
|---|---|---|
| API keys, tokens, bearer values (`sk-ant-…`, `Bearer …`, `key/token/secret = "…"`) | **0** | still re-scanned with gitleaks + trufflehog after rewriting (belt and braces) |
| Private LAN IP address | 18 lines | replace with `192.0.2.10` (RFC 5737 documentation range) |
| Owner's username / home path / LaunchAgent labels | 10 + 1 + 9 lines | replace with `user`, `$HOME`, `io.hylo.*` |
| A client project name | 1 line + 1 commit message | replace with `project-a` |
| Commit author email (owner's personal address) | all 18 commits | rewritten to the GitHub no-reply address via `--mailmap` (D9) |
| Account hashes, DGX hostname | 0 | — |
| Utility name revealing the owner's region (docs) | 2 lines | replace with `local utility` |
| Links to the owner's private Claude sessions (commit messages) | 5 | removed |

**Procedure:**
1. Fresh clone of the source repository into a scratch directory (never the working copy).
2. `git filter-repo --path …` keeping only the files in §4 (with `--path-rename` into the new
   layout, Python under `legacy/`), plus `--replace-text` (the table above) and `--mailmap`.
3. Verify the rewritten history: gitleaks, trufflehog, and the same pattern scan as above
   must all return **0**; every commit message re-read for project names.
4. **Scrub report to the owner** (done 2026-11-14: gitleaks and trufflehog clean, every pattern 0 in content, messages and identities) (counts before/after, every replaced pattern, file list,
   commit list) — **push only after approval**.
5. Create `drbothen/hylo` (public), add `LICENSE` (owner decision, §10), README stating
   "for Claude Code — not affiliated with Anthropic", push the history.

## 6. Architecture of hylo (Go)

- **One binary, subcommands:** `run`, `proxy`, `ui`, `top`, `statusline`, `exporter`, `hook stop`,
  `doctor`, `ca` (create/install/rotate the local CA), `cost backfill`, `config` (show/validate).
- **Layout:** `cmd/hylo` · `internal/proxy` (TLS interception, routing, normalization, SSE
  tap) · `internal/ledger` (writer + exporter; schema unchanged per D7) · `internal/events`
  (the live event stream shared by the ledger writer and the UIs) · `internal/ui` (web UI
  assets and API) · `internal/statusline`
  · `internal/config` · `internal/ca` · `internal/platform` (per-OS: process ancestry for ⌂,
  paths, service units, CA trust) · `internal/hook` · `web/` (React UI source and the Storybook
  design system; its build output is embedded by `internal/ui`).
- **Config:** `~/.config/hylo/config.yaml` (Windows: `%APPDATA%\hylo\config.yaml`), profiles,
  env overrides `HYLO_*`; secrets referenced by file path, never inline. Parity phase ships a
  config whose defaults reproduce today's `claude-dgx` exactly. Every behavior-shaping value
  is a config key with a documented default (D15).
- **CA trust:** Claude Code is a Node app and trusts the hylo CA via `NODE_EXTRA_CA_CERTS`
  on every OS — no system trust store changes needed (same as today).
- **Proxy model:** one long-lived proxy per user (port in a state file, lock), shared by
  every window; `hylo run` starts it on demand. Streaming end to end; SSE tap reads usage
  without buffering; error bodies buffered for the ledger (today's behavior). It intercepts
  every host Claude Code contacts (D13); proxy settings are scoped to the Claude Code
  process, not its children (D14).
- **Dependencies:** Go standard library first (`crypto/tls`, `net/http`, `httputil`); a YAML
  library; nothing else without a reason. Frontend (`web/`, D16): npm packages are build-time
  only, locked with a lockfile, installed with `npm ci`, and each needs a stated reason.

## 7. Phases (parity first, D4) — each with an exit criterion

| Phase | Work | Exit criterion |
|---|---|---|
| P0 | Repo + scrubbed history (§5), license, README, CI skeleton (GitHub Actions matrix macOS / Linux / Windows), release tooling | Owner approves the scrub report; CI green on all three OSes |
| P1 | `hylo statusline` — lowest risk, pure function of stdin + transcript + metrics | **Golden tests**: the Python and Go versions render byte-identical output for a corpus of recorded stdin fixtures and real transcripts (incl. compaction, >512 KB lines, rebuilds) |
| P2 | `hylo exporter` | Same metric names, labels and values as the Python exporter on the same ledger file |
| P3 | `hylo proxy` — the hard part; internal event stream (feeds the ledger now, the UIs later) | Recorded-request replay: identical routing decisions, rewritten bodies and ledger lines vs the Python addon; then a **shadow week**: one real window on hylo, the rest on Python, ledger diff clean |
| P4 | `hylo run`, `hylo hook stop`, `hylo doctor`, `hylo ca`, `hylo ui` (web UI, D16) | A full working session on each OS; Remote Control works (D6) |
| P5 | **Cutover** — all windows on hylo; Python kept runnable for rollback for 2 weeks; the home-lab repository keeps a pointer README | 2 weeks without rollback; DGX dashboards unchanged (D7) |
| P6 | **Generalize** — backends in config (Anthropic-compatible; OpenAI-compatible translation), routing rules in config, telemetry sources pluggable, cost basis configurable; `DGX_*` → `HYLO_*` with a compatibility shim; `hylo top` (terminal UI, D16) | A non-DGX backend (e.g. Ollama on a laptop) works end to end with only config |
| P7 | **Redesign** ledger and metrics (D7, after it works) | Owner-approved new schema + migration for the Grafana boards |

**Timing constraint:** nothing touches the live `claude-dgx` proxies while the DGX 24 h soak
runs (until it is scored, ~2026-11-14 17:00Z); P0–P2 are safe to do in parallel (new repo only).

## 8. Testing strategy

- **Parity harness** (P1–P3): record real inputs (status line stdin, transcripts, proxied
  requests/responses with secrets stripped) into `testdata/`; run Python and Go on the same
  input; diff outputs. Parity is the definition of done before any behavior change.
- **Unit + table tests** in Go for every rule the status line review fixed (timer `% 60`,
  rebuild threshold, compaction reset, line-completion, pace coloring, etc.).
- **Cross-OS CI** for every PR; Windows covers paths, process ancestry and service install.

## 9. Risks

| Risk | Mitigation |
|---|---|
| TLS interception in Go diverges from mitmproxy (HTTP/2, SSE, keep-alive, WebSocket bridge for Remote Control) | Replay + shadow week before cutover; WebSocket passthrough tested explicitly |
| Claude Code changes underneath (e.g. 2.1.323 removed `subagentStatusLine`) | Pin the tested Claude Code version range in docs; `hylo doctor` reports the running version |
| Windows: no `ps`, different process tree and shells | `internal/platform` per OS; CI on Windows from P0 |
| A public repo leaks something in history | §5 procedure + owner-approved scrub report before the first push |
| Trademark | No "Claude" in the name or logo; "not affiliated with Anthropic" in the README |
| Disrupting the live setup | Python stays the production path until P5; rollback documented |

## 10. Owner decisions (2026-11-14, previously open)

| # | Decision |
|---|---|
| D8 | **License: Apache-2.0** |
| D9 | **Author email in carried-over history → the GitHub no-reply address** (`--mailmap`); author name unchanged |
| D10 | **Keep the scrubbed Python under `legacy/`** until cutover (P5) — the parity harness runs it — then remove |
| D11 | **Kev stays an optional integration** (a config URL for the Stop hook; the regex fallback works without it) |
| D12 | **Distribution: GitHub Releases first**; Homebrew tap / Scoop / `go install` as follow-ups |
| D13 | **Intercept all Claude Code traffic.** TLS is terminated for every host the Claude Code process contacts (as the prototype does today), not only `api.anthropic.com`. Only `POST /v1/messages` on `api.anthropic.com` is ever rewritten; every other host and path is forwarded unchanged. Consequence: the local CA cannot be name-constrained to one host, so it is trusted only by the Claude Code process (via `NODE_EXTRA_CA_CERTS`) and never added to an OS trust store |
| D14 | **Proxy settings do not leak to child processes.** `HTTPS_PROXY` / `NODE_EXTRA_CA_CERTS` apply to the Claude Code process only, not to the commands it spawns (Bash tool commands, `git`/`gh`/`curl`, hooks, the status line), so those keep working when the proxy is down. An intentional, owner-approved deviation from the prototype, which exports both to the whole environment; the mechanism is chosen in P4 (`hylo run`) |
| D15 | **Config over code (iron rule).** Every value that shapes behavior is configuration, not code: backends, hosts, ports, model prefixes, routing rules, prices, timeouts, paths, feature toggles, status line thresholds and colors. One schema in `internal/config`, resolved as config file → `HYLO_*` environment override → built-in default (the prototype's `DGX_*` names stay accepted until the P6 rename shim). Each default sits next to its rationale and, until cutover, equals the prototype's value exactly (D4), so the rule changes no behavior during parity. Logic never contains a magic number or a hard-coded host, model or price; it reads config. Exceptions are protocol and format constants (e.g. `POST /v1/messages`, SSE event and field names, the ledger schema frozen by D7): these are named constants, each with a comment saying why it is not configuration |
| D16 | **Proxy UIs: a web UI and a terminal UI on one live feed.** `hylo proxy` publishes a local, read-only event API covering connected clients and sessions, live flows (lane, routing reason, rewritten-body diff, SSE timeline, usage, ledger lines written), WebSocket/Remote Control connections, backend health, plan limits, effective config (D15) and the CA. Two front ends read it: a web UI built into the binary (`hylo ui`, P4) and a terminal UI (`hylo top`, after the web UI). The web UI is a React + TypeScript app built with Vite and embedded in the binary via `go:embed`: Node is a build-time dependency only, never a runtime one, so users still get one binary. Its components come from a hylo design system (design tokens, components, patterns) developed and documented in Storybook (a development tool, not shipped in the binary); the terminal UI reuses the design system's color and spacing tokens. Design goal: feature-rich yet decluttered and modern, using progressive disclosure (summary first, details on demand). Guardrails: bound to localhost with a per-launch access token; credentials (`Authorization`, `x-api-key`, cookies) always redacted, never stored or forwarded; request/response bodies kept only in a bounded in-memory buffer, never written to disk; read-only to start (no replay or editing); fed by the same internal event stream as the ledger, which stays unchanged (D7). A clickable mockup is approved by the owner before either UI is built |

## 11. After the split — the private home-lab repository

Keeps the serving side (vLLM/LMCache, VictoriaMetrics/Grafana, benchmarks, reports, economics,
runbooks, Kev). Its `claude-dgx` files are replaced by a short README pointing to hylo once P5
completes; until then they stay as the production path.
