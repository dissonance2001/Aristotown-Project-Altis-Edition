import base64
import dbm
import importlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

SUFFIXES = (".dat", ".dir", ".bak", ".pag", ".db", ".dbm", ".gdbm", ".ddb")
BACKUP_MARKER = re.compile(r"\.pre-docker-recovery(?:\..*)?$", re.IGNORECASE)
BACKUP_FILE = re.compile(
    r"^(?P<base>.+?)(?P<extension>\.(?:dat|dir|bak|pag|db|dbm|gdbm|ddb))(?P<marker>\.pre-docker-recovery(?:\..*)?)$",
    re.IGNORECASE,
)


def to_bytes(value):
    return value if isinstance(value, bytes) else str(value).encode("utf-8")


def opener_list():
    result = [dbm.open]
    for module_name in ("dbm.dumb", "dbm.ndbm", "dbm.gnu"):
        try:
            opener = importlib.import_module(module_name).open
        except (ImportError, OSError):
            continue
        if opener not in result:
            result.append(opener)
    return result


OPENERS = opener_list()


def read_database(prefix):
    errors = []
    for opener in OPENERS:
        try:
            with opener(str(prefix), "r") as database:
                entries = {to_bytes(key): to_bytes(database[key]) for key in database.keys()}
            return entries, None
        except Exception as error:
            errors.append("%s: %s" % (getattr(opener, "__module__", "dbm"), error))
    return None, "; ".join(errors)


def config_candidates(root):
    results = []
    config_roots = [root / "dependencies" / "config", root]
    seen = set()
    for config_root in config_roots:
        if not config_root.exists():
            continue
        for current, dirs, files in os.walk(str(config_root)):
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", ".venv", "venv", "node_modules", "dependencies", "resources", "build", "dist"}]
            for filename in files:
                if not filename.lower().endswith((".prc", ".cfg", ".ini", ".bat", ".cmd")):
                    continue
                file_path = os.path.join(current, filename)
                if file_path in seen:
                    continue
                seen.add(file_path)
                try:
                    content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                for line in content.splitlines():
                    match = re.match(r"\s*account-bridge-filename\s+(.+?)\s*(?:#.*)?$", line, re.IGNORECASE)
                    if not match:
                        continue
                    value = os.path.expandvars(match.group(1).strip().strip("\"'"))
                    candidate = Path(value)
                    if not candidate.is_absolute():
                        candidate = root / candidate
                    results.append(candidate)
    return results


def has_files(prefix):
    text = str(prefix)
    return os.path.isfile(text) or any(os.path.isfile(text + suffix) for suffix in SUFFIXES)


def collect_live_candidates(root, requested_base):
    result = []
    seen = set()

    def add(prefix):
        text = os.path.abspath(str(prefix))
        key = os.path.normcase(text)
        if key not in seen:
            seen.add(key)
            result.append(text)

    add(requested_base)
    add(root / "account-bridge")
    add(root / "user" / "account-bridge")
    add(root / "account-bridge.dbm")
    add(root / "user" / "account-bridge.dbm")
    for configured in config_candidates(root):
        add(configured)

    return [prefix for prefix in result if has_files(prefix)]


def scan_roots(root):
    roots = [root, root / "user", root / "dependencies" / "config"]
    found = set()
    ignored = {".git", "resources", "dependencies", ".venv", "venv", "node_modules", "__pycache__", "build", "dist"}
    for scan_root in roots:
        if not scan_root.exists():
            continue
        for current, dirs, files in os.walk(str(scan_root)):
            dirs[:] = [d for d in dirs if d not in ignored]
            for filename in files:
                if "account-bridge" in filename.lower():
                    found.add(os.path.abspath(os.path.join(current, filename)))
    return sorted(found)


def read_backup_databases(root, scratch):
    groups = {}
    backup_paths = scan_roots(root)
    for file_path in backup_paths:
        filename = os.path.basename(file_path)
        match = BACKUP_FILE.match(filename)
        if not match:
            continue
        directory = os.path.dirname(file_path)
        key = (directory, match.group("base"), match.group("marker"))
        groups.setdefault(key, {})[match.group("extension").lower()] = file_path

    readable = []
    unreadable = []
    for index, ((directory, base_name, marker), files) in enumerate(groups.items()):
        label = os.path.join(directory, base_name + marker)
        if ".dat" in files and ".dir" in files:
            normalized = os.path.join(scratch, "backup-%04d" % index)
            try:
                shutil.copy2(files[".dat"], normalized + ".dat")
                shutil.copy2(files[".dir"], normalized + ".dir")
                entries, error = read_database(normalized)
            except OSError as error:
                entries, error = None, str(error)
        elif ".db" in files:
            normalized = os.path.join(scratch, "backup-%04d.db" % index)
            try:
                shutil.copy2(files[".db"], normalized)
                entries, error = read_database(normalized)
            except OSError as error:
                entries, error = None, str(error)
        else:
            continue
        if entries is None:
            unreadable.append((label, error))
        else:
            readable.append((label, marker, entries))
    return readable, unreadable, backup_paths


def main():
    if len(sys.argv) != 3:
        raise RuntimeError("Usage: export_account_bridge.py <account-bridge-base-path> <output-json-path>")
    requested_base, output_path = map(os.path.abspath, sys.argv[1:])
    root = Path(os.path.abspath(os.path.join(os.path.dirname(requested_base), os.pardir)))
    if os.path.basename(os.path.dirname(requested_base)).lower() != "user":
        root = Path(os.path.abspath(os.path.dirname(requested_base)))

    candidates = collect_live_candidates(root, requested_base)
    live_readable = []
    live_unreadable = []
    for prefix in candidates:
        entries, error = read_database(prefix)
        if entries is None:
            live_unreadable.append((prefix, error))
        else:
            live_readable.append((prefix, entries))

    with tempfile.TemporaryDirectory(prefix="altis-bridge-recovery-") as scratch:
        backup_readable, backup_unreadable, backup_paths = read_backup_databases(root, scratch)
        live_nonempty = [(path, entries) for path, entries in live_readable if entries]
        backup_nonempty = [(path, marker, entries) for path, marker, entries in backup_readable if entries]

        if live_nonempty:
            selected_path, entries = live_nonempty[0]
            selected_note = "read existing bridge at " + selected_path
        elif backup_nonempty:
            backup_nonempty.sort(
                key=lambda item: tuple(int(v) for v in re.findall(r"\d+", item[1]))[-1:] or (0,),
                reverse=True,
            )
            selected_path, marker, entries = backup_nonempty[0]
            selected_note = "recovered readable backup at " + selected_path
        elif live_unreadable or backup_unreadable or any("account-bridge" in os.path.basename(p).lower() for p in backup_paths):
            details = []
            details.extend("%s => %s" % item for item in live_unreadable)
            details.extend("%s => %s" % item for item in backup_unreadable)
            if not details:
                details.append("account-bridge-related files were found, but no complete readable database pair was available")
            raise RuntimeError(
                "No complete readable account-bridge database was found. The exporter searched the configured path, "
                "source root, user folder, and .pre-docker-recovery backups. No files were modified. "
                "Candidate errors: %s" % " | ".join(details)
            )
        elif live_readable:
            selected_path, entries = live_readable[0]
            selected_note = "read empty bridge at " + selected_path
        else:
            entries = {}
            selected_note = "no account-bridge files found; new local installation"

        payload = {
            "format": "altis-account-bridge-v1",
            "source_exists": bool(live_readable or live_unreadable or backup_readable or backup_unreadable or backup_paths),
            "entries": [
                [base64.b64encode(key).decode("ascii"), base64.b64encode(value).decode("ascii")]
                for key, value in sorted(entries.items())
            ],
            "source_note": selected_note,
        }
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".account-bridge-export-", suffix=".tmp", dir=str(output_path_obj.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
                json.dump(payload, stream, separators=(",", ":"))
                stream.write("\n")
            os.replace(temporary, output_path)
        finally:
            if os.path.exists(temporary):
                os.remove(temporary)

        print("Account bridge export created: %s" % output_path)
        print("Mapping count: %d (%s)." % (len(entries), selected_note))
        if live_unreadable or backup_unreadable:
            print("Unreadable stale candidates were left untouched.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("ERROR: %s" % error, file=sys.stderr)
        raise SystemExit(1)
