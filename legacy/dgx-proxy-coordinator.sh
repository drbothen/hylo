#!/bin/zsh
# Singleton coordinator for the claude-dgx invisible proxy (port auto-discovery + flock).
# Usage: dgx-proxy-coordinator.sh
#   Prints "PORT=<port>" on stdout and exits 0 if a healthy proxy exists or was started.
# State: ~/hylo/legacy/.proxy-state/{port,pid,lock}
set -u
BASE="${0:A:h}"
STATE="$BASE/.proxy-state"
LOCK="$STATE/lock"
START_RANGE=8090; END_RANGE=8143
STALE_SEC=120
mkdir -p "$STATE"

proxy_alive_on_port() {  # port -> 0 if a mitmdump actually LISTENs there
  lsof -nP -iTCP:"$1" -sTCP:LISTEN 2>/dev/null | grep -q mitmdump
}

state_valid() {  # state port file points at a live mitmdump
  local p pid
  [ -s "$STATE/port" ] || return 1
  p=$(<"$STATE/port"); pid=$(<"$STATE/pid" 2>/dev/null)
  [ -n "$p" ] && proxy_alive_on_port "$p" || return 1
  kill -0 "$pid" 2>/dev/null
}

start_new() {  # pick first free port, start mitmdump+addon, wait for LISTEN, record state
  local port=$START_RANGE
  while proxy_alive_on_port "$port" || lsof -nP -iTCP:"$port" -sTCP:LISTEN 2>/dev/null | grep -q .; do
    (( port++ )); (( port > END_RANGE )) && { echo "no free port in $START_RANGE-$END_RANGE" >&2; return 1; }
  done
  PYTHONUNBUFFERED=1 "$BASE/.mitmenv/bin/mitmdump" --set flow_detail=1 --listen-port "$port" \
    -s "$BASE/dgx_proxy.py" > "${TMPDIR:-/tmp}/dgx-shared-mitm.$port.log" 2>&1 &
  local pid=$!
  local i=0
  while (( i < 40 )); do proxy_alive_on_port "$port" && break; sleep 0.25; (( i++ )); done
  proxy_alive_on_port "$port" || { echo "mitmdump failed to bind :$port" >&2; kill $pid 2>/dev/null; return 1; }
  echo "$port" >| "$STATE/port"; echo "$pid" >| "$STATE/pid"
}

(
  # flock this dir: only one session may bootstrap at a time
  exec 9>"$LOCK"
  flock 9
  if state_valid; then exit 0; fi
  # kill leftovers of OUR prior state records if port is stale-but-occupied by something else
  start_new
) || exit 1

p=$(<"$STATE/port")
echo "PORT=$p"
