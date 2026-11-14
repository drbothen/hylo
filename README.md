# hylo

**Hybrid local + cloud model routing for Claude Code.** One session, two lanes: requests for
the models you choose run on your own AI hardware, everything else goes to Anthropic —
switched per request, invisibly, with a status line that shows which lane you are on and what
it costs.

> **Not affiliated with Anthropic.** hylo is an independent tool for
> [Claude Code](https://code.claude.com). "Claude" is a trademark of Anthropic.

## Name

**hylo** (*HY-loh*, /ˈhaɪ.loʊ/) is a blend of **hy**brid + **lo**cal. It also echoes the
Greek **ὕλη** (*hýlē*): "wood, timber", and in philosophy "matter, the physical stuff" — fitting
for a tool about running models on the machine in the room.

## Status

**Early: being ported from a working Python prototype to Go.** The prototype (`legacy/`) has
been in daily use against a self-hosted GPU server running vLLM; it is kept here, unchanged,
as the reference the Go version is tested against.

| Piece | Prototype (`legacy/`) | Go (`hylo …`) |
|---|---|---|
| Invisible router (TLS-intercepting proxy, per-request routing, usage ledger) | `dgx_proxy.py` (mitmproxy addon) | planned: `hylo proxy` |
| Status line (lane, context, tokens, cost, plan limits, backend telemetry) | `dgx_statusline.py` | planned: `hylo statusline` |
| Launcher | `claude-dgx` | planned: `hylo run` |
| Ledger → Prometheus exporter | `dgx_ledger_exporter.py` | planned: `hylo exporter` |
| Stop hook (fake-stop detection; optional external classifier) | `auto_continue.py` | planned: `hylo hook stop` |

The prototype's names (`dgx_*`, `DGX_*`) come from its first backend, an NVIDIA DGX Station;
hylo generalizes to any local backend (vLLM, SGLang, llama.cpp, Ollama, …) once the Go port
reaches parity.

## How it works (prototype)

Claude Code talks to `api.anthropic.com` through a local proxy that it trusts via
`NODE_EXTRA_CA_CERTS`. The proxy reads each `/v1/messages` request: models matching your
local prefixes go to your server (model name and auth rewritten), everything else passes
through to Anthropic untouched. Because Claude Code still believes it talks to Anthropic
directly, features like Remote Control keep working. Every request and its token usage is
appended to a JSONL ledger, which feeds the status line and optional Prometheus metrics.

## Documentation

- [`docs/PLAN.md`](docs/PLAN.md) — the migration and Go-port plan (phases, testing, decisions)
- [`docs/STATUSLINE-WIDGETS.md`](docs/STATUSLINE-WIDGETS.md) — every status line widget: what it measures and how
- [`docs/STATUSLINE-REVIEW-2026-11-13.md`](docs/STATUSLINE-REVIEW-2026-11-13.md) — the widget-by-widget review and its decisions

## Platforms

macOS, Linux and Windows are targets for the Go version. The prototype ran on macOS.

## License

[Apache License 2.0](LICENSE).
