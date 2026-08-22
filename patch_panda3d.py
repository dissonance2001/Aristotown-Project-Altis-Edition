"""
patch_panda3d.py

One-time setup script for Project Altis.

Panda3D's installed `direct.distributed.AstronInternalRepository` module has
a Python-2-era bug: `sendActivate()` calls `fieldPacker.getString()` on raw
packed binary field data, which forces a UTF-8 decode that randomly fails
depending on field values (UnicodeDecodeError). The fix is to use
`fieldPacker.getBytes()` instead, which returns the raw bytes untouched.

Run this once, after `pip install`-ing your requirements:

    python patch_panda3d.py

It's safe to run more than once — it checks whether the patch is already
applied before touching anything.
"""

import sys

try:
    import direct
except ImportError:
    print("ERROR: Could not import 'direct' (panda3d). "
          "Install your requirements first, e.g.:\n"
          "    pip install -r requirements.txt")
    sys.exit(1)

import os

target_path = os.path.join(
    os.path.dirname(direct.__file__),
    "distributed",
    "AstronInternalRepository.py",
)

OLD = "dg.appendData(fieldPacker.getString())"
NEW = "dg.appendData(fieldPacker.getBytes())"

if not os.path.isfile(target_path):
    print(f"ERROR: Could not find AstronInternalRepository.py at:\n  {target_path}")
    print("Your panda3d install may be structured differently than expected. "
          "Please report this so the script can be updated.")
    sys.exit(1)

with open(target_path, "r", encoding="utf-8") as f:
    content = f.read()

if NEW in content:
    print("Already patched — nothing to do.")
    sys.exit(0)

if OLD not in content:
    print("WARNING: Expected code not found — your panda3d version may differ "
          "from the one this patch targets. No changes made.")
    print(f"  File checked: {target_path}")
    sys.exit(1)

backup_path = target_path + ".bak"
if not os.path.isfile(backup_path):
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Backed up original to:\n  {backup_path}")

patched = content.replace(OLD, NEW)
with open(target_path, "w", encoding="utf-8") as f:
    f.write(patched)

print(f"Patched successfully:\n  {target_path}")
print("You're ready to play.")
