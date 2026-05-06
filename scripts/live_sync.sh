#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOG_FILE="${REPO_ROOT}/.git/revtrack_live_sync.log"
TMUX_SESSION="revtrack_live_sync"

sync_once() {
  cd "${REPO_ROOT}"
  if [[ -z "$(git status --porcelain)" ]]; then
    return 0
  fi

  git add -A
  if git diff --cached --quiet; then
    return 0
  fi

  local ts
  ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  git commit -m "live sync: ${ts}" || true
  git push origin "$(git rev-parse --abbrev-ref HEAD)"
}

is_running() {
  tmux has-session -t "${TMUX_SESSION}" 2>/dev/null
}

start_loop() {
  local interval="${1:-120}"
  if is_running; then
    echo "live-sync already running (tmux session: ${TMUX_SESSION})"
    return 0
  fi

  tmux new-session -d -s "${TMUX_SESSION}" "cd '${REPO_ROOT}' && while true; do '${REPO_ROOT}/scripts/live_sync.sh' once || true; sleep '${interval}'; done >> '${LOG_FILE}' 2>&1"
  echo "live-sync started (tmux session: ${TMUX_SESSION}, interval=${interval}s)"
  echo "attach: tmux attach -t ${TMUX_SESSION}"
}

stop_loop() {
  if ! is_running; then
    echo "live-sync is not running"
    return 0
  fi

  tmux kill-session -t "${TMUX_SESSION}"
  echo "live-sync stopped (tmux session: ${TMUX_SESSION})"
}

status_loop() {
  if is_running; then
    echo "live-sync running (tmux session: ${TMUX_SESSION})"
  else
    echo "live-sync stopped"
  fi
  echo "log: ${LOG_FILE}"
}

usage() {
  cat <<EOF
Usage:
  scripts/live_sync.sh start [interval_seconds]
  scripts/live_sync.sh stop
  scripts/live_sync.sh status
  scripts/live_sync.sh once
EOF
}

cmd="${1:-}"
case "${cmd}" in
  start)
    start_loop "${2:-120}"
    ;;
  stop)
    stop_loop
    ;;
  status)
    status_loop
    ;;
  once)
    sync_once
    ;;
  *)
    usage
    exit 1
    ;;
esac
