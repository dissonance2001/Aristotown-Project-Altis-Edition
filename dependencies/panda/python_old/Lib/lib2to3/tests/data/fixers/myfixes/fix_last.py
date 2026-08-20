from __future__ import absolute_import
from lib2to3.fixer_base import BaseFix

class FixLast(BaseFix):

    run_order = 10

    def match(self, node): return False
