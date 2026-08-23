"""
find_bad_imports.py

Scans a Toontown-style Python source tree for old Python-2-only
"implicit relative imports" -- statements like:

    import SuitDNA
    import GardenGlobals, time

that only worked in Python 2 because Python 2 checked the local
package folder before falling back to the top-level search path.
Python 3 requires these to be either:

    from toontown.suit import SuitDNA
    from . import SuitDNA

This script does NOT touch your files. It only reports suspects,
by cross-referencing every bare "import X" against the actual
.py filenames that exist anywhere in the repo. A bare import is
flagged ONLY if a matching filename exists somewhere in the tree
-- e.g. "import random" is left alone (no random.py in your repo),
but "import SuitDNA" is flagged if SuitDNA.py exists anywhere.

Usage (from the repo root):
    dependencies\\panda\\python\\python.exe find_bad_imports.py
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# 1. Build a set of every module name (filename without .py) that
#    exists anywhere in the repo, skipping vendored/dependency code.
SKIP_DIRS = {'dependencies', '.git', '__pycache__', 'py3_originals'}

local_module_names = set()
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        if fn.endswith('.py'):
            local_module_names.add(fn[:-3])

# 2. Regex for simple "import X" / "import X, Y, Z" statements.
#    Deliberately does NOT match "from X import Y" or "import X.Y" --
#    dotted imports are already absolute and are not the bug we're
#    looking for.
import_re = re.compile(r'^\s*import\s+([A-Za-z_][A-Za-z0-9_]*(?:\s*,\s*[A-Za-z_][A-Za-z0-9_]*)*)\s*$')

suspects = []  # (filepath, lineno, line, flagged_names)

for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        if not fn.endswith('.py'):
            continue
        fpath = os.path.join(dirpath, fn)
        try:
            with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
        except Exception as e:
            print("Could not read %s: %s" % (fpath, e))
            continue

        for lineno, line in enumerate(lines, start=1):
            m = import_re.match(line)
            if not m:
                continue
            names = [n.strip() for n in m.group(1).split(',')]
            flagged = [n for n in names if n in local_module_names and n != fn[:-3]]
            if flagged:
                suspects.append((fpath, lineno, line.rstrip(), flagged))

# 3. Report
if not suspects:
    print("No suspicious implicit relative imports found.")
else:
    print("Found %d suspicious import(s):\n" % len(suspects))
    for fpath, lineno, line, flagged in suspects:
        rel = os.path.relpath(fpath, ROOT)
        print("%s:%d" % (rel, lineno))
        print("    %s" % line)
        print("    -> looks like local module(s): %s" % ", ".join(flagged))
        print()

print("Scanned %d local module names across the repo." % len(local_module_names))
