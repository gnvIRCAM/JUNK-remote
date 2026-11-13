#!/usr/bin/env bash
# Usage: load_patch.sh <patch_dir>
# Starts Pure Data headless on the patch's entry file.
# Uses `exec` so the PID seen by Python *is* the pd process.
set -euo pipefail

PATCH_DIR="${1:?usage: load_patch.sh <patch_dir>}"
PD_BIN="${PD_BIN:-pd}"
# PD_FLAGS="${PD_FLAGS:--nogui -noprefs -alsa -r 44100}"
PD_FLAGS="${PD_FLAGS:--noprefs -alsa -r 44100}"


if [[ ! -d "$PATCH_DIR" ]]; then
    echo "load_patch: '$PATCH_DIR' is not a directory" >&2
    exit 1
fi

if [[ -f "$PATCH_DIR/main.pd" ]]; then
    PATCH_FILE="$PATCH_DIR/main.pd"
else
    PATCH_FILE="$(find "$PATCH_DIR" -maxdepth 1 -name '*.pd' | sort | head -n 1)"
fi

if [[ -z "${PATCH_FILE:-}" ]]; then
    echo "load_patch: no .pd file found in '$PATCH_DIR'" >&2
    exit 2
fi

cd "$PATCH_DIR"   # so relative abstractions/samples resolve
# shellcheck disable=SC2086
exec "$PD_BIN" $PD_FLAGS -path "$PATCH_DIR" -open "$PATCH_FILE"