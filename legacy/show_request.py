#!/usr/bin/env python3
"""Pretty-print a request saved by opus_router.py (ROUTER_DUMP_DIR).

usage: show_request.py [FILE]        (default: newest file in ~/dgx-llm-dumps)
       show_request.py FILE --system  (system prompt text only)
"""
import glob
import json
import os
import sys

args = [a for a in sys.argv[1:] if not a.startswith("--")]
path = args[0] if args else max(glob.glob(os.path.expanduser("~/dgx-llm-dumps/*-messages.json")), key=os.path.getmtime)
req = json.load(open(path))

system = req.get("system", "")
blocks = [system] if isinstance(system, str) else [b.get("text", "") for b in system if isinstance(b, dict)]
system_text = "\n\n".join(blocks)

if "--system" in sys.argv:
    print(system_text)
    sys.exit()

print(f"file:     {path}")
print(f"model:    {req.get('model')}   max_tokens: {req.get('max_tokens')}   thinking: {req.get('thinking')}")
print(f"system:   {len(blocks)} block(s), {len(system_text):,} chars")
tools = req.get("tools", [])
print(f"tools:    {len(tools)} -> {', '.join(t.get('name', '?') for t in tools)}")
msgs = req.get("messages", [])
print(f"messages: {len(msgs)}  (roles: {' '.join(m.get('role', '?')[0] for m in msgs)})")
print("\n--- system prompt (first 3000 chars; use --system for all) ---\n")
print(system_text[:3000])
