"""Fix incompatible imports and module references that must be fixed after
fix_imports."""
from __future__ import absolute_import
from . import fix_imports


MAPPING = {
            'whichdb': 'dbm',
            'anydbm': 'dbm',
          }


class FixImports2(fix_imports.FixImports):

    run_order = 7

    mapping = MAPPING
