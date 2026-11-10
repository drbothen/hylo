#!/usr/bin/env python3
"""Tiny Anthropic-API router for Claude Code.

Requests whose JSON body names an Opus model are sent to the local llama-server
on the DGX; everything else is passed through to api.anthropic.com untouched
(including the caller's own auth headers, so claude.ai login keeps working).

Point Claude Code at it with:  ANTHROPIC_BASE_URL=http://127.0.0.1:4141
"""
import json
import logging
import os

from aiohttp import ClientSession, ClientTimeout, web

LISTEN_HOST = os.environ.get("ROUTER_HOST", "127.0.0.1")
LISTEN_PORT = int(os.environ.get("ROUTER_PORT", "4141"))
ANTHROPIC_UPSTREAM = os.environ.get("ANTHROPIC_UPSTREAM", "https://api.anthropic.com")
DGX_UPSTREAM = os.environ.get("DGX_UPSTREAM", "http://192.0.2.10:8080")
DGX_KEY_FILE = os.path.expanduser(os.environ.get("DGX_KEY_FILE", "~/.config/dgx-llm/api-key"))
# Opt-in: when set, every request routed to the DGX is saved here as JSON
# (system prompt, tools, messages) for inspection. Off by default.
DUMP_DIR = os.path.expanduser(os.environ.get("ROUTER_DUMP_DIR", ""))
# Which Claude model family is served by the DGX (default: Sonnet; Opus/Haiku go to Anthropic).
LOCAL_MODEL_PREFIXES = tuple(
    p.strip() for p in os.environ.get("LOCAL_MODEL_PREFIXES", "claude-sonnet").split(",") if p.strip()
)
# Name the DGX server answers to (vLLM/llama-server --served-model-name / --alias). DGX-bound requests
# get their "model" rewritten to this, so the remapped family doesn't need a server restart.
DGX_SERVED_MODEL = os.environ.get("DGX_SERVED_MODEL", "claude-sonnet-5-5")

# Hop-by-hop / recomputed headers that must not be copied verbatim.
DROP_REQ = {"host", "content-length", "accept-encoding", "connection", "transfer-encoding"}
DROP_RESP = {"content-length", "content-encoding", "transfer-encoding", "connection"}

log = logging.getLogger("opus-router")


def dgx_key() -> str:
    with open(DGX_KEY_FILE) as f:
        return f.read().strip()


# Anthropic server-side tools (executed on Anthropic's servers, declared without input_schema).
# The DGX can't run them, so any request that declares one goes to Anthropic unchanged.
SERVER_TOOL_PREFIXES = ("web_search_", "web_fetch_", "code_execution_")


def uses_server_tool(req: dict) -> bool:
    for tool in req.get("tools") or []:
        if isinstance(tool, dict) and str(tool.get("type", "")).startswith(SERVER_TOOL_PREFIXES):
            return True
    return False


def pick_upstream(path: str, body: bytes):
    """Return (base_url, is_local, model)."""
    model = None
    req = {}
    if path.startswith("/v1/messages") and body:
        try:
            req = json.loads(body)
            model = req.get("model")
        except (ValueError, AttributeError):
            req, model = {}, None
    if model and model.startswith(LOCAL_MODEL_PREFIXES):
        if isinstance(req, dict) and uses_server_tool(req):
            log.info("  request uses an Anthropic server tool (web search/fetch/code exec) -> sending to Anthropic")
            return ANTHROPIC_UPSTREAM, False, model
        return DGX_UPSTREAM, True, model
    return ANTHROPIC_UPSTREAM, False, model


# Content block types vLLM's Anthropic endpoint accepts (from its validation error).
DGX_BLOCK_TYPES = {"text", "image", "tool_use", "tool_result", "tool_reference", "thinking", "redacted_thinking"}
_logged_unknown: set = set()


def _tool_name(block: dict):
    tool = block.get("tool") if isinstance(block.get("tool"), dict) else {}
    definition = tool.get("definition") if isinstance(tool.get("definition"), dict) else {}
    return definition.get("name") or tool.get("name") or block.get("name") or block.get("tool_name")


def normalize_for_dgx(req: dict) -> bool:
    """Translate newer Anthropic request features the DGX (vLLM's Anthropic endpoint) rejects.

    Claude Code changes the tool set mid-conversation with content blocks vLLM doesn't know:
      - `tool_addition` ({"tool": {"definition": {...}}}): definition appended to top-level `tools`
      - `tool_removal`: that tool dropped from top-level `tools`
    Both are applied in conversation order and removed from the messages. Any OTHER unknown block type
    is dropped and logged once (type + keys), so a future Claude Code feature can't 400 every request.
    Returns True if the request was changed.
    """
    changed = False
    tools = req.get("tools")
    if not isinstance(tools, list):
        tools = []
    by_name = {t.get("name"): t for t in tools if isinstance(t, dict) and t.get("name")}
    order = [t.get("name") for t in tools if isinstance(t, dict)]
    for msg in req.get("messages") or []:
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        kept = []
        for block in content:
            btype = block.get("type") if isinstance(block, dict) else None
            if btype in DGX_BLOCK_TYPES or btype is None:
                kept.append(block)
                continue
            changed = True
            name = _tool_name(block)
            if btype == "tool_addition":
                definition = ((block.get("tool") or {}).get("definition")) or {}
                if name and definition:
                    if name not in by_name:
                        order.append(name)
                    by_name[name] = definition
            elif btype == "tool_removal":
                if name:
                    by_name.pop(name, None)
            elif btype not in _logged_unknown:
                _logged_unknown.add(btype)
                log.info("  dropping unknown content block type for DGX: %s keys=%s", btype, list(block.keys()))
        if len(kept) != len(content):
            msg["content"] = kept or [{"type": "text", "text": "(tools updated)"}]
    if changed:
        req["tools"] = [by_name[n] for n in dict.fromkeys(order) if n in by_name]
    return changed


def dump_request(path: str, body: bytes) -> None:
    """Save a DGX-bound request body (only the body; no auth headers) for inspection."""
    import time
    os.makedirs(DUMP_DIR, mode=0o700, exist_ok=True)
    kind = "count_tokens" if path.endswith("count_tokens") else "messages"
    name = f"{time.strftime('%Y%m%d-%H%M%S')}-{time.time_ns() % 1_000_000:06d}-{kind}.json"
    fd = os.open(os.path.join(DUMP_DIR, name), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(body)


def log_reply_end(status: int, tail: bytes) -> None:
    """Log why a DGX reply ended, from its last bytes (works for streamed SSE and plain JSON)."""
    import re
    text = tail.decode("utf-8", "replace")
    stops = re.findall(r'"stop_reason"\s*:\s*"?([a-z_]+|null)', text)
    outs = re.findall(r'"output_tokens"\s*:\s*(\d+)', text)
    log.info("  DGX reply ended: http=%s stop_reason=%s output_tokens=%s",
             status, stops[-1] if stops else "?", outs[-1] if outs else "?")
    if status >= 400:
        log.info("  DGX error body: %s", text[-600:].replace("\n", " "))


async def health(request: web.Request) -> web.Response:
    return web.json_response({"router": "opus-router", "dgx": DGX_UPSTREAM})


async def handle(request: web.Request) -> web.StreamResponse:
    body = await request.read()
    base, is_local, model = pick_upstream(request.path, body)

    headers = {k: v for k, v in request.headers.items() if k.lower() not in DROP_REQ}
    if is_local:
        # Never send the user's Anthropic credentials to the DGX.
        for k in list(headers):
            if k.lower() in {"authorization", "x-api-key", "anthropic-beta"}:
                headers.pop(k)
        headers["Authorization"] = f"Bearer {dgx_key()}"
        try:
            req = json.loads(body)
            changed = normalize_for_dgx(req)
            if DGX_SERVED_MODEL and model and model != DGX_SERVED_MODEL:
                req["model"] = DGX_SERVED_MODEL
                changed = True
            if changed:
                body = json.dumps(req).encode()
        except (ValueError, TypeError, AttributeError):
            pass
        if DUMP_DIR:
            dump_request(request.path, body)

    url = base + request.path_qs
    log.info("%s %s model=%s -> %s", request.method, request.path, model, "DGX" if is_local else "anthropic")

    session: ClientSession = request.app["session"]
    try:
        async with session.request(request.method, url, headers=headers, data=body) as up:
            resp = web.StreamResponse(status=up.status)
            for k, v in up.headers.items():
                if k.lower() not in DROP_RESP:
                    resp.headers[k] = v
            await resp.prepare(request)
            tail = b""  # last bytes of a DGX reply, kept to log how it ended (stop_reason / output_tokens)
            async for chunk in up.content.iter_any():
                await resp.write(chunk)
                if is_local:
                    tail = (tail + chunk)[-4096:]
            await resp.write_eof()
            if is_local and request.path == "/v1/messages":
                log_reply_end(up.status, tail)
            return resp
    except Exception as e:  # upstream down, DNS, etc.
        log.error("upstream error for %s: %r", url, e)
        return web.json_response(
            {"type": "error", "error": {"type": "api_error", "message": f"router upstream error: {e!r}"}},
            status=502,
        )


async def on_startup(app: web.Application):
    app["session"] = ClientSession(timeout=ClientTimeout(total=None, sock_connect=15), auto_decompress=True)


async def on_cleanup(app: web.Application):
    await app["session"].close()


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    app = web.Application(client_max_size=256 * 1024 * 1024)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    app.router.add_get("/_opus_router/health", health)
    app.router.add_route("*", "/{tail:.*}", handle)
    web.run_app(app, host=LISTEN_HOST, port=LISTEN_PORT, access_log=None)


if __name__ == "__main__":
    main()
