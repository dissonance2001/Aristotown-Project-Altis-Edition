#!/bin/bash
cd "$(dirname "$0")" || exit 1

find_python() {
    for candidate in \
        "/Library/Frameworks/Python.framework/Versions/2.7/bin/python2.7" \
        "/usr/local/bin/python2.7" \
        "/opt/local/bin/python2.7" \
        "$(command -v python2.7 2>/dev/null)" \
        "$(command -v python2 2>/dev/null)"; do
        if [ -n "$candidate" ] && [ -x "$candidate" ]; then
            echo "$candidate"
            return 0
        fi
    done
    return 1
}

PYTHON_BIN="$(find_python)"
if [ -z "$PYTHON_BIN" ]; then
    echo "Python 2.7 was not found."
    echo "Install the Python 2.7.18 macOS 64-bit installer, then run setup_macos.command."
    read -r -p "Press Enter to close..."
    exit 1
fi

run_python() {
    if [ "$(uname -m)" = "arm64" ]; then
        arch -x86_64 "$PYTHON_BIN" "$@"
    else
        "$PYTHON_BIN" "$@"
    fi
}

if ! run_python -c "import panda3d.core; import pandac.PandaModules" >/dev/null 2>&1; then
    echo "Panda3D for Python 2.7 was not found."
    echo "Run setup_macos.command first."
    read -r -p "Press Enter to close..."
    exit 1
fi

if [ -z "$TT_GAMESERVER" ]; then
    read -r -p "Server IP [127.0.0.1]: " TT_GAMESERVER
    TT_GAMESERVER="${TT_GAMESERVER:-127.0.0.1}"
fi

if [ -z "$TT_USERNAME" ]; then
    read -r -p "Username: " TT_USERNAME
fi

export TT_GAMESERVER
export TT_USERNAME
export TT_PLAYCOOKIE="$TT_USERNAME"
export TT_PASSWORD="$TT_USERNAME"

run_python -m toontown.toonbase.ClientStart
STATUS=$?
echo
if [ $STATUS -ne 0 ]; then
    echo "Project Altis exited with code $STATUS."
fi
read -r -p "Press Enter to close..."
exit $STATUS
