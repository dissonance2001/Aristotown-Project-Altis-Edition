#!/bin/sh
set -eu

export PYTHONPATH="/tmp/altis-python-hooks:/tmp/altis-task-compat:/app/dependencies/python313-compat:/app${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX=/tmp/altis-pycache

prepare_task_compat() {
    source_task=/app/dependencies/python313-compat/direct/task/Task.py
    compat_root=/tmp/altis-task-compat
    if [ ! -f "$source_task" ]; then
        return
    fi

    mkdir -p "$compat_root/direct/task"
    python - "$source_task" "$compat_root/direct/task/Task.py" <<'PYCODE'
from pathlib import Path
import sys

source = Path(sys.argv[1]).read_text(encoding="utf-8")
target = Path(sys.argv[2])
old = "shield = Task.shield"
new = "try:\n    shield = Task.shield\nexcept AttributeError:\n    def shield(future):\n        return future"
if old in source:
    source = source.replace(old, new, 1)
target.write_text(source, encoding="utf-8")
PYCODE

    cat > "$compat_root/direct/__init__.py" <<'PYCODE'
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
PYCODE
    cat > "$compat_root/direct/task/__init__.py" <<'PYCODE'
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
PYCODE
}

prepare_toon_dna_compat() {
    hook_root=/tmp/altis-python-hooks
    mkdir -p "$hook_root"
    cat > "$hook_root/sitecustomize.py" <<'PYCODE'
import importlib.abc
import importlib.machinery
import socket
import sys
import dbm
import dbm.dumb

dbm.open = dbm.dumb.open

_TOON_DNA = "toontown.toon.ToonDNA"
_ASTRON_REPOSITORY = "direct.distributed.AstronInternalRepository"

class _PatchedToonDNALoader:
    def __init__(self, loader):
        self._loader = loader

    def create_module(self, spec):
        method = getattr(self._loader, "create_module", None)
        return method(spec) if method else None

    def exec_module(self, module):
        source = self._loader.get_source(module.__name__)
        lines = source.splitlines(keepends=True)
        changed = False
        for index, line in enumerate(lines):
            if line.strip() == "loadCustomClothing()":
                ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
                indent = line[:len(line) - len(line.lstrip())]
                lines[index] = indent + "pass" + ending
                changed = True
                break
        if not changed and "loadCustomClothing()" in source:
            raise RuntimeError("Could not disable the legacy clothing registry loader in ToonDNA.py")
        code = compile("".join(lines), self._loader.get_filename(module.__name__), "exec", dont_inherit=True)
        exec(code, module.__dict__)

    def __getattr__(self, name):
        return getattr(self._loader, name)

class _ToonDNAFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname != _TOON_DNA:
            return None
        spec = importlib.machinery.PathFinder.find_spec(fullname, path, target)
        if spec and spec.loader and callable(getattr(spec.loader, "get_source", None)):
            spec.loader = _PatchedToonDNALoader(spec.loader)
        return spec

class _AltisEventSocket:
    def __init__(self, host, port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._address = (host, int(port))

    def Send(self, data):
        if isinstance(data, str):
            try:
                data = data.encode("latin-1")
            except UnicodeEncodeError:
                data = data.encode("utf-8")
        elif isinstance(data, memoryview):
            data = data.tobytes()
        self._socket.sendto(bytes(data), self._address)
        return True

    def close(self):
        self._socket.close()


def _patch_astron_repository(module):
    repository = module.AstronInternalRepository

    def setEventLogHost(self, host, port=7197):
        previous = getattr(self, "eventSocket", None)
        if isinstance(previous, _AltisEventSocket):
            previous.close()
        if not host:
            self.eventSocket = None
            return
        self.eventSocket = _AltisEventSocket(host, port)

    repository.setEventLogHost = setEventLogHost

class _AstronRepositoryLoader:
    def __init__(self, loader):
        self._loader = loader

    def create_module(self, spec):
        method = getattr(self._loader, "create_module", None)
        return method(spec) if method else None

    def exec_module(self, module):
        self._loader.exec_module(module)
        _patch_astron_repository(module)

    def __getattr__(self, name):
        return getattr(self._loader, name)

class _AstronRepositoryFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname != _ASTRON_REPOSITORY:
            return None
        spec = importlib.machinery.PathFinder.find_spec(fullname, path, target)
        if spec and spec.loader:
            spec.loader = _AstronRepositoryLoader(spec.loader)
        return spec

sys.meta_path.insert(0, _ToonDNAFinder())
sys.meta_path.insert(0, _AstronRepositoryFinder())
PYCODE
}
prepare_account_bridge() {
    mkdir -p /app/user
    python - <<'PYCODE'
import base64
import dbm.dumb
import importlib
import json
import os
import shutil
import time

base = "/app/user/account-bridge"
export_path = "/app/user/account-bridge-export.json"
temporary = "/app/user/.account-bridge-migration"
suffixes = ("", ".db", ".dat", ".dir", ".bak", ".pag")


def paths(prefix):
    return [prefix + suffix for suffix in suffixes if os.path.isfile(prefix + suffix)]


def as_bytes(value):
    return value if isinstance(value, bytes) else str(value).encode("utf-8")


def read_database(prefix):
    if not paths(prefix):
        return None, []
    errors = []
    openers = [dbm.dumb.open]
    for module_name in ("dbm.gnu", "dbm.ndbm"):
        try:
            openers.append(importlib.import_module(module_name).open)
        except (ImportError, OSError):
            pass
    for opener in openers:
        try:
            with opener(prefix, "r") as database:
                return {as_bytes(key): as_bytes(database[key]) for key in database.keys()}, []
        except Exception as error:
            errors.append("%s: %s" % (getattr(opener, "__module__", opener), error))
    return None, errors


def preserve(prefix):
    saved = []
    stamp = str(int(time.time()))
    for path in paths(prefix):
        backup = path + ".pre-docker-recovery." + stamp
        suffix = 1
        while os.path.exists(backup):
            backup = path + ".pre-docker-recovery." + stamp + "." + str(suffix)
            suffix += 1
        shutil.copy2(path, backup)
        saved.append(backup)
    return saved


export_data = None
if os.path.isfile(export_path):
    try:
        with open(export_path, "r", encoding="utf-8") as stream:
            exported = json.load(stream)
        if exported.get("format") != "altis-account-bridge-v1" or not isinstance(exported.get("entries"), list):
            raise ValueError("unknown export format")
        export_data = {
            base64.b64decode(item[0], validate=True): base64.b64decode(item[1], validate=True)
            for item in exported["entries"]
            if isinstance(item, list) and len(item) == 2
        }
    except Exception as error:
        raise RuntimeError("The host-side account bridge export is invalid: %s" % error) from error

current_data, current_errors = read_database(base)
if export_data is None:
    if current_data is None and paths(base):
        raise RuntimeError(
            "The account bridge at %s is not readable in Linux, and no host-side export is available. "
            "Run Start-Aristotown-Docker.bat so the bundled Windows Python can export it safely. "
            "Existing bridge files have been left untouched. Errors: %s"
            % (base, "; ".join(current_errors))
        )
    export_data = {}

if current_data is None and paths(base) and not export_data:
    raise RuntimeError(
        "The account bridge at %s is unreadable and the host-side export contains no mappings. "
        "Refusing to overwrite it or create a blank mapping. Existing files have been left untouched."
        % base
    )

merged = dict(current_data or {})
merged.update(export_data)
target_is_dumb = os.path.isfile(base + ".dat") and os.path.isfile(base + ".dir") and current_data is not None

if current_data is None or not target_is_dumb or merged != current_data:
    for path in paths(temporary):
        os.remove(path)
    with dbm.dumb.open(temporary, "n") as database:
        for key, value in merged.items():
            database[key] = value

    generated = paths(temporary)
    if not os.path.isfile(temporary + ".dat") or not os.path.isfile(temporary + ".dir"):
        raise RuntimeError("Could not create a complete writable account bridge database")
    with dbm.dumb.open(temporary, "r") as database:
        verified = {as_bytes(key): as_bytes(database[key]) for key in database.keys()}
    if verified != merged:
        raise RuntimeError("The migrated account bridge failed verification; the original files were left untouched")

    if paths(base):
        saved = preserve(base)
        print("Preserved the previous account bridge files: %s" % ", ".join(saved))
    for path in paths(base):
        os.remove(path)
    for path in generated:
        os.replace(path, base + path[len(temporary):])

print("Account bridge ready (%d mapping(s))." % len(merged))
PYCODE
}
select_mongo_uri() {
    if python - <<'PYCODE'
import socket
import sys
try:
    with socket.create_connection(("host.docker.internal", 27017), timeout=1.5):
        sys.exit(0)
except OSError:
    sys.exit(1)
PYCODE
    then
        ALTIS_MONGO_URI=mongodb://host.docker.internal:27017/astrondb
        echo "Using the installed MongoDB on the Windows host."
    else
        ALTIS_MONGO_URI=mongodb://mongo:27017/astrondb
        echo "No reachable host MongoDB found; using the source MongoDB container."
        attempts=0
        until nc -z -w 2 mongo 27017 >/dev/null 2>&1; do
            attempts=$((attempts + 1))
            if [ "$attempts" -ge 90 ]; then
                echo "ERROR: Neither host MongoDB nor the source MongoDB container is reachable." >&2
                exit 1
            fi
            sleep 1
        done
    fi
    export ALTIS_MONGO_URI
}

make_docker_prc() {
    printf 'mongodb-url %s\naccount-bridge-filename /app/user/account-bridge\n' "$ALTIS_MONGO_URI" > /tmp/altis-docker.prc
}

make_astron_config() {
    source_config=/app/dependencies/astron/config/cluster.yml
    if [ ! -f "$source_config" ]; then
        echo "ERROR: Altis Astron config not found: $source_config" >&2
        exit 1
    fi

    sed -E \
        -e 's#bind: 127\.0\.0\.1:7199#bind: 0.0.0.0:7199#g' \
        -e 's#bind: 127\.0\.0\.1:7197#bind: 0.0.0.0:7197#g' \
        -e "s#mongodb://(127\\.0\\.0\\.1|localhost|mongodb|mongo|host\\.docker\\.internal)(:27017)?/astrondb#${ALTIS_MONGO_URI}#g" \
        -e 's#../dclass/toon.dc#/app/dependencies/astron/dclass/toon.dc#g' \
        -e 's#../logs/events-%y%m%d_%H%M%S.log#/var/log/altis/events-%y%m%d_%H%M%S.log#g' \
        "$source_config" > /tmp/altis-cluster-docker.yml
}

case "${1:-}" in
    astron)
        select_mongo_uri
        make_astron_config
        exec /usr/local/bin/astrond --loglevel info /tmp/altis-cluster-docker.yml
        ;;
    uberdog)
        select_mongo_uri
        prepare_task_compat
        prepare_toon_dna_compat
        prepare_account_bridge
        make_docker_prc
        exec python -u -X faulthandler -m toontown.uberdog.ServiceStart \
            --base-channel 1000000 \
            --max-channels 999999 \
            --stateserver 4002 \
            --astron-ip astron:7199 \
            --eventlogger-ip astron:7197 \
            /app/dependencies/config/general.prc \
            /app/dependencies/config/release/dev.prc \
            /tmp/altis-docker.prc
        ;;
    ai)
        select_mongo_uri
        prepare_task_compat
        prepare_toon_dna_compat
        make_docker_prc
        exec python -u -X faulthandler -m toontown.ai.ServiceStart \
            --base-channel 402000000 \
            --max-channels 999999 \
            --stateserver 4002 \
            --astron-ip astron:7199 \
            --eventlogger-ip astron:7197 \
            --district-name Nuttyriver \
            /app/dependencies/config/general.prc \
            /app/dependencies/config/release/dev.prc \
            /tmp/altis-docker.prc
        ;;
    *)
        echo "Usage: start.sh {astron|uberdog|ai}" >&2
        exit 2
        ;;
esac
