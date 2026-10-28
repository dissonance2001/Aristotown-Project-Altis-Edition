from toontown.notifications.gui.ClashGuiUtils import kwargsToOptionDefs
from toontown.notifications.gui.windows.NotifWindowBase import NotifWindowBase


class NotifWindowGenericText(NotifWindowBase):
    def __init__(self, parent, data, **kw):
        optiondefs = kwargsToOptionDefs()
        self.defineoptions(kw, optiondefs)
        NotifWindowBase.__init__(self, parent, data, **kw)
        self.initialiseoptions(NotifWindowGenericText)
        self.title_text.setText(data.getTitle())
        if data.getNotificationType() == 'catalog':
            self.title_text.setZ(self.title_text.getZ() + 0.05)
        self.text.setTextWithVerticalAlignment(data.getSubtitle())
        if data.getNotificationType() == 'catalog':
            self.text.setZ(self.text.getZ() + 0.02)
