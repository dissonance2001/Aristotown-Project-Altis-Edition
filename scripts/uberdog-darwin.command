#!/bin/bash
set -u

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

VENV_DIR="$PROJECT_ROOT/.venv313"
PYTHON="$VENV_DIR/bin/python"
COMPAT_ROOT="$PROJECT_ROOT/dependencies/python313-compat"

if [ ! -x "$PYTHON" ]; then
    echo "Python 3.13 environment not found: $VENV_DIR"
    echo "Run ./setup_macos.command first."
    read -r -p "Press Enter to close..."
    exit 1
fi

export PYTHONPATH="$COMPAT_ROOT${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONPYCACHEPREFIX="$PROJECT_ROOT/dependencies/python313-pycache-macos"
export PYTHONUNBUFFERED=1
export PYTHONFAULTHANDLER=1

MAX_CHANNELS=999999
STATESERVER=4002
ASTRON_IP="127.0.0.1:7199"
EVENTLOGGER_IP="127.0.0.1:7197"
BASE_CHANNEL="${BASE_CHANNEL:-1000000}"

while true; do
    "$PYTHON" -u -X faulthandler -m toontown.uberdog.ServiceStart --base-channel "$BASE_CHANNEL" \
        --max-channels "$MAX_CHANNELS" --stateserver "$STATESERVER" \
        --astron-ip "$ASTRON_IP" --eventlogger-ip "$EVENTLOGGER_IP"
    STATUS=$?
    echo "Altis UberDOG exited with code $STATUS; restarting in 2 seconds..."
    sleep 2
done
