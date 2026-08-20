from __future__ import absolute_import
from lib2to3.fixer_base import BaseFix

class FixFirst(BaseFix):
    run_order = 1

    def match(self, node): return False
