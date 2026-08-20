#!/usr/bin/env python

# Make a reST file compliant to our pre-commit hook.
# Currently just remove trailing whitespace.

from __future__ import absolute_import
import sys

import patchcheck

def main(argv=sys.argv):
    patchcheck.normalize_docs_whitespace(argv[1:])

if __name__ == '__main__':
    sys.exit(main())
