#!/bin/bash
set -u

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
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

if [ ! -d "$COMPAT_ROOT/direct" ]; then
    echo "Altis Direct compatibility files not found: $COMPAT_ROOT/direct"
    echo "Run ./setup_macos.command and check its output."
    read -r -p "Press Enter to close..."
    exit 1
fi

export PYTHONPATH="$COMPAT_ROOT${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONPYCACHEPREFIX="$PROJECT_ROOT/dependencies/python313-pycache-macos"
export PYTHONUNBUFFERED=1
export PYTHONFAULTHANDLER=1

if ! "$PYTHON" -c 'import panda3d.core; import direct.extensions_native; from direct.distributed.AstronInternalRepository import AstronInternalRepository' >/dev/null 2>&1; then
    echo "The Python 3.13/Panda3D imports did not pass."
    echo "Run ./setup_macos.command again and share its output if it fails."
    read -r -p "Press Enter to close..."
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
export TT_PLAYCOOKIE="${TT_PLAYCOOKIE:-$TT_USERNAME}"
export TT_PASSWORD="${TT_PASSWORD:-$TT_USERNAME}"

"$PYTHON" -u -X faulthandler -m toontown.toonbase.ClientStart
STATUS=$?

if [ "$STATUS" -ne 0 ]; then
    echo "Project Altis exited with code $STATUS."
    read -r -p "Press Enter to close..."
fi
exit "$STATUS"
