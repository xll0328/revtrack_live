#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PID_FILE="${REPO_ROOT}/.git/revtrack_live_sync.pid"
LOG_FILE="${REPO_ROOT}/.git/revtrack_live_sync.log"

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
  if [[ -f "${PID_FILE}" ]]; then
    local pid
    pid="$(cat "${PID_FILE}")"
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      return 0
    fi
  fi
  return 1
}

start_loop() {
  local interval="${1:-120}"
  if is_running; then
    echo "live-sync already running (pid=$(cat "${PID_FILE}"))"
    return 0
  fi

  nohup "${BASH_SOURCE[0]}" daemon "${interval}" >>"${LOG_FILE}" 2>&1 &

  echo "$!" >"${PID_FILE}"
  echo "live-sync started (pid=$!, interval=${interval}s)"
}

stop_loop() {
  if ! [[ -f "${PID_FILE}" ]]; then
    echo "live-sync is not running"
    return 0
  fi

  local pid
  pid="$(cat "${PID_FILE}")"
  if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
    kill "${pid}"
    echo "live-sync stopped (pid=${pid})"
  else
    echo "live-sync pid file exists but process is not running"
  fi
  rm -f "${PID_FILE}"
}

status_loop() {
  if is_running; then
    echo "live-sync running (pid=$(cat "${PID_FILE}"))"
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

daemon_loop() {
  local interval="${1:-120}"
  cd "${REPO_ROOT}"
  while true; do
    sync_once
    sleep "${interval}"
  done
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
  daemon)
    daemon_loop "${2:-120}"
    ;;
  *)
    usage
    exit 1
    ;;
esac
