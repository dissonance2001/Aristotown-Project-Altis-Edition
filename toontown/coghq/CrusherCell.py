from __future__ import absolute_import
from toontown.coghq import ActiveCell
from direct.directnotify import DirectNotifyGlobal

class CrusherCell(ActiveCell.ActiveCell):
    notify = DirectNotifyGlobal.directNotify.newCategory('CrusherCell')

    def __init__(self, cr):
        ActiveCell.ActiveCell.__init__(self, cr)