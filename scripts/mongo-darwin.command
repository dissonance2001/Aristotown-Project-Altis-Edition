#!/bin/bash

set -u

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DBPATH="$PROJECT_ROOT/dependencies/astron/mongo/astrondb"

MONGOD_BIN=""
if command -v mongod >/dev/null 2>&1; then
    MONGOD_BIN="$(command -v mongod)"
elif [ -x "/opt/homebrew/bin/mongod" ]; then
    MONGOD_BIN="/opt/homebrew/bin/mongod"
elif [ -x "/usr/local/bin/mongod" ]; then
    MONGOD_BIN="/usr/local/bin/mongod"
fi

if [ -z "$MONGOD_BIN" ]; then
    echo "MongoDB (mongod) was not found on your system."
    echo "You can install it using Homebrew:"
    echo "    brew tap mongodb/brew"
    echo "    brew install mongodb-community"
    read -r -p "Press Enter to exit..."
    exit 1
fi

if nc -z 127.0.0.1 27017 2>/dev/null; then
    echo "MongoDB is already running and listening on 127.0.0.1:27017 (e.g. via brew services)."
    echo "You're all set! You can leave this window or close it."
    read -r -p "Press Enter to exit..."
    exit 0
fi

mkdir -p "$DBPATH"
echo "Starting MongoDB using $MONGOD_BIN..."
echo "Database path: $DBPATH"
exec "$MONGOD_BIN" --dbpath "$DBPATH" --bind_ip 127.0.0.1 --port 27017
