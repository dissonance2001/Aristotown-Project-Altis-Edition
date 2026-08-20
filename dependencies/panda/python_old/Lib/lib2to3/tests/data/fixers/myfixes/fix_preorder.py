from __future__ import absolute_import
from lib2to3.fixer_base import BaseFix

class FixPreorder(BaseFix):
    order = "pre"

    def match(self, node): return False
