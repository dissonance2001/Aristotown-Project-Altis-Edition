from __future__ import absolute_import
from lib2to3.fixer_base import BaseFix

class FixExplicit(BaseFix):
    explicit = True

    def match(self): return False
