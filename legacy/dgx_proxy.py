"""mitmproxy addon: invisible router for claude-dgx (DGX_INVISIBLE=1 mode).

Claude Code connects to api.anthropic.com via HTTPS_PROXY (this proxy), trusting our CA via
NODE_EXTRA_CA_CERTS. We terminate that TLS here, read POST /v1/messages bodies, and route:

  - model in LOCAL_MODEL_PREFIXES (claude-sonnet) and no Anthropic server tools declared
      -> DGX (scheme/host/port switched, model rewritten to DGX_SERVED_MODEL,
         tool_addition/tool_removal blocks translated, Authorization swapped to the DGX key)
  - everything else (Opus, Haiku, server-tool requests, telemetry, unknown paths)
      -> real api.anthropic.com, untouched, with the session's own auth

Streaming: /v1/messages responses are streamed (response.stream = True) so Claude Code sees
tokens live. Detailed stop_reason logging therefore only applies to buffered responses;
mitmdump's own flow log always records completion.

v2 OBSERVABILITY (2026-11-09): every request/response/classified endpoint is appended as one JSON
line to the LEDGER (~/dgx-llm-obs.jsonl). WebSocket lanes (bridge.claudeusercontent.com) are
life-cycle logged only: CONNECT/tls-establish/close with durations and byte counts — payloads are
never touched or buffered, so realtime ping/pong latency is unaffected. Unknown hosts default to
passthrough+tunnel; only api.anthropic.com /v1/messages is ever rewritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urlparse

try:
    import mitmproxy.http
    from mitmproxy import ctx
except ImportError:  # CLI mode (`dgx_proxy.py trust ...`) needs no mitmproxy
    pass

DGX_BLOCK_TYPES = {"text", "image", "tool_use", "tool_result", "thinking", "redacted_thinking"}
_logged_unknown: set = set()
log = logging.getLogger("dgx_proxy")

DECISION_LOG = os.environ.get("DGX_PROXY_DECISIONS", os.path.expanduser("~/dgx-llm-routing-decisions.log"))
LEDGER = os.environ.get("DGX_OBS_LEDGER", os.path.expanduser("~/dgx-llm-obs.jsonl"))

def ledger(event: str, **fields) -> None:
    """Append one observability event to the JSONL ledger. Never raises."""
    try:
        with open(LEDGER, "a") as f:
            f.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "event": event, **fields}) + "\n")
    except OSError:
        pass


def note(msg: str, *args) -> None:
    try:
        msg = msg % args if args else msg
    except Exception:
        pass
    try:           # direct append to a file: immune to mitmdump's stdout buffering
        with open(DECISION_LOG, "a") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + msg + "\n")
    except OSError:
        pass


class DGXRouter:
    def __init__(self):
        upstream = os.environ.get("DGX_UPSTREAM", "http://192.0.2.10:8080")
        u = urlparse(upstream)
        self.dgx_scheme = u.scheme or "http"
        self.dgx_host = u.hostname or "192.0.2.10"
        self.dgx_port = u.port or 80
        self.served = os.environ.get("DGX_SERVED_MODEL", "claude-sonnet-5-5")
        self.prefixes = tuple(
            p.strip() for p in os.environ.get("LOCAL_MODEL_PREFIXES", "claude-sonnet").split(",") if p.strip()
        )
        self.key_file = os.environ.get("DGX_KEY_FILE", os.path.expanduser("~/.config/dgx-llm/api-key"))
        self._key_cache = None

    def _key(self) -> str:
        if self._key_cache is None:
            with open(self.key_file) as f:
                self._key_cache = f.read().strip()
        return self._key_cache

    # ---- request-side routing -------------------------------------------------
    def request(self, flow: mitmproxy.http.HTTPFlow) -> None:
        # WebSocket upgrade for the bridge: mark the flow so ws hooks can report its life-cycle.
        if flow.request.host == "bridge.claudeusercontent.com" and flow.request.headers.get("upgrade", "").lower() == "websocket":
            ledger("bridge_ws_connect", host=flow.request.host)
            return
        if flow.request.host != "api.anthropic.com" or not flow.request.path.startswith("/v1/messages"):
            return  # telemetry etc.: pass through untouched
        try:
            req = json.loads(flow.request.get_text())
        except (ValueError, TypeError):
            note("unparseable /v1/messages body, passing through to anthropic")
            return
        if not isinstance(req, dict):
            return
        model = req.get("model") or ""
        # Attribution stash for BOTH lanes (parsed, never mutated on passthrough:
        # CC applies ANTHROPIC_CUSTOM_HEADERS to every request it makes, so the
        # Opus/Haiku lane carries the same X-DGX-Project/User + session headers).
        meta = req.get("metadata") if isinstance(req.get("metadata"), dict) else {}
        flow._attrib = {
            "project": flow.request.headers.get("X-DGX-Project"),
            "user": flow.request.headers.get("X-DGX-User"),
            "session": flow.request.headers.get("X-Claude-Code-Session-Id"),
            "meta_user_id": meta.get("user_id"),
            "model_req": model,
            "req_bytes": len(flow.request.get_text() or ""),
        }
        flow._t0 = time.time()
        # Plain-text streaming on BOTH lanes so the SSE tap can read usage lines
        # (gzip'd chunks would defeat the parser; LAN penalty is negligible).
        flow.request.headers["Accept-Encoding"] = "identity"
        if not model.startswith(self.prefixes):
            flow._attrib["lane"] = "anthropic"
            ledger("anth_request", **flow._attrib)
            note("-> anthropic (%s)", model)
            return  # Opus / Haiku / unknown families: real Anthropic
        if uses_server_tool(req):
            flow._attrib["lane"] = "anthropic-server-tools"
            ledger("anth_request", **flow._attrib)
            note("-> anthropic (%s declares a server tool)", model)
            return

        attrib = dict(flow._attrib)
        attrib["model_served"] = req.get("model")
        changed = normalize_for_dgx(req)
        if self.served and model != self.served:
            req["model"] = self.served
            changed = True
        if changed:
            flow.request.set_text(json.dumps(req))

        flow._dgx = attrib
        flow._dgx_t0 = flow._t0
        ledger("dgx_request", **attrib)
        # Belt-and-braces: carry attribution to the serving side (vLLM logs/OTel).
        flow.request.headers["X-DGX-Project"] = attrib["project"] or "unknown"
        flow.request.headers["X-DGX-User"] = attrib["user"] or "unknown"
        if attrib["session"]:
            flow.request.headers["X-DGX-Session"] = attrib["session"]

        flow.request.scheme = self.dgx_scheme
        flow.request.host = self.dgx_host
        flow.request.port = self.dgx_port
        flow.request.headers["Authorization"] = f"Bearer {self._key()}"
        flow.request.headers.pop("anthropic-beta", None)  # OAuth beta header is meaningless to the DGX
        flow.request.headers["Accept-Encoding"] = "identity"
        note("-> DGX (%s)", model)

    # ---- response handling ------------------------------------------------------
    def responseheaders(self, flow: mitmproxy.http.HTTPFlow) -> None:
        # Stream /v1/messages bodies so Claude Code sees tokens as they are generated —
        # EXCEPT error responses, which we buffer so the error body can be logged.
        # Any response declaring text/event-stream is ALSO streamed unconditionally: SSE lanes
        # (relay polls, realtime channels) die if the proxy buffers mid-event.
        ctype = (flow.response.headers.get("content-type") or "") if flow.response else ""
        if flow.response is not None and "text/event-stream" in ctype:
            flow._sse_tap = _SSETap()
            flow.response.stream = flow._sse_tap.feed  # pass-through tap
            return
        if flow.request.path.startswith("/v1/messages") and flow.response is not None:
            flow.response.stream = flow.response.status_code < 400  # buffer error bodies for logging

    def response(self, flow: mitmproxy.http.HTTPFlow) -> None:
        host = flow.request.host
        if host == "bridge.claudeusercontent.com":
            ledger("bridge_ws_close", duration_s=round(getattr(flow, "_bridge_dur", 0.0) or 0.0, 1))
            return
        if host == "api.anthropic.com" and flow.request.path.startswith("/v1/messages"):
            attrib = getattr(flow, "_attrib", {})
            tap = getattr(flow, "_sse_tap", None)
            in_tok = out_tok = None
            stop = None
            if tap is not None and tap.usage:
                in_tok, out_tok = tap.usage
                stop = tap.stop_reason
            elif flow.response.status_code < 400:
                try:
                    body = json.loads(flow.response.get_text(strict=False))
                    u = body.get("usage") if isinstance(body, dict) else None
                    if isinstance(u, dict):
                        in_tok = u.get("input_tokens")
                        out_tok = u.get("output_tokens")
                    stop = extract_stop_reason(body)
                except (ValueError, TypeError):
                    pass
            ev = dict(attrib)
            ev.update(status=flow.response.status_code,
                      duration_s=round(time.time() - getattr(flow, "_t0", time.time()), 3))
            if tap is not None:
                note("   anth tap: buf=%d usage=%s ct=%s", len(tap.buf), tap.usage,
                     flow.response.headers.get("content-type"))
            if in_tok is not None:
                ev.update(in_tok=int(in_tok or 0), out_tok=int(out_tok or 0), stop_reason=stop)
            ledger("anth_reply", **ev)
            if in_tok is not None:
                ledger("anth_usage", lane=attrib.get("lane", "anthropic"),
                       project=attrib.get("project"), user=attrib.get("user"),
                       session=attrib.get("session"),
                       account=_account_hint(attrib.get("meta_user_id")),
                       model=attrib.get("model_req"),
                       in_tok=int(in_tok or 0), out_tok=int(out_tok or 0),
                       stop_reason=stop)
        if flow.request.host != self.dgx_host or not flow.request.path.startswith("/v1/messages"):
            return
        attrib = getattr(flow, "_dgx", {})
        tap = getattr(flow, "_sse_tap", None)
        if tap is not None and tap.usage:
            attrib["in_tok"] = tap.usage[0]
            attrib["out_tok"] = tap.usage[1]
        if tap is not None and tap.stop_reason:
            attrib["stream_stop_reason"] = tap.stop_reason
        ledger("dgx_reply", status=flow.response.status_code,
               duration_s=round(time.time() - getattr(flow, "_dgx_t0", time.time()), 3),
               **attrib)
        if attrib.get("in_tok") is not None:
            ledger("dgx_usage", project=attrib.get("project"), user=attrib.get("user"),
                   session=attrib.get("session"), account=_account_hint(attrib.get("meta_user_id")),
                   in_tok=attrib["in_tok"], out_tok=attrib["out_tok"],
                   stop_reason=attrib.get("stream_stop_reason"))
        if flow.response.status_code >= 400:
            # Keep the full offending request for post-mortem (e.g. FastAPI json_invalid
            # truncation-style 400s on multi-MB bodies). Capped to 20 newest files.
            note("   DGX %s error body: %s", flow.response.status_code,
                 flow.response.get_text(strict=False)[:600])
            try:
                obs = Path.home() / "dgx-llm-obs"
                obs.mkdir(exist_ok=True)
                old = sorted(obs.glob("failed-req-*.json"))
                for stale in old[:-19]:
                    stale.unlink(missing_ok=True)
                body_text = flow.request.get_text() or ""
                if len(body_text) < 50_000_000:
                    (obs / f"failed-req-{int(time.time() * 1000)}.json").write_text(body_text)
                    note("   saved offending request (%d bytes) to dgx-llm-obs/", len(body_text))
            except OSError:
                pass
            return
        stop = "unknown"
        if flow.response.stream or "text/event-stream" in (flow.response.headers.get("content-type") or ""):
            stop = "(streamed)"  # body flowed through chunk by chunk; nothing to parse here
        else:
            try:
                stop = extract_stop_reason(json.loads(flow.response.get_text(strict=False))) or stop
            except (ValueError, TypeError):
                pass  # unparseable body: leave the marker for the log
        note("   DGX reply: http=%s stop_reason=%s", flow.response.status_code, stop)


def _account_hint(meta_user_id):
    """8-char account prefix from CC's metadata.user_id (stringified JSON) for the ledger."""
    if isinstance(meta_user_id, str):
        try:
            m = json.loads(meta_user_id)
            if isinstance(m, dict):
                return (m.get("account_uuid") or "unknown")[:8]
        except ValueError:
            pass
        return meta_user_id[:8]
    return "unknown"


class _SSETap:
    """Pass-through SSE tap: mitmproxy calls feed() per chunk when response.stream
    is a callable. Accumulates the tail, extracts usage{} from message_delta and
    the final stop_reason, without buffering the whole body client-side."""

    KEEP = 64_000  # tail bytes retained for line-safe parsing

    def __init__(self):
        self.buf = b""
        self.usage = None       # (input_tokens, output_tokens)
        self.stop_reason = None

    def feed(self, chunk: bytes) -> bytes:
        self.buf += chunk
        # keep only complete trailing lines; parse the complete ones
        nl = self.buf.rfind(b"\n")
        if nl >= 0:
            block, self.buf = self.buf[:nl], self.buf[nl + 1:]
            try:
                self._scan(block)
            except Exception:
                pass
        if len(self.buf) > self.KEEP:  # runaway line guard
            self.buf = self.buf[-self.KEEP:]
        return chunk

    def _scan(self, block: bytes) -> None:
        for m in re.finditer(rb"data: ({.*})", block):
            try:
                obj = json.loads(m.group(1))
            except ValueError:
                continue
            u = obj.get("usage") if isinstance(obj, dict) else None
            if isinstance(u, dict) and "input_tokens" in u:
                self.usage = (int(u.get("input_tokens") or 0), int(u.get("output_tokens") or 0))
            sr = obj.get("delta", {}).get("stop_reason") if isinstance(obj, dict) else None
            if sr:
                self.stop_reason = sr


_STOP_REASON_ALIASES = {    # OpenAI/vLLM finish_reason -> Anthropic stop_reason vocabulary, so the
    # decision log reads identically whichever lane produced the reply.
    "stop": "end_turn",
    "length": "max_tokens",
    "tool_calls": "tool_use",
    "function_call": "tool_use",
}


def extract_stop_reason(body) -> str | None:
    """Read the stop reason from either response dialect.

    Anthropic /v1/messages: `stop_reason` at the top level (end_turn, tool_use,
    max_tokens, stop_sequence). OpenAI/vLLM chat completions:
    `choices[0].finish_reason` (stop, length, tool_calls). Alias-normalized onto
    the Anthropic vocabulary; unrecognized values pass through verbatim.
    """
    if not isinstance(body, dict):
        return None
    reason = body.get("stop_reason")
    if reason is None:
        choices = body.get("choices")
        if isinstance(choices, list) and choices and isinstance(choices[0], dict):
            reason = choices[0].get("finish_reason")
    if not isinstance(reason, str):
        return None
    return _STOP_REASON_ALIASES.get(reason, reason)


def uses_server_tool(req: dict) -> bool:
    """Anthropic-executed tools (web search/fetch, code execution) only run on Anthropic's side."""
    for tool in req.get("tools") or []:
        if isinstance(tool, dict) and str(tool.get("type", "")).startswith(("web_search_", "web_fetch_", "code_execution_")):
            return True
    return False


def normalize_for_dgx(req: dict) -> bool:
    """Apply mid-conversation tool-set changes (newer Claude Code) that vLLM rejects.

    `tool_addition` blocks carry a tool definition: append it to the top-level `tools`.
    `tool_removal` blocks drop a tool. Both are removed from the messages. Any other block type
    outside vLLM's accepted set is dropped and logged once. Returns True if the request changed.
    """
    changed = False
    tools = req.get("tools")
    if not isinstance(tools, list):
        tools = []
    by_name = {t.get("name"): t for t in tools if isinstance(t, dict) and t.get("name")}
    order = [t.get("name") for t in tools if isinstance(t, dict)]
    # vLLM requires input_schema on every tool; a few Claude Code tools omit it (e.g. WebSearch
    # declarations carried as plain tools). An empty object schema is semantically identical.
    for tool in tools:
        if isinstance(tool, dict) and "input_schema" not in tool:
            tool["input_schema"] = {"type": "object", "properties": {}}
            changed = True
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
            tool = block.get("tool") if isinstance(block.get("tool"), dict) else {}
            definition = tool.get("definition") if isinstance(tool.get("definition"), dict) else {}
            name = definition.get("name") or tool.get("name") or block.get("name") or block.get("tool_name")
            if btype == "tool_addition":
                if name and definition:
                    if name not in by_name:
                        order.append(name)
                    by_name[name] = definition
            elif btype == "tool_removal":
                by_name.pop(name, None)
            else:
                if btype not in _logged_unknown:
                    _logged_unknown.add(btype)
                    note("dropping unknown content block type for DGX: %s keys=%s", btype, list(block.keys()))
        if len(kept) != len(content):
            msg["content"] = kept or [{"type": "text", "text": "(tools updated)"}]
    if changed:
        req["tools"] = [by_name[n] for n in dict.fromkeys(order) if n in by_name]
    return changed


note("addon module loaded (PID %d)" % os.getpid())


_router = DGXRouter()


def request(flow: mitmproxy.http.HTTPFlow) -> None:
    _router.request(flow)


def websocket_start(flow: mitmproxy.http.HTTPFlow) -> None:
    if hasattr(flow, "_ws_started"):
        flow._ws_started = time.time()


def websocket_end(flow: mitmproxy.http.HTTPFlow) -> None:
    if hasattr(flow, "_ws_started"):
        dur = time.time() - flow._ws_started
        ledger("ws_closed", duration_s=round(dur, 1))


def responseheaders(flow: mitmproxy.http.HTTPFlow) -> None:
    _router.responseheaders(flow)


def response(flow: mitmproxy.http.HTTPFlow) -> None:
    _router.response(flow)


# ============================================================================
# Trust lifecycle CLI:  python dgx_proxy.py trust {install,status,remove,rotate}
#
# Permanent-install model (the mkcert pattern): the CA is trusted once, and
# these commands own the whole story — install, inspect, remove, rotate.
# The state file records WHICH fingerprint we installed so remove/rotate can
# distinguish our keychain entry from one the user imported independently.
# Runs standalone: the mitmproxy imports above are optional.
# ============================================================================
MITMPROXY_DIR = Path.home() / ".mitmproxy"
CA_PEM = MITMPROXY_DIR / "mitmproxy-ca-cert.pem"
TRUST_CERT_NAME = "mitmproxy"
STATE_PATH = Path(os.environ.get("DGX_TRUST_STATE", str(Path.home() / ".dgx" / "trust-state.json")))
BACKUPS_TO_KEEP = 3


def _login_keychain() -> Path:
    proc = subprocess.run(["security", "login-keychain"], capture_output=True, text=True)
    line = (proc.stdout or "").strip().strip('"')
    if proc.returncode == 0 and line:
        return Path(line)
    return Path.home() / "Library/Keychains/login.keychain-db"


def _file_fingerprint(path: Path) -> str | None:
    """X.509 SHA-256 of the CA, or None if unreadable / openssl unavailable."""
    try:
        proc = subprocess.run(
            ["openssl", "x509", "-in", str(path), "-noout", "-fingerprint", "-sha256"],
            capture_output=True, text=True,
        )
        if proc.returncode == 0 and "=" in proc.stdout:
            return proc.stdout.strip().split("=", 1)[-1].replace(":", "").lower()
    except OSError:
        pass
    return None


def _keychain_fingerprint(keychain: Path) -> str | None:
    proc = subprocess.run(
        ["security", "find-certificate", "-Z", "-c", TRUST_CERT_NAME, str(keychain)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return None
    for line in proc.stdout.splitlines():
        if "hash" not in line.lower():
            continue
        hex_tokens = [tok for tok in line.replace(":", " ").split() if len(tok) == 64]
        if hex_tokens:
            return hex_tokens[-1].lower()
    return None


def _mitmdump_running() -> bool:
    return subprocess.run(["pgrep", "-f", "mitmdump"], capture_output=True).returncode == 0


def _read_state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text())
    except (OSError, ValueError):
        return {}


def _write_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(STATE_PATH.parent), prefix=".trust-state.")
    with os.fdopen(fd, "w") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, STATE_PATH)


def cmd_trust_install(_args) -> None:
    if not CA_PEM.is_file():
        sys.exit(f"No CA at {CA_PEM} — start the proxy once so mitmproxy generates one.")
    keychain = _login_keychain()
    file_fp = _file_fingerprint(CA_PEM)
    keychain_fp = _keychain_fingerprint(keychain)
    state = {"installed_sha256": file_fp, "keychain": str(keychain),
             "installed_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if keychain_fp and file_fp and keychain_fp == file_fp:
        _write_state(state)
        print("Already trusted; keychain matches the CA on disk. Nothing to do.")
        return
    print(f"Adding {CA_PEM} to the login keychain — macOS may prompt for authorization…")
    proc = subprocess.run(["security", "add-trusted-cert", "-r", "trustRoot",
                           "-k", str(keychain), str(CA_PEM)])
    if proc.returncode != 0:
        sys.exit("add-trusted-cert failed — trust was NOT installed.")
    _write_state(state)
    print(f"Trusted in {keychain}.")
    print("Coverage reminder: keychain trust covers Apple-native, Go, curl, .NET stacks;")
    print(f"Node/Electron need NODE_EXTRA_CA_CERTS={CA_PEM}. (sha256 {file_fp})")


def cmd_trust_status(_args) -> None:
    keychain = _login_keychain()
    file_fp = _file_fingerprint(CA_PEM) if CA_PEM.is_file() else None
    keychain_fp = _keychain_fingerprint(keychain)
    if file_fp and keychain_fp:
        match = "YES" if file_fp == keychain_fp else "NO — DRIFT"
    elif file_fp or keychain_fp:
        match = "one side missing"
    else:
        match = "cannot verify (openssl missing?)"
    state = _read_state()
    rows = [
        ("CA file", str(CA_PEM) if CA_PEM.is_file() else "MISSING"),
        ("CA sha256", file_fp or "n/a"),
        ("Keychain entry", "present" if keychain_fp else "absent"),
        ("Keychain sha256", keychain_fp or "n/a"),
        ("Match", match),
        ("Proxy process", "running" if _mitmdump_running() else "not detected"),
        ("Last install recorded", state.get("installed_at", "none")),
    ]
    width = max(len(k) for k, _ in rows)
    for k, v in rows:
        print(f"{k.ljust(width)} : {v}")
    if match.startswith("NO"):
        print("\nDRIFT: the keychain trusts a DIFFERENT CA than the file on disk.")
        print("Classic silent breakage — re-run `trust install` (or `trust rotate`).")


def cmd_trust_remove(args) -> None:
    keychain = _login_keychain()
    keychain_fp = _keychain_fingerprint(keychain)
    if not keychain_fp:
        print("No CA named 'mitmproxy' in the login keychain; nothing to remove.")
        STATE_PATH.unlink(missing_ok=True)
        return
    state_fp = _read_state().get("installed_sha256")
    if state_fp and state_fp != keychain_fp and not args.force:
        sys.exit("Keychain entry does not match our recorded install; "
                 "pass --force to remove it anyway.")
    if not args.yes:
        if input(f"Remove '{TRUST_CERT_NAME}' from {keychain}? [y/N] ").strip().lower() not in {"y", "yes"}:
            print("Aborted.")
            return
    removed = 0
    while removed < 10 and _keychain_fingerprint(keychain):
        subprocess.run(["security", "delete-certificate", "-c", TRUST_CERT_NAME, str(keychain)],
                       check=False)
        removed += 1
    STATE_PATH.unlink(missing_ok=True)
    print(f"Removed ({removed} entry deleted) from {keychain}. CA files remain in {MITMPROXY_DIR}.")
    print("If the CA was ever added to the SYSTEM keychain, also run:")
    print(f"  sudo security delete-certificate -c {TRUST_CERT_NAME} /Library/Keychains/System.keychain")


def cmd_trust_rotate(args) -> None:
    if _mitmdump_running() and not args.force:
        sys.exit("mitmdump appears to be running — stop it first (rotation swaps the CA "
                 "files beneath it), or pass --force.")
    if not MITMPROXY_DIR.is_dir():
        sys.exit(f"{MITMPROXY_DIR} not found; nothing to rotate.")
    old_fp = _file_fingerprint(CA_PEM)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup = MITMPROXY_DIR.parent / f".mitmproxy.bak-{stamp}"
    print(f"Archiving {MITMPROXY_DIR} -> {backup}")
    shutil.move(str(MITMPROXY_DIR), str(backup))
    old_digest = hashlib.sha256((backup / CA_PEM.name).read_bytes()).hexdigest()[:16]

    backups = sorted(MITMPROXY_DIR.parent.glob(".mitmproxy.bak-*"))
    for stale in backups[:-BACKUPS_TO_KEEP]:
        shutil.rmtree(stale, ignore_errors=True)

    restart_cmd = os.environ.get("DGX_PROXY_RESTART_CMD")  # e.g. "brew services restart mitmdump"
    if restart_cmd:
        print("Regenerating CA via DGX_PROXY_RESTART_CMD (must return after daemonising)…")
        subprocess.run(restart_cmd, shell=True, check=False)
        deadline = time.time() + 30
        while not CA_PEM.is_file() and time.time() < deadline:
            time.sleep(0.5)
    if not CA_PEM.is_file():
        sys.exit("Fresh CA not found — start the proxy yourself, then re-run `trust install`.")

    cmd_trust_install(None)
    new_digest = hashlib.sha256(CA_PEM.read_bytes()).hexdigest()[:16]
    print("\nRotation complete.")
    print(f"  old CA (archive {backup.name}, sha256[:16]={old_digest}) fingerprint: {old_fp}")
    print(f"  new CA sha256[:16]={new_digest}; fingerprint: {_file_fingerprint(CA_PEM)}")
    print("Re-export the new CA anywhere the old one was copied (browsers, remote boxes).")


def _build_parser() -> "argparse.ArgumentParser":
    parser = argparse.ArgumentParser(prog="dgx_proxy.py trust",
                                     description="manage mitmproxy CA trust for the dgx proxy")
    sub = parser.add_subparsers(dest="command", required=True)

    install = sub.add_parser("install", help="add the mitmproxy CA to the login keychain (idempotent)")
    install.set_defaults(func=cmd_trust_install)

    status = sub.add_parser("status", help="report CA file / keychain agreement and drift")
    status.set_defaults(func=cmd_trust_status)

    remove = sub.add_parser("remove", help="remove the CA from the login keychain")
    remove.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    remove.add_argument("--force", action="store_true", help="remove even if the fingerprint differs from ours")
    remove.set_defaults(func=cmd_trust_remove)

    rotate = sub.add_parser("rotate", help="archive ~/.mitmproxy, mint a fresh CA, re-trust")
    rotate.add_argument("--force", action="store_true", help="rotate even if mitmdump looks running")
    rotate.set_defaults(func=cmd_trust_rotate)
    return parser


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "trust":
        _build_parser().parse_args(sys.argv[2:]).func(None)
    else:
        print("usage: dgx_proxy.py trust {install,status,remove,rotate}", file=sys.stderr)
        sys.exit(2)
