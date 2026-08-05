from toontown.notifications.gui.ClashGuiUtils import kwargsToOptionDefs
from toontown.notifications.gui.windows.NotifWindowBase import NotifWindowBase


class NotifWindowGenericText(NotifWindowBase):
    def __init__(self, parent, data, **kw):
        optiondefs = kwargsToOptionDefs()
        self.defineoptions(kw, optiondefs)
        NotifWindowBase.__init__(self, parent, data, **kw)
        self.initialiseoptions(NotifWindowGenericText)
        self.title_text.setText(data.getTitle())
        self.text.setTextWithVerticalAlignment(data.getSubtitle())
