#!/bin/bash

set -u

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

if [ -d .venv ]; then
    VENV_DIR="$PROJECT_ROOT/.venv"
elif [ -d venv ]; then
    VENV_DIR="$PROJECT_ROOT/venv"
else
    if ! command -v python3.9 >/dev/null 2>&1; then
        echo "Python 3.9 is required but was not found on PATH."
        exit 1
    fi

    VENV_DIR="$PROJECT_ROOT/.venv"
    echo "Creating Python 3.9 virtual environment at $VENV_DIR..."
    python3.9 -m venv "$VENV_DIR" || exit 1
fi

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate" || exit 1

MAX_CHANNELS=999999
STATESERVER=4002
ASTRON_IP="127.0.0.1:7199"
EVENTLOGGER_IP="127.0.0.1:7197"
BASE_CHANNEL="${BASE_CHANNEL:-1000000}"

while true; do
    python -m toontown.uberdog.ServiceStart --base-channel "$BASE_CHANNEL" \
        --max-channels "$MAX_CHANNELS" --stateserver "$STATESERVER" \
        --astron-ip "$ASTRON_IP" --eventlogger-ip "$EVENTLOGGER_IP"
done
