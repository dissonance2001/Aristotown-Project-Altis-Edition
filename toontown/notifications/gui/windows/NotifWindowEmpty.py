from __future__ import absolute_import
from toontown.notifications.gui.ClashGuiUtils import kwargsToOptionDefs
from toontown.notifications.gui.windows.NotifWindowBase import NotifWindowBase


class NotifWindowEmpty(NotifWindowBase):
    def __init__(self, parent, data=None, **kw):
        optiondefs = kwargsToOptionDefs()
        self.defineoptions(kw, optiondefs)
        NotifWindowBase.__init__(self, parent, **kw)
        self.initialiseoptions(NotifWindowEmpty)
        self.middle_text.setTextWithVerticalAlignment(
            'You have no notifications.')
