from direct.gui.DirectGui import DirectFrame, DirectButton
from direct.gui import DirectGuiGlobals as DGG
from toontown.toon.socialpanel.SocialPanelGlobals import *
from toontown.toon.socialpanel.SocialPanelTabs import SocialPanelTabs
from toontown.toon.socialpanel.friends.SocialPanelFriendsTab import SocialPanelFriendsTab
from toontown.toon.socialpanel.clubs.SocialPanelClubsTab import SocialPanelClubsTab


class SocialPanel(DirectFrame):
    image_ratio = 566.0 / 1092.0
    shadow_image_ratio = 568.0 / 1024.0
    scale_mult = 1.08
    shadow_xscale = 1.06
    shadow_zscale = 1.075

    def __init__(self):
        DirectFrame.__init__(
            self,
            parent=base.a2dTopRight,
            relief=None,
            image=sp_gui.find('**/SocialPanel_Base'),
            image_pos=(-0.50 * self.image_ratio, 0, -0.50),
            image_scale=(self.image_ratio, 1, 1),
            scale=self.scale_mult,
            state=DGG.NORMAL,
        )
        self.initialiseoptions(SocialPanel)
        self.setPos(0, 0, 0)
        self.setBin('gui-popup', 100)

        self.currentTab = None
        self.tabs = None
        self.shadow = None
        self.close = None
        self.secrets = None
        self.isEntered = 0
        self.open = False

        self.load()
        self.hide()

    def load(self):
        self.shadow = DirectFrame(
            parent=self,
            relief=None,
            image=sp_gui.find('**/SocialPanel_Shadow'),
            image_pos=(-0.50 * self.image_ratio, 0, -0.50),
            image_scale=(self.shadow_image_ratio * self.shadow_xscale,
                         1, self.shadow_zscale),
        )
        self.shadow.setBin('gui-popup', 99)

        self.tabs = SocialPanelTabs(self)
        self.close = self.tabs.button_closePanel

        self.secrets = DirectButton(parent=self, relief=None)
        self.secrets.hide()

        self.showFriendsTab()

    def showFriendsTab(self):
        if self.currentTab is not None:
            self.currentTab.destroy()
        self.currentTab = SocialPanelFriendsTab(self)
        self.currentTab.setPos(-0.26, 0, -0.5)

    def showClubsTab(self):
        if self.currentTab is not None:
            self.currentTab.destroy()
        self.currentTab = SocialPanelClubsTab(self)
        self.currentTab.setPos(-0.26, 0, -0.5)

    def unavailableTab(self, tabId):
        return

    def enter(self):
        if self.isEntered:
            return
        self.isEntered = 1
        self.open = True
        try:
            base.localAvatar.obscureFriendsListButton(1)
        except:
            pass
        try:
            from toontown.toon import ToonAvatarPanel
            if ToonAvatarPanel.ToonAvatarPanel.currentAvatarPanel:
                ToonAvatarPanel.ToonAvatarPanel.currentAvatarPanel.cleanup()
                ToonAvatarPanel.ToonAvatarPanel.currentAvatarPanel = None
        except:
            pass
        if self.currentTab is None:
            self.showFriendsTab()
        else:
            self.currentTab.reload()
        self.show()
        messenger.send('social-panel-opened')

    def exit(self):
        if not self.isEntered:
            return
        self.isEntered = 0
        self.open = False
        self.hide()
        try:
            base.localAvatar.obscureFriendsListButton(-1)
        except:
            pass
        messenger.send('social-panel-closed')
        messenger.send('friends-list-done')

    def start(self, tab=None):
        self.enter()

    def stop(self, instant=False):
        self.exit()

    def unload(self):
        self.exit()
        self.destroy()

    def destroy(self):
        self.ignoreAll()
        if self.currentTab is not None:
            self.currentTab.destroy()
            self.currentTab = None
        self.tabs = None
        self.shadow = None
        self.close = None
        self.secrets = None
        DirectFrame.destroy(self)
