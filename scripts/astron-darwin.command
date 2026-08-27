#!/bin/bash

set -u

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ASTRON_DIR="$PROJECT_ROOT/dependencies/astron"

case "$(uname -m)" in
    arm64)
        ASTROND="$ASTRON_DIR/astrond-darwin-arm"
        ;;
    x86_64)
        ASTROND="$ASTRON_DIR/astrond-darwin"
        ;;
    *)
        echo "Unsupported macOS architecture: $(uname -m)"
        exit 1
        ;;
esac

if [ ! -f "$ASTROND" ]; then
    echo "Astron binary was not found: $ASTROND"
    exit 1
fi

chmod +x "$ASTROND"
cd "$ASTRON_DIR" || exit 1
exec "$ASTROND" --loglevel info config/cluster-yaml.yml
