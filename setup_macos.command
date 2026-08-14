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
    echo "Install the Python 2.7.18 macOS 64-bit installer first."
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

if [ "$(uname -m)" = "arm64" ]; then
    if ! arch -x86_64 "$PYTHON_BIN" -c "import sys; print(sys.version)" >/dev/null 2>&1; then
        echo "The Intel Python 2.7 runtime could not start."
        echo "Install Rosetta 2, then run this setup again."
        read -r -p "Press Enter to close..."
        exit 1
    fi
fi

run_python -m ensurepip --upgrade
run_python -m pip install --user --upgrade "pip<21" "setuptools<45"
run_python -m pip install --user "panda3d==1.10.10"

if run_python -c "import panda3d.core; import pandac.PandaModules" >/dev/null 2>&1; then
    echo
    echo "Panda3D is ready."
    echo "You can now run start_macos.command."
else
    echo
    echo "Panda3D installation did not pass the import test."
    exit 1
fi

read -r -p "Press Enter to close..."
