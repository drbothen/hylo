# CLAUDE.md — working in hylo

hylo is a **public** Go project: hybrid local + cloud model routing for Claude Code (one
session; requests for chosen models run on the user's own AI hardware, the rest go to
Anthropic, switched per request by an invisible TLS-intercepting proxy, with a status line).
It is being ported from a working Python prototype (`legacy/`). Not affiliated with Anthropic.

## Read first, in this order

1. **`docs/RESUME.md`** — current state, what was just done, the next concrete steps. Start here.
2. **`docs/PLAN.md`** — the approved plan: decisions **D1–D14**, scope, architecture, phases
   **P0–P7** with exit criteria, testing strategy, risks. Decisions are settled; do not reopen
   them unless the owner asks.
3. **`docs/STATUSLINE-WIDGETS.md`** — the status line's behavior, widget by widget (the spec the
   Go port must match), and **`docs/STATUSLINE-REVIEW-2026-11-13.md`** — why each rule exists.
4. **`CLAUDE.local.md`** (git-ignored, not in the public repo) — machine-specific context: where
   the live prototype runs, paths, endpoints. If it is missing, ask the owner; never guess.

## Repository layout

| Path | What |
|---|---|
| `legacy/` | The Python/zsh prototype, **read-only reference** for the parity harness. Do not modify it (other than to make it runnable for tests); remove only at cutover (P5, D10) |
| `docs/` | Plan, resume snapshot, status line spec and review |
| `cmd/hylo/`, `internal/…` | The Go implementation (created in P1; layout in `docs/PLAN.md` §6) |

## Rules

**Public-repo hygiene (most important — this repository is public).**
- Never commit personal or infrastructure details: real IP addresses (use `192.0.2.x`, RFC
  5737), usernames, home paths, hostnames, account IDs or hashes, client/project names, email
  addresses (commit identity is the GitHub no-reply address), links to private sessions.
- Never commit real transcripts, ledgers, request/response captures or status line stdin.
  Test fixtures are **synthetic**, or scrubbed by a script that is itself committed and reviewed.
- Before every push: `gitleaks detect --source . --log-opts="--all"` and a pattern scan for the
  categories above must both be clean. Do not add `Claude-Session:` links to commits here.
- No "Claude" in names, binaries or logos (Anthropic trademark); describe hylo as "for Claude Code".

**How the owner works.**
- **Commit only when the owner asks.** Push only when asked.
- **Parity first (D4):** the Go port must reproduce `legacy/` behavior on recorded inputs before
  any behavior change or generalization. A parity diff is the definition of done for P1–P3.
- **Explain every threshold:** each numeric cut-off gets its rationale (measured, derived,
  convention, or labeled judgment call) in a code comment and in the docs.
- **Verify before claiming.** Run it, test it, read the source; say what was not verified.
- Keep the ledger format and metric names unchanged until after cutover (D7).
- Write everything in English.

**Engineering.**
- Go ≥ 1.26, standard library first (`crypto/tls`, `net/http`, `httputil`); add a dependency only
  with a reason.
- Cross-platform from day one: macOS, Linux, Windows (D5). OS-specific code lives in
  `internal/platform` with build tags; never shell out to OS tools without a per-OS fallback.
- Every widget rule fixed in the status line review gets a table test (see the review doc).
- CI runs on all three OSes for every change.

## Glossary

- **Lane** — where a request is served: local (your backend) or Anthropic.
- **Invisible mode** — Claude Code keeps talking to `api.anthropic.com`; the proxy (trusted via
  `NODE_EXTRA_CA_CERTS`) routes each `/v1/messages` request. Keeps Remote Control working (D6).
- **Ledger** — the append-only JSONL log of every request, reply and usage block (plus
  `anth_ratelimit` plan-limit headers), feeding the status line and the Prometheus exporter.
- **Parity harness** — runs `legacy/` and the Go code on the same inputs and diffs the outputs.
