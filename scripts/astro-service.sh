#!/usr/bin/env bash
# ASTRO background runner. Starts the web UI on a stable port and logs to ~/.astro/astro.log.
set -euo pipefail

PORT="${ASTRO_PORT:-8080}"
HOST="${ASTRO_HOST:-127.0.0.1}"
VAULT_PATH="${ASTRO_VAULT:-$HOME/Documents/notes}"
PIDFILE="$HOME/.astro/astro.pid"
LOGFILE="$HOME/.astro/astro.log"

start() {
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        echo "ASTRO is already running (pid $(cat "$PIDFILE"))"
        return 0
    fi
    mkdir -p "$HOME/.astro"
    nohup astro serve "$VAULT_PATH" --host "$HOST" --port "$PORT" > "$LOGFILE" 2>&1 &
    echo $! > "$PIDFILE"
    echo "ASTRO started on http://$HOST:$PORT (pid $(cat "$PIDFILE"))"
}

stop() {
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        kill "$(cat "$PIDFILE")"
        rm -f "$PIDFILE"
        echo "ASTRO stopped"
    else
        echo "ASTRO not running"
    fi
}

status() {
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        echo "ASTRO running (pid $(cat "$PIDFILE"))"
    else
        echo "ASTRO not running"
    fi
}

case "${1:-start}" in
    start) start ;;
    stop) stop ;;
    restart) stop; sleep 1; start ;;
    status) status ;;
    *) echo "Usage: $0 {start|stop|restart|status}" ; exit 1 ;;
esac
