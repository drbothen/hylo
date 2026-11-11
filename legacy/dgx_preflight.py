#!/usr/bin/env python3
"""Preflight for claude-dgx: can THIS process (and so the proxy it is about to start)
open a TCP connection to the DGX vLLM endpoint?

Run it with the same Python the proxy uses: macOS Local Network permission is granted
per app, and a child process inherits it from the terminal app that launched it. A
terminal without it gets errno 65 (EHOSTUNREACH, "No route to host") for LAN addresses
while internet traffic still works — which is exactly how a stale iTerm helper
(iTermServer-3.6.10 after the 3.7.7 upgrade) broke every Sonnet request on 2026-11-11.

usage: dgx_preflight.py [upstream-url]     exit 0 = reachable, 1 = not (message on stdout)
"""
import errno
import socket
import sys
from urllib.parse import urlparse

url = sys.argv[1] if len(sys.argv) > 1 else "http://192.0.2.10:8080"
u = urlparse(url)
host, port = u.hostname or "192.0.2.10", u.port or 80

try:
    with socket.create_connection((host, port), timeout=4):
        pass
except OSError as e:
    if e.errno == errno.EHOSTUNREACH:
        print(f"cannot reach the DGX at {host}:{port} (No route to host).\n"
              "  On macOS this usually means this terminal app has no Local Network permission,\n"
              "  for example a window still hosted by an old iTerm helper after an iTerm upgrade.\n"
              "  Fix: open a NEW terminal window and run claude-dgx there, or allow the app in\n"
              "  System Settings > Privacy & Security > Local Network.")
    elif isinstance(e, socket.timeout) or e.errno in (errno.ETIMEDOUT, errno.EHOSTDOWN):
        print(f"cannot reach the DGX at {host}:{port} (timed out / host down).\n"
              "  Check the DGX is powered on and on the network: ssh dgx 'uptime'")
    elif e.errno == errno.ECONNREFUSED:
        print(f"the DGX at {host}:{port} refused the connection: vLLM is not listening.\n"
              "  It may be restarting (model load takes 3.5-7 min). Check:\n"
              "  ssh dgx 'sudo docker ps; curl -s -o /dev/null -w \"%{http_code}\" http://127.0.0.1:8080/health'")
    else:
        print(f"cannot reach the DGX at {host}:{port}: {e}")
    sys.exit(1)
