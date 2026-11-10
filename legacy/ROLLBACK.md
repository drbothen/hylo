# claude-dgx rollback / handoff

Last known-good checkpoint: `checkpoint-20261109-<HHMM>/` in this directory (checksummed).
`claude --version` at checkpoint time: see `checkpoint-*/claude-version.txt`.

## Rollback the laptop side (claude-dgx + router)

```bash
cd ~/hylo/legacy
# stop any live routers (they are per-session and die with their shells, but be safe)
pkill -f opus_router.py 2>/dev/null
# restore the checkpoint over the live files
cp checkpoint-*/claude-dgx checkpoint-*/opus_router.py checkpoint-*/auto_continue.py .
cp checkpoint-*/profile.env ~/.config/dgx-llm/profile.env
# start a NEW claude-dgx session; old sessions keep whatever router they started with
```

Man-in-the-middle spikes (2026-11-09) add NOTHING machine-wide: mitmproxy lives in
`dgx-llm/.mitmenv` (venv), its CA in `~/.mitmproxy/`, and the `HTTPS_PROXY` /
`NODE_EXTRA_CA_CERTS` env vars are set only inside spike shells. To scrub:

```bash
pkill -f mitmdump; rm -rf ~/hylo/legacy/.mitmenv ~/.mitmproxy
# macOS keychain: only if you installed the CA there (spike fallback) —
#   Keychain Access → System → delete 'mitmproxy' certificate
```

## Rollback the DGX side (serving)

State is decided by what serves :8080 — see memory file `dgx-warlock-opus-serving.md`:
- Warlock (llama.cpp): `ssh dgx 'sudo systemctl start warlock-llm'` (unit = -c 524288 MTP; NOTE
  still `enabled`, so after a DGX reboot IT takes :8080 back)
- dealignai Flash (vLLM 0.31, NGC 26.10): `ssh dgx ~/llm/serve-flash.sh` (~7 min)
- full uncensored NVFP4: `~/llm/bench/vllm-run.sh` variants, or serve-vllm.sh (120k, 26.08 image)
- After switching backends update `~/.config/dgx-llm/profile.env` (one active block; rule:
  compact+output < server ctx) — checkpointed copy matches the Flash backend.

## Remote Control / invisible-proxy spikes (2026-11-09)

Outcome recorded at the bottom of this file as SPIKE RESULTS. If spikes are abandoned:
`pkill -f mitmdump` and use the checkpoint — nothing else persists.

## Checkpoints (2026-11-09)
- `checkpoint-20261109-*` (first, no "-invisible" suffix): VISIBLE-router-only stack, before the invisible proxy.
- `checkpoint-20261109-1146-invisible`: WORKING invisible-proxy stack (default DGX_INVISIBLE=1, DGX_REMOTE=1 adds --remote-control).
  Restore: `cp checkpoint-20261109-1146-invisible/{claude-dgx,opus_router.py,auto_continue.py,dgx_proxy.py} . && cp checkpoint-20261109-1146-invisible/profile.env ~/.config/dgx-llm/`

## SPIKE RESULTS / known pitfalls (2026-11-09)
- Both spikes passed: Claude Code trusts the mitmproxy CA via NODE_EXTRA_CA_CERTS; `claude remote-control` connects through the proxy.
- /remote-control is a REAL slash command, but Claude Code hides it ("Unknown command") whenever ANTHROPIC_BASE_URL
  is set. Bug fixed 11:45: launcher line exporting ANTHROPIC_BASE_URL still defaulted DGX_INVISIBLE to 0 → it set the
  variable to a router that was never started (502 to 127.0.0.1:4143) AND hid /remote-control. Invisible mode now
  explicitly unsets it.
- tmux servers keep the environment they were started from: a tmux server started from a visible-mode session carries
  ANTHROPIC_BASE_URL into every pane. The launcher now unsets it, so this no longer matters for claude-dgx.
