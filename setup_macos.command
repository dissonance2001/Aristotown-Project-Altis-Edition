#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv313"
COMPAT_ROOT="$PROJECT_ROOT/dependencies/python313-compat"
SOURCE_DIRECT="$PROJECT_ROOT/dependencies/panda/direct"
PYTHON_BIN=""

for candidate in \
    "$(command -v python3.13 2>/dev/null || true)" \
    "/opt/homebrew/bin/python3.13" \
    "/usr/local/bin/python3.13"; do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
        PYTHON_BIN="$candidate"
        break
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "Python 3.13 (64-bit) was not found."
    echo "Install Python 3.13, then run ./setup_macos.command again."
    read -r -p "Press Enter to close..."
    exit 1
fi

if [ -x "$VENV_DIR/bin/python" ]; then
    if ! "$VENV_DIR/bin/python" -c 'import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 13) else 1)' 2>/dev/null; then
        echo "The existing .venv313 is not a Python 3.13 environment: $VENV_DIR"
        echo "Rename or remove only .venv313, then run this setup again."
        read -r -p "Press Enter to close..."
        exit 1
    fi
else
    if [ -e "$VENV_DIR" ]; then
        echo "The path exists but is not a usable virtual environment: $VENV_DIR"
        read -r -p "Press Enter to close..."
        exit 1
    fi
    echo "Creating Python 3.13 environment at $VENV_DIR..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

if [ ! -d "$COMPAT_ROOT/direct" ]; then
    if [ ! -d "$SOURCE_DIRECT" ]; then
        echo "Altis's Direct compatibility package was not found."
        echo "Expected either: $COMPAT_ROOT/direct"
        echo "or: $SOURCE_DIRECT"
        echo "Restore the Altis Direct source before running this setup."
        read -r -p "Press Enter to close..."
        exit 1
    fi
    mkdir -p "$COMPAT_ROOT"
    cp -R "$SOURCE_DIRECT" "$COMPAT_ROOT/direct"
fi

PYTHON="$VENV_DIR/bin/python"
if [ ! -f "$PROJECT_ROOT/requirements.txt" ]; then
    echo "requirements.txt was not found in the Altis source root."
    read -r -p "Press Enter to close..."
    exit 1
fi

echo "Installing the existing requirements.txt..."
"$PYTHON" -m pip install --upgrade pip
"$PYTHON" -m pip install -r "$PROJECT_ROOT/requirements.txt"

echo "Installing the macOS Python 3.13 Panda3D build and tested compatibility pins..."
"$PYTHON" -m pip install \
    --index-url https://pypi.org/simple \
    --extra-index-url https://archive.panda3d.org/ \
    "panda3d==1.11.0.dev3895" \
    "pymongo==4.9.2" \
    "StrEnum==0.4.15" \
    "six==1.17.0"

"$PYTHON" -m pip check
PYTHONPATH="$COMPAT_ROOT" "$PYTHON" - <<'PY'
import panda3d.core
import pymongo
import six
import strenum
import direct
import raven
import requests
import Crypto
import yaml
import semidbm
from direct.distributed.AstronInternalRepository import AstronInternalRepository

print("Panda3D:", panda3d.core.PandaSystem.getVersionString())
print("PyMongo:", pymongo.version)
print("StrEnum module:", strenum.__file__)
print("Direct:", direct.__file__)
print("All requirements imports and Altis Astron repository import: OK")
PY

echo
echo "Python 3.13 setup complete."
echo "Environment: $VENV_DIR"
echo "Direct compatibility path: $COMPAT_ROOT"
echo "Launch the client with ./start_macos.command."
read -r -p "Press Enter to close..."
