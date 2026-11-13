#!/usr/bin/env bash
# Usage: close_patch.sh <pid>
# Gracefully stops the pd process, force-kills after a timeout.
set -uo pipefail

PID="${1:?usage: close_patch.sh <pid>}"
TIMEOUT="${CLOSE_TIMEOUT:-3}"

kill -0 "$PID" 2>/dev/null || exit 0   # already gone

kill -TERM "$PID"
for _ in $(seq $((TIMEOUT * 10))); do
    kill -0 "$PID" 2>/dev/null || exit 0
    sleep 0.1
done

kill -KILL "$PID" 2>/dev/null
exit 0