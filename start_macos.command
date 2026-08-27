#!/bin/bash

set -u

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
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

if ! python -c 'import panda3d.core; import pandac.PandaModules; import direct.distributed.AstronInternalRepository' >/dev/null 2>&1; then
    echo "The Altis Panda3D/Astron build is not installed in $VENV_DIR."
    echo "Install the macOS build of the Altis Panda3D fork into this environment first."
    exit 1
fi

if [ -z "${TT_GAMESERVER:-}" ]; then
    read -r -p "Server IP [127.0.0.1]: " TT_GAMESERVER
    TT_GAMESERVER="${TT_GAMESERVER:-127.0.0.1}"
fi

if [ -z "${TT_USERNAME:-}" ]; then
    read -r -p "Username: " TT_USERNAME
fi

export TT_GAMESERVER
export TT_USERNAME
export TT_PLAYCOOKIE="$TT_USERNAME"
export TT_PASSWORD="$TT_USERNAME"

python -m toontown.toonbase.ClientStart
STATUS=$?

if [ $STATUS -ne 0 ]; then
    echo "Project Altis exited with code $STATUS."
fi
exit $STATUS
