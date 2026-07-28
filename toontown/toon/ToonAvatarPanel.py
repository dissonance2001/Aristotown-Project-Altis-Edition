from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.gui import DirectGuiGlobals as DGG
from direct.directnotify import DirectNotifyGlobal

from toontown.toon import AvatarPanelBase
from toontown.toon import DistributedToon
from toontown.toon import Toon
from toontown.toon import ToonAvatarPanelGlobals as TAPG
from toontown.toon import ToonProfileGlobals as TPG
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.toonbase.ToontownBattleGlobals import Tracks, Levels
from toontown.hood import ZoneUtil
from toontown.suit import SuitDNA
from toontown.suit import Suit
from toontown.battle import SuitBattleGlobals
from toontown.coghq import CogDisguiseGlobals
from toontown.quest import QuestBookPoster


IGNORE_SCALE = 0.06
STOP_IGNORE_SCALE = 0.04


NAMEPLATE_ID_TO_NODE = {
    0: 'default_med_blue',
    1: 'default_green',
    2: 'default_purple',
    3: 'default_red',
    4: 'default_yellow',
    5: 'default_orange',
    6: 'default_blue',
    7: 'default_dark_blue',
    8: 'default_dark_green',
    9: 'hidden_stars',
    10: 'hidden_pg_dg',
    11: 'hidden_pg_ddl',
    12: 'hidden_underwater',
    13: 'event_tinsel',
    14: 'event_candy',
    15: 'event_wrapping',
    16: 'event_nightlights',
    17: 'event_2019_fireworks',
    18: 'event_skyclan',
    19: 'hidden_banana',
    20: 'hidden_pg_ttc',
    21: 'event_outback',
    22: 'hidden_golfing',
    23: 'hidden_trolley',
    24: 'hidden_racing',
    25: 'hidden_pg_bb',
    26: 'hidden_pg_yott',
    27: 'hidden_pg_mml',
    28: 'hidden_pg_tb',
    29: 'hidden_pg_aa',
    30: 'event_lazy',
    31: 'event_2019_thanksgiving',
    32: 'event_2020_newyears',
    33: 'event_btl',
    34: 'event_easter2020',
    35: 'event_standin',
    36: 'firework_nameplate',
    37: 'hidden_maxevidence',
    38: 'event_halloween_candy_blue',
    39: 'event_halloween_candy_green',
    40: 'event_halloween_candy_magenta',
    41: 'event_halloween_candy_purple',
    42: 'event_halloween_candy_red',
    43: 'event_halloween_bat',
    44: 'sidetask_judy',
    45: 'hidden_steve',
    46: 'hidden_ocftf',
    47: 'kudos_ttc',
    48: 'kudos_bb',
    49: 'kudos_yott',
    50: 'kudos_dg',
    51: 'kudos_mml',
    52: 'kudos_tb',
    53: 'kudos_aa',
    54: 'kudos_ddl',
    55: 'event_electric',
    56: 'event_halloween_witch',
    101: 'default_med_blue',
    102: 'default_green',
    103: 'default_purple',
    104: 'default_red',
    105: 'default_yellow',
    106: 'default_orange',
    107: 'default_blue',
    108: 'default_dark_blue',
    109: 'default_dark_green',
    200: 'hidden_pg_ttc',
    201: 'hidden_pg_bb',
    202: 'hidden_pg_yott',
    203: 'hidden_pg_dg',
    204: 'hidden_pg_mml',
    205: 'hidden_pg_tb',
    206: 'hidden_pg_aa',
    207: 'hidden_pg_ddl',
    300: 'hidden_golfing',
    301: 'hidden_trolley',
    302: 'hidden_racing',
    400: 'sidetask_judy',
    500: 'hidden_stars',
    501: 'hidden_underwater',
    502: 'hidden_banana',
    503: 'hidden_maxevidence',
    504: 'hidden_steve',
    505: 'hidden_ocftf',
    600: 'event_tinsel',
    601: 'event_candy',
    602: 'event_wrapping',
    603: 'event_nightlights',
    604: 'event_2019_fireworks',
    605: 'event_skyclan',
    606: 'event_outback',
    607: 'event_lazy',
    608: 'event_2019_thanksgiving',
    609: 'event_2020_newyears',
    610: 'event_btl',
    611: 'event_easter2020',
    612: 'event_standin',
    613: 'firework_nameplate',
    614: 'event_electric',
    615: 'event_highroller',
    700: 'event_halloween_candy_blue',
    701: 'event_halloween_candy_green',
    702: 'event_halloween_candy_magenta',
    703: 'event_halloween_candy_purple',
    704: 'event_halloween_candy_red',
    705: 'event_halloween_bat',
    800: 'kudos_ttc',
    801: 'kudos_bb',
    802: 'kudos_yott',
    803: 'kudos_dg',
    804: 'kudos_mml',
    805: 'kudos_tb',
    806: 'kudos_aa',
    807: 'kudos_ddl',
}


NAMEPLATE_NAME_TO_NODE = {
    'candy': 'event_candy',
    'dreams come true': 'event_skyclan',
    'dreamscometrue': 'event_skyclan',
    'skyclan': 'event_skyclan',
    'default': 'default_med_blue',
    'default blue': 'default_med_blue',
    'blue': 'default_med_blue',
    'green': 'default_green',
    'purple': 'default_purple',
    'red': 'default_red',
    'yellow': 'default_yellow',
    'orange': 'default_orange',
}


class ToonAvatarPanel(AvatarPanelBase.AvatarPanelBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('ToonAvatarPanel')

    ToonClipPlaneValues = {
        0: ((1, 0, 0), (-0.2425, 0, 0)),
        1: ((-1, 0, 0), (0.2425, 0, 0)),
        2: ((0, 0, 1), (0, 0, -0.135)),
        3: ((0, 0, -1), (0, 0, 0.135)),
    }

    def __init__(self, avatar, playerId=None, openStats=False, requestFriend=False):
        from toontown.friends import FriendsListPanel

        actualAvatar = None
        try:
            actualAvatar = base.cr.doId2do.get(avatar.getDoId())
        except:
            actualAvatar = None
        if actualAvatar:
            avatar = actualAvatar

        AvatarPanelBase.AvatarPanelBase.__init__(self, avatar, FriendsListPanel=FriendsListPanel)

        self.playerId = playerId
        self.openStats = openStats
        self.requestFriend = requestFriend
        self.sourceAvatar = avatar
        self.lookupAvatar = None
        self.createdAvatar = False
        self.waitingForDetails = False
        self.isLoaded = False
        self.detailOpened = False
        self.dCurrentPage = -1
        self.gui = None
        self.detailsGui = None
        self.profileBackgroundModel = None
        self.profileNameplateModel = None
        self.toon = None
        self.toonPoseRoot = None
        self.toonClippingPlanes = []
        self.dInfoFrame = None
        self.dGagsFrame = None
        self.dSuitsFrame = None
        self.dQuestsFrame = None
        self.dClubFrame = None
        self.dSuits = []
        self.questFrames = []
        self.managedGuiElement = None
        self.dialog = None
        self.avDisableName = avatar.uniqueName('disable') if hasattr(avatar, 'uniqueName') else None

        if not hasattr(avatar, 'style') and not hasattr(avatar, 'getStyle'):
            self.notify.warning("Avatar has no style; cannot open ToonAvatarPanel.")
            self.cleanup()
            return

        base.localAvatar.obscureFriendsListButton(1)
        self.accept('AvatarIgnoreChange', self.refreshIgnoreButton)

        if actualAvatar or avatar == base.localAvatar or hasattr(avatar, 'inventory'):
            self.avatar = avatar
            self.openAvatarPanel()
        else:
            self.waitingForDetails = True
            self.lookupAvatar = DistributedToon.DistributedToon(base.cr)
            self.lookupAvatar.doId = self.avId
            self.lookupAvatar.forceAllowDelayDelete()
            self.createdAvatar = True
            base.cr.getAvatarDetails(self.lookupAvatar, self.__handleAvatarDetails, 'DistributedToon')

    def __handleAvatarDetails(self, gotData, avatar, dclass):
        if not self.waitingForDetails:
            return
        self.waitingForDetails = False
        if gotData:
            self.avatar = avatar
        else:
            self.avatar = self.sourceAvatar
        self.openAvatarPanel()

    def openAvatarPanel(self):
        if self.isLoaded:
            return

        cbm = CullBinManager.getGlobalPtr()
        if cbm.findBin('sorted-gui-popup') < 0:
            cbm.addBin('sorted-gui-popup', CullBinManager.BTFixed, 70)

        self.gui = loader.loadModel('phase_3.5/models/gui/friendsPanel')
        self.detailsGui = loader.loadModel('phase_3.5/models/gui/avatarPanelDetails')
        self.profileBackgroundModel = loader.loadModel('phase_3.5/models/gui/profile/background')
        self.profileNameplateModel = loader.loadModel('phase_3.5/models/gui/profile/nameplates')

        self.managedGuiElement = DirectFrame(parent=base.a2dTopRight, relief=None)

        background = self.getAvatarBackground()
        self.tapBackground = DirectFrame(
            parent=self.managedGuiElement,
            image=background,
            relief=None,
            pos=(-0.28, 0, -0.178),
            image_scale=0.485,
            sortOrder=50)
        self.tapBackground.setBin('sorted-gui-popup', 800)

        self.toon = self.generateToon()
        if self.toon:
            poseId = getattr(self.toon, '_toonProfilePoseId', None)
            neutralBounds = getattr(self.toon, '_toonProfileNeutralBounds', None)
            if poseId == 42:
                # Restore Fire Hands to the original Toon Panel behaviour.
                # Its complete posed composition (including both fire props)
                # determines the fit, and none of the Neutral-centering logic
                # is applied.  The Shticker Book preview is unaffected.
                self.fitGeometry(self.toon, 1, includePoseProps=True)
                self.toon.reparentTo(self.tapBackground)
                profileOffset = getattr(
                    self.toon, '_toonProfilePanelOffset', (0, 0, 0))
                self.toon.setPos(profileOffset[0] * 0.045, 0,
                                 -0.05 + profileOffset[2] * 0.045)
            elif getattr(self.toon, '_toonProfileUsesPosedFit', False):
                # Use the same complete posed-composition centring as the left
                # Shticker Book page.  AvatarPanelPos offsets are deliberately
                # ignored so these poses share Neutral's exact visual anchor.
                self.toonPoseRoot = self.fitSelectedPoseOnPanel(
                    self.toon, self.tapBackground, neutralBounds, 0.4,
                    (0, 0, -0.05))
                if (getattr(self.toon, '_toonProfilePoseId', None) == 44 and
                        self.toonPoseRoot):
                    # Naptime is correctly placed in the Shticker Book, but
                    # the smaller Toon Panel needs the whole Toon-and-ZZZ
                    # composition noticeably higher.
                    self.toonPoseRoot.setZ(
                        self.toonPoseRoot.getZ() + 0.10)
                if (getattr(self.toon, '_toonProfilePoseId', None) == 40 and
                        self.toonPoseRoot):
                    # Elegance is centred correctly in the Shticker Book, but
                    # needs a small panel-only adjustment to the right and down.
                    self.toonPoseRoot.setX(
                        self.toonPoseRoot.getX() + 0.055)
                    self.toonPoseRoot.setZ(
                        self.toonPoseRoot.getZ() - 0.025)
            else:
                # Keep Fire Hands and every already-correct pose on the
                # Neutral-reference path.
                self.fitGeometry(self.toon, 1, referenceBounds=neutralBounds)
                self.toon.reparentTo(self.tapBackground)
                self.centerPoseOnNeutral(self.toon, self.tapBackground,
                                         (0, 0, -0.05))
                # Sinking's melt animation still appears far below Neutral's
                # visual anchor.  Raise the complete pose substantially in
                # the Toon Panel without affecting any other pose.
                if getattr(self.toon, '_toonProfilePoseId', None) == 27:
                    self.toon.setZ(self.toon.getZ() + 0.15)
                # Rolled uses the Neutral-reference path.  Raise the complete
                # Toon-and-log composition to the same panel height as
                # Naptime, without changing the Shticker Book preview.
                if getattr(self.toon, '_toonProfilePoseId', None) == 43:
                    self.toon.setZ(self.toon.getZ() + 0.10)
            for i in range(4):
                clipData = self.ToonClipPlaneValues[i]
                planeNode = PlaneNode('toon-clippingPlane')
                planeNode.setPlane(Plane(Vec3(*clipData[0]), Point3(*clipData[1])))
                clipNP = self.tapBackground.attachNewNode(planeNode)
                self.toon.setClipPlane(clipNP)
                self.toonClippingPlanes.append(clipNP)

        self.dMainFrame = DirectFrame(
            parent=self.tapBackground,
            image=self.detailsGui.find('**/details_panel'),
            relief=None,
            scale=(-1.3, 1.3, 1.3),
            pos=(-0.8, 0, -0.275),
            sortOrder=40)
        self.dMainFrame.setBin('sorted-gui-popup', 790)
        self.dMainFrame.hide()

        shadowModel = loader.loadModel('phase_3.5/models/gui/socialpanel/ttcc_avatar_panel_shadows')
        self.dMainShadow = DirectFrame(
            parent=self.dMainFrame,
            image=shadowModel.find('**/panel_detail_shadow'),
            relief=None,
            image_pos=(0.02417, 0, -0.01115),
            image_scale=(1.06854, 1.0, 0.77213),
            sortOrder=20)
        self.dMainShadow.setBin('sorted-gui-popup', 789)
        self.dMainShadow.setTransparency(TransparencyAttrib.MDual)

        self.tapMainFrame = DirectFrame(
            parent=self.tapBackground,
            image=self.gui.find('**/friends_panel'),
            relief=None,
            pos=(0, 0, -0.326),
            sortOrder=45)
        self.tapMainFrame.setBin('sorted-gui-popup', 799)

        self.tapMainShadow = DirectFrame(
            parent=self.tapMainFrame,
            image=shadowModel.find('**/panel_shadow'),
            image_scale=(0.6435, 1.0, 1.10175),
            image_pos=(0, 0, -0.005),
            relief=None,
            sortOrder=-20)
        self.tapMainShadow.setBin('sorted-gui-popup', 797)
        shadowModel.removeNode()

        nameplate, nameplatePos, nameplateScale = self.getAvatarNameplate()
        self.tapNameplate = DirectFrame(
            parent=self.tapMainFrame,
            image=nameplate,
            relief=None,
            pos=nameplatePos,
            image_scale=(0.485 * nameplateScale[0], 0.485, 0.485 * nameplateScale[2]))
        self.tapNameplate.setBin('sorted-gui-popup', 801)
        self.generateNameText()

        ignoreStr, ignoreCmd, ignoreScale = self.getIgnoreButtonInfo()
        reportStr = getattr(TTLocalizer, 'AvatarPanelReport', 'Report')
        if base.localAvatar.doId == self.avId:
            reportStr = ''

        self.tapFriendButton = self.__makeWideButton(
            'friend', 0.004, getattr(TTLocalizer, 'AvatarPanelFriends', 'Friends'), self.onFriendButtonPressed)
        self.tapTeleportButton = self.__makeWideButton(
            'goto', -0.127, getattr(TTLocalizer, 'AvatarPanelGoTo', 'Go To'), self.onTeleportButtonPressed)
        self.tapWhisperButton = self.__makeWideButton(
            'talk', -0.258, getattr(TTLocalizer, 'AvatarPanelWhisper', 'Whisper'), self.onWhisperButtonPressed)

        self.tapCloseButton = self.__makeSmallButton(
            'close', (0.181, 0, -0.377), (-0.12, 0.12, 0.11),
            getattr(TTLocalizer, 'AvatarPanelCogDetailClose', 'Close'), self.onCloseButtonPressed)
        self.tapIgnoreButton = self.__makeSmallButton(
            'block', (-0.059, 0, -0.381), (0.12, 0.12, 0.115),
            ignoreStr, ignoreCmd, textMayChange=1)
        self.tapReportButton = self.__makeSmallButton(
            'report', (0.061, 0, -0.381), (0.12, 0.12, 0.115),
            reportStr, self.onReportButtonPressed)
        self.tapDetailsButton = self.__makeSmallButton(
            'right', (-0.1795, 0, -0.377), (-0.12, 0.12, 0.11),
            getattr(TTLocalizer, 'AvatarPanelDetail', 'Toon Details'), self.onDetailsButtonPressed)

        self.__setupDetailsPanel()
        self.__updateButtonStates()

        self.isLoaded = True
        self.frame = self.managedGuiElement
        messenger.send('avPanelDone')
        messenger.send('avPanelCreated', ['t'])

        if self.openStats:
            self.openStats = False
            self.onDetailsButtonPressed()
        if self.requestFriend:
            self.requestFriend = False
            self.onFriendButtonPressed()

    def __makeWideButton(self, node, z, text, command):
        return DirectButton(
            parent=self.tapMainFrame,
            image=(
                self.gui.find('**/%s_normal' % node),
                self.gui.find('**/%s_pressed' % node),
                self.gui.find('**/%s_hover' % node),
                self.gui.find('**/%s_normal' % node)),
            image3_color=TAPG.colors['disabledImageColor'],
            image_scale=(0.48, 0.48, 0.13),
            relief=None,
            text=text,
            text_scale=0.07,
            pos=(0, 0, z),
            text0_fg=TAPG.colors['text0Color'],
            text1_fg=TAPG.colors['text1Color'],
            text2_fg=TAPG.colors['text2Color'],
            text3_fg=TAPG.colors['text3Color'],
            text_pos=(-0.07, -0.0253),
            text_align=TextNode.ALeft,
            text_shadow=Vec4(0.611, 0.364, 0.09, 1),
            command=command)

    def __makeSmallButton(self, node, pos, imageScale, text, command, textMayChange=0):
        return DirectButton(
            parent=self.tapMainFrame,
            image=(
                self.gui.find('**/%s_normal' % node),
                self.gui.find('**/%s_pressed' % node),
                self.gui.find('**/%s_hover' % node),
                self.gui.find('**/%s_normal' % node)),
            relief=None,
            pos=pos,
            image_scale=imageScale,
            text=('', text, text),
            textMayChange=textMayChange,
            text0_fg=TAPG.colors['text0Color'],
            text1_fg=TAPG.colors['text1Color'],
            text2_fg=TAPG.colors['text2Color'],
            text3_fg=TAPG.colors['text3Color'],
            text_scale=0.06,
            text_pos=(0, -0.1),
            text_align=TextNode.ACenter,
            command=command)

    def __setupDetailsPanel(self):
        buttonScale = (-0.156, 0.15, 0.11)
        self.dTitle = DirectLabel(
            parent=self.dMainFrame,
            pos=(0.023, 0, 0.117),
            scale=(-1, 1, 1),
            relief=None,
            text='Info',
            text_fg=Vec4(1, 1, 1, 1),
            text_scale=0.048,
            text_wordwrap=7.5,
            text_align=TextNode.ACenter)

        self.dInfoButton = self.__makeDetailButton('info', (0.374, 0, 0.242), 0, buttonScale)
        self.dGagsButton = self.__makeDetailButton('gags', (0.205, 0, 0.242), 1, buttonScale)
        self.dSuitsButton = self.__makeDetailButton('disguise', (0.033, 0, 0.242), 2, buttonScale)
        self.dQuestsButton = self.__makeDetailButton('quests', (-0.14, 0, 0.242), 3, buttonScale)
        self.dClubButton = self.__makeDetailButton('doodle', (-0.311, 0, 0.242), 4, buttonScale)
        self.dClubButton['state'] = DGG.DISABLED
        self.dClubButton['image3_color'] = TAPG.colors['noPetImageColor']

    def __makeDetailButton(self, node, pos, page, buttonScale):
        return DirectButton(
            parent=self.dMainFrame,
            image=(
                self.detailsGui.find('**/%s_normal' % node),
                self.detailsGui.find('**/%s_pressed' % node),
                self.detailsGui.find('**/%s_normal' % node),
                self.detailsGui.find('**/%s_normal' % node)),
            image3_color=TAPG.colors['disabledImageColor'],
            image_scale=buttonScale,
            relief=None,
            text='',
            pos=pos,
            command=self.switchPage,
            extraArgs=[page])

    def __updateButtonStates(self):
        isSelf = base.localAvatar.doId == self.avId
        ignored = False
        try:
            ignored = base.cr.avatarFriendsManager.checkIgnored(self.avId)
        except:
            pass

        if isSelf:
            for button in (self.tapFriendButton, self.tapTeleportButton, self.tapWhisperButton,
                           self.tapIgnoreButton, self.tapReportButton):
                button['state'] = DGG.DISABLED
            self.tapIgnoreButton['text'] = ''
            self.tapReportButton['text'] = ''
            self.tapIgnoreButton['image_color'] = Vec4(0.75, 0.75, 0.75, 1)
            self.tapReportButton['image_color'] = Vec4(0.75, 0.75, 0.75, 1)
        elif ignored:
            self.tapFriendButton['state'] = DGG.DISABLED
            self.tapTeleportButton['state'] = DGG.DISABLED
            self.tapWhisperButton['state'] = DGG.DISABLED

        if not base.localAvatar.isTeleportAllowed():
            self.tapTeleportButton['state'] = DGG.DISABLED

    def onCloseButtonPressed(self):
        self.cleanup()
        AvatarPanelBase.currentAvatarPanel = None
        if getattr(self, 'friendsListShown', False):
            self.FriendsListPanel.showFriendsList()

    def onReportButtonPressed(self):
        self.handleReport()

    def onFriendButtonPressed(self):
        base.localAvatar.chatMgr.noWhisper()
        messenger.send('friendAvatar', [self.avId, self.avName, self.avDisableName])

    def onTeleportButtonPressed(self):
        if base.localAvatar.isTeleportAllowed():
            base.localAvatar.chatMgr.noWhisper()
            messenger.send('gotoAvatar', [self.avId, self.avName, self.avDisableName])

    def onWhisperButtonPressed(self):
        base.localAvatar.chatMgr.whisperTo(self.avName, self.avId, None)

    def onDetailsButtonPressed(self):
        if self.dMainFrame.isHidden():
            self.openDetails()
            self.tapDetailsButton['image'] = (
                self.gui.find('**/left_normal'),
                self.gui.find('**/left_pressed'),
                self.gui.find('**/left_hover'),
                self.gui.find('**/left_normal'))
        else:
            self.closeDetails()
            self.tapDetailsButton['image'] = (
                self.gui.find('**/right_normal'),
                self.gui.find('**/right_pressed'),
                self.gui.find('**/right_hover'),
                self.gui.find('**/right_normal'))

    def openDetails(self):
        self.switchPage(0)
        self.dMainFrame.show()
        self.detailOpened = True
        if hasattr(self.avatar, 'uniqueName'):
            self.accept(self.avatar.uniqueName('hpChange'), self.updateInfoText)

    def closeDetails(self):
        self.dMainFrame.hide()
        self.detailOpened = False
        if hasattr(self.avatar, 'uniqueName'):
            self.ignore(self.avatar.uniqueName('hpChange'))

    def switchPage(self, page):
        if page == 4:
            return
        if self.dCurrentPage >= 0:
            self.__hidePage(self.dCurrentPage)
        if page == 0:
            self.dShowInfo()
        elif page == 1:
            self.dShowGags()
        elif page == 2:
            self.dShowSuits()
        elif page == 3:
            self.dShowQuests()
        self.dCurrentPage = page

    def __hidePage(self, page):
        frames = (self.dInfoFrame, self.dGagsFrame, self.dSuitsFrame, self.dQuestsFrame)
        buttons = (self.dInfoButton, self.dGagsButton, self.dSuitsButton, self.dQuestsButton)
        if page < len(frames) and frames[page]:
            frames[page].hide()
        if page < len(buttons):
            buttons[page]['state'] = DGG.NORMAL

    def dShowInfo(self):
        self.dInfoButton['state'] = DGG.DISABLED
        status = 'Online' if self.isAvatarOnline() else 'Offline'
        self.dTitle['text'] = 'Info - %s' % status
        if not self.dInfoFrame:
            self.dInfoFrame = DirectFrame(parent=self.dMainFrame, scale=(-1, 1, 1), relief=None)
            self.detailsInfoText = DirectLabel(
                parent=self.dInfoFrame,
                pos=(-0.44, 0, 0.035),
                relief=None,
                text=self.generateInfoText(),
                text_fg=Vec4(1, 1, 1, 1),
                text_scale=0.05,
                text_wordwrap=20,
                text_align=TextNode.ALeft)
        else:
            self.detailsInfoText['text'] = self.generateInfoText()
            self.dInfoFrame.show()

    def dShowGags(self):
        self.dGagsButton['state'] = DGG.DISABLED
        self.dTitle['text'] = ''
        if not self.dGagsFrame:
            self.dGagsFrame = DirectFrame(
                parent=self.dMainFrame,
                scale=(-1.125, 1.125, 1.125),
                relief=None)
            self.dGagsFrame.setPos(0.01, 0, 0.05)
            gagTracks = self.__generateGags()
            gagTracks.reparentTo(self.dGagsFrame)
            gagTracks.setPos(0, 0, -0.085)
            gagTracks.setScale(0.77)
        else:
            self.dGagsFrame.show()

    def __generateGags(self):
        """Build the Corporate Clash avatar-panel gag display."""
        tracksFrame = DirectFrame(relief=None)
        inventory = getattr(self.avatar, 'inventory', None)
        if not inventory or not hasattr(inventory, 'invModels'):
            DirectLabel(
                parent=tracksFrame,
                relief=None,
                text='Gag information unavailable.',
                text_fg=(1, 1, 1, 1),
                text_scale=0.05,
                pos=(0, 0, 0))
            return tracksFrame

        gagSelectGui = loader.loadModel(
            'phase_3.5/models/gui/battlegui/gag_selection_panels')
        inventoryModels = loader.loadModel(
            'phase_3.5/models/gui/inventory_gui')
        buttonModel = inventoryModels.find('**/InventoryButtonUp')
        prestigeStarFilled = gagSelectGui.find('**/prestige_star')
        prestigeStarEmpty = gagSelectGui.find('**/prestige_star_empty')

        gagButtonsXOffset = -0.22
        gagButtonsXSpacing = 0.084
        gagTracksZSeparation = 0.059
        gagTrackOrder = (0, 1, 2, 3, 4, 5, 6, 7)

        for index, trackIndex in enumerate(gagTrackOrder):
            if trackIndex >= len(Tracks):
                continue

            trackName = Tracks[trackIndex]
            rowZ = (7 - index * 2) * gagTracksZSeparation / 2.0

            DirectFrame(
                parent=tracksFrame,
                relief=None,
                image=gagSelectGui.find('**/track_' + trackName),
                scale=(1, 1, 0.0625),
                pos=(0, 0, rowZ))

            DirectFrame(
                parent=tracksFrame,
                relief=None,
                image=gagSelectGui.find('**/track_' + trackName + '_title'),
                scale=(0.25 if trackName == 'toon-up' else 0.125,
                       1, 0.0625),
                pos=(-0.388, 0, rowZ))

            DirectFrame(
                parent=tracksFrame,
                relief=None,
                image=prestigeStarEmpty,
                scale=0.04,
                pos=(0.44, 0, rowZ))

            prestigeStar = DirectFrame(
                parent=tracksFrame,
                relief=None,
                image=prestigeStarFilled,
                scale=0.0424,
                pos=(0.44, 0, rowZ))
            prestigeStar.hide()

            try:
                hasAccess = self.avatar.hasTrackAccess(trackIndex)
            except:
                hasAccess = False
            if not hasAccess:
                continue

            prestiged = False
            if hasattr(self.avatar, 'checkGagBonus'):
                try:
                    for gagLevel in range(len(Levels[trackIndex])):
                        if self.avatar.checkGagBonus(trackIndex, gagLevel):
                            prestiged = True
                            break
                except:
                    prestiged = False
            if prestiged:
                prestigeStar.show()

            try:
                curExp, nextExp = inventory.getCurAndNextExpValues(trackIndex)
            except:
                curExp = 0

            for item in range(len(Levels[trackIndex])):
                if curExp < Levels[trackIndex][item]:
                    break
                try:
                    numItems = inventory.numItem(trackIndex, item)
                    gagGeom = inventory.invModels[trackIndex][item]
                except:
                    continue

                try:
                    organic = self.avatar.checkGagBonus(trackIndex, item)
                except:
                    organic = False

                if numItems:
                    if organic:
                        imageColor = getattr(
                            inventory, 'PressableOrganicColor',
                            getattr(inventory, 'PressableImageColor',
                                    Vec4(0, 0.6, 1, 1)))
                    else:
                        imageColor = getattr(
                            inventory, 'PressableImageColor',
                            Vec4(0, 0.6, 1, 1))
                else:
                    imageColor = getattr(
                        inventory, 'UnpressableImageColor',
                        Vec4(0.3, 0.3, 0.3, 0.8))

                DirectLabel(
                    parent=tracksFrame,
                    image=buttonModel,
                    image_color=imageColor,
                    geom=gagGeom,
                    geom_color=getattr(
                        inventory, 'BookUnpressableGeomColor',
                        Vec4(1, 1, 1, 1)),
                    text=str(numItems),
                    text_align=TextNode.ARight,
                    geom_scale=0.7,
                    geom_pos=(-0.01, -0.1, 0),
                    text_font=ToontownGlobals.getBuildingNametagFont(),
                    text_scale=0.075 if prestiged else 0.07,
                    text_pos=(0.075, -0.05),
                    text_fg=Vec4(1, 1, 1, 1),
                    textMayChange=1,
                    relief=None,
                    pos=(gagButtonsXOffset + item * gagButtonsXSpacing,
                         0, 0.0005 + rowZ),
                    scale=0.48)

        gagSelectGui.removeNode()
        inventoryModels.removeNode()
        return tracksFrame

    def dShowSuits(self):
        self.dSuitsButton['state'] = DGG.DISABLED
        self.dTitle['text'] = ''
        if not self.dSuitsFrame:
            self.dSuitsFrame = DirectFrame(parent=self.dMainFrame, scale=(-1, 1, 1), relief=None)
            # Display the five Altis disguise departments in Clash order:
            # Sellbot, Cashbot, Lawbot, Bossbot, Boardbot.
            for dept in ('s', 'm', 'l', 'c', 'g'):
                suit = self.__generateSuit(dept, TAPG.disguiseSuitPos[dept])
                if suit:
                    self.dSuits.append(suit)
        else:
            self.dSuitsFrame.show()

    def __generateSuit(self, suitKind, pos):
        try:
            deptIndex = ToontownGlobals.cogDept2index[suitKind]
            cogTypes = (self.avatar.getCogTypes()
                        if hasattr(self.avatar, 'getCogTypes')
                        else self.avatar.cogTypes)
            cogType = cogTypes[deptIndex]

            # Altis adds many custom Cogs, so its departments no longer occupy
            # fixed-size blocks inside suitHeadTypes. Resolve the disguise from
            # the department's own regular-Cog list instead. This displays the
            # exact Sellbot/Cashbot/Lawbot/Bossbot/Boardbot suit the Toon is wearing.
            departmentSuits = SuitDNA.suitDeptCogs[suitKind]
            if cogType < 0:
                cogType = 0
            elif cogType >= len(departmentSuits):
                cogType = len(departmentSuits) - 1
            cogIdentifier = departmentSuits[cogType]
        except:
            DirectLabel(parent=self.dSuitsFrame, relief=None, text='No data',
                        text_scale=0.025, text_fg=(1, 1, 1, 1), pos=pos)
            return None

        try:
            suit = Suit.Suit()
            dna = SuitDNA.SuitDNA()
            dna.newSuit(cogIdentifier)
            suit.setDNA(dna)
            suit.reparentTo(self.dSuitsFrame)
            suit.setScale(0.03)
            suit.setHpr(180, 0, 0)
            suit.setPos(pos)
            suit.getGeomNode().setDepthWrite(1)
            suit.getGeomNode().setDepthTest(1)
            suit.getGeomNode().setTwoSided(True)
            suit.hideNametag3d()
            suit.loop('neutral')
        except:
            return None

        try:
            suitName = SuitBattleGlobals.SuitAttributes[cogIdentifier]['name']
        except:
            suitName = cogIdentifier

        try:
            level = self.avatar.cogLevels[deptIndex]
            parts = CogDisguiseGlobals.getTotalParts(self.avatar.cogParts[deptIndex])
            partsRequired = CogDisguiseGlobals.PartsPerSuit[deptIndex]
            if level > 0:
                status = 'Level %s' % (level + 1)
            else:
                status = '%s/%s parts' % (parts, partsRequired)
        except:
            status = ''

        DirectLabel(parent=self.dSuitsFrame, pos=TAPG.disguiseTextPos[suitKind],
                    relief=None, text='%s\n%s' % (suitName, status),
                    text_fg=Vec4(1, 1, 1, 1), text_scale=0.026,
                    text_wordwrap=6, text_align=TextNode.ACenter)

        try:
            merits = self.avatar.cogMerits[deptIndex]
            meritText = str(merits)
        except:
            meritText = '0'
        DirectWaitBar(parent=self.dSuitsFrame, relief=DGG.SUNKEN,
                      frameSize=(-0.8, 0.8, -0.2, 0.2), borderWidth=(0.02, 0.02),
                      scale=0.1, text=meritText, text_scale=0.22,
                      text_fg=(0, 0, 0, 1), text_align=TextNode.ACenter,
                      text_pos=(0, -0.085), pos=TAPG.disguiseBarsPos[suitKind],
                      frameColor=(0.35, 0.35, 0.35, 1),
                      barColor=(0.75, 0.75, 0.75, 1), value=0, range=1)
        return suit

    def dShowQuests(self):
        self.dQuestsButton['state'] = DGG.DISABLED
        # Clash leaves the title blank on this page so it cannot overlap
        # the top row of ToonTask posters.
        self.dTitle['text'] = ''
        if not self.dQuestsFrame:
            self.dQuestsFrame = DirectFrame(
                parent=self.dMainFrame,
                scale=(-1.17, 1.17, 1.17),
                relief=None)
            # Centre the complete 2x2 poster grid inside the details panel.
            self.dQuestsFrame.setPos(0.015, 0, 0.035)
            self.__generateQuests()
        else:
            self.dQuestsFrame.show()

    def __generateQuests(self):
        quests = getattr(self.avatar, 'quests', [])
        if not quests:
            DirectLabel(parent=self.dQuestsFrame, relief=None, text='No active quests.',
                        text_fg=(1, 1, 1, 1), text_scale=0.045, pos=(0, 0, 0))
            return
        maxQuests = min(4, len(quests))
        questPositions = (
            (-0.165, 0, 0.005, 0, 0, 0),
            (0.165, 0, 0.005, 0, 0, 0),
            (-0.165, 0, -0.185, 0, 0, 0),
            (0.165, 0, -0.185, 0, 0, 0),
        )
        for i in range(maxQuests):
            try:
                frame = QuestBookPoster.QuestBookPoster(
                    parent=self.dQuestsFrame, mapIndex=i + 1, reverse=i % 2)
                frame.reparentTo(self.dQuestsFrame)
                frame.setPosHpr(*questPositions[i])
                frame.setScale(0.305)
                frame.update(quests[i])
                self.questFrames.append(frame)
            except:
                DirectLabel(parent=self.dQuestsFrame, relief=None,
                            text='Quest %s' % (i + 1), text_fg=(1, 1, 1, 1),
                            text_scale=0.04, pos=questPositions[i][:3])

    def generateToon(self):
        try:
            style = self.avatar.style
        except:
            try:
                style = self.avatar.getStyle()
            except:
                return None
        toon = Toon.Toon()
        toon.setDNAString(style.makeNetString())
        toon.getGeomNode().setDepthWrite(1)
        toon.getGeomNode().setDepthTest(1)
        toon.getGeomNode().setTwoSided(True)

        # Capture Neutral before applying the selected pose.  Only the known
        # off-centre poses use Clash's posed-composition fitting; all others
        # keep the Neutral-reference path.
        neutralBounds = self.getNeutralBounds(toon)
        poseId = getattr(self.avatar, 'profilePose', TPG.DEFAULT_POSE)
        try:
            poseId = self.avatar.getProfilePose()
        except:
            pass
        offset = TPG.applyPose(toon, poseId, self.notify)
        toon._toonProfilePoseId = poseId
        toon._toonProfilePanelOffset = offset

        # Sinking is centred from the Toon body because its melt animation
        # moves the body root downward.  Naptime keeps the full Toon-and-ZZZ
        # composition and receives its intended upward panel offset later.
        bodyCenteredPose = poseId == 27
        # Elegance's sprinkle-dust animation shifts the posed body away from
        # Neutral's visual anchor.  Use complete posed-bounds fitting for it
        # in the Toon Panel as well.
        posedFit = TPG.usesPosedPanelFit(poseId) or poseId == 40
        toon._toonProfileUsesPosedFit = posedFit and not bodyCenteredPose
        toon._toonProfileNeutralBounds = neutralBounds
        return toon

    def fitSelectedPoseOnPanel(self, toon, parent, neutralBounds, dimension,
                               basePos):
        """Centre a complete posed composition in the Toon Panel.

        This mirrors the left Shticker Book page's centring hierarchy.  The
        selected animation, root motion, HPR and props are measured together,
        then their visible centre is placed on Neutral's fixed panel anchor.
        Wide or tall compositions are shrunk only when required to remain
        inside the panel.
        """
        poseRoot = parent.attachNewNode('toonProfilePanelPoseRoot')
        scaleRoot = poseRoot.attachNewNode('toonProfilePanelScaleRoot')
        offsetRoot = scaleRoot.attachNewNode('toonProfilePanelOffsetRoot')
        facingRoot = offsetRoot.attachNewNode('toonProfilePanelFacingRoot')
        facingRoot.setH(180)
        toon.reparentTo(facingRoot)

        p1 = Point3()
        p2 = Point3()
        try:
            scaleRoot.calcTightBounds(p1, p2)
        except:
            toon.reparentTo(parent)
            self.fitGeometry(toon, 1, referenceBounds=neutralBounds)
            self.centerPoseOnNeutral(toon, parent, basePos)
            poseRoot.removeNode()
            return None

        posedSize = p2 - p1
        posedBiggest = max(posedSize[0], posedSize[2])
        if posedBiggest <= 0:
            posedBiggest = 1.0

        neutralBiggest = posedBiggest
        if neutralBounds is not None:
            neutralSize = neutralBounds[1] - neutralBounds[0]
            candidate = max(neutralSize[0], neutralSize[2])
            if candidate > 0:
                neutralBiggest = candidate

        neutralScale = dimension / neutralBiggest
        posedFitScale = dimension / posedBiggest
        finalScale = min(neutralScale, posedFitScale)

        posedCenter = (p1 + p2) / 2.0
        offsetRoot.setPos(-posedCenter[0], -posedCenter[1], -posedCenter[2])
        scaleRoot.setScale(finalScale)
        poseRoot.setPos(basePos[0], basePos[1] + 2.0,
                        basePos[2] - 0.02)
        return poseRoot

    def getPoseBodyCenter(self, geom, relativeTo):
        """Return the posed Toon body's visual centre in relativeTo space."""
        props = getattr(geom, '_toonProfilePoseProps', [])
        stashedProps = []
        for prop in props:
            try:
                prop.stash()
                stashedProps.append(prop)
            except:
                pass

        try:
            p1 = Point3()
            p2 = Point3()
            geom.calcTightBounds(p1, p2)
            localCenter = (p1 + p2) / 2.0
            try:
                return relativeTo.getRelativePoint(geom, localCenter)
            except:
                return geom.getMat(relativeTo).xformPoint(localCenter)
        except:
            return None
        finally:
            for prop in stashedProps:
                try:
                    prop.unstash()
                except:
                    pass

    def centerPoseOnNeutral(self, geom, relativeTo, basePos):
        # fitGeometry places Neutral's body centre at (0, 2, -0.02).  Align
        # the currently posed body to that same point without changing its
        # animation, HPR, scale, or props.
        geom.setPos(basePos[0], basePos[1], basePos[2])
        bodyCenter = self.getPoseBodyCenter(geom, relativeTo)
        if bodyCenter is None:
            return

        neutralCenter = Point3(basePos[0], basePos[1] + 2.0,
                               basePos[2] - 0.02)
        correction = neutralCenter - bodyCenter
        currentPos = geom.getPos(relativeTo)
        geom.setPos(relativeTo,
                    currentPos[0] + correction[0],
                    currentPos[1],
                    currentPos[2] + correction[2])

    def getNeutralBounds(self, geom):
        try:
            geom.pose('neutral', 0)
        except:
            try:
                geom.loop('neutral')
            except:
                pass

        p1 = Point3()
        p2 = Point3()
        try:
            geom.calcTightBounds(p1, p2)
            return (Point3(p1), Point3(p2))
        except:
            return None

    def fitGeometry(self, geom, fFlip=0, dimension=0.4, referenceBounds=None, includePoseProps=False):
        # Use the Neutral pose as the common centre and scale reference.  The
        # selected pose is never allowed to recalculate its own anchor.
        if referenceBounds is not None:
            p1 = Point3(referenceBounds[0])
            p2 = Point3(referenceBounds[1])
        else:
            props = getattr(geom, '_toonProfilePoseProps', [])
            stashedProps = []
            if not includePoseProps:
                for prop in props:
                    try:
                        prop.stash()
                        stashedProps.append(prop)
                    except:
                        pass

            p1 = Point3()
            p2 = Point3()
            try:
                geom.calcTightBounds(p1, p2)
            finally:
                for prop in stashedProps:
                    try:
                        prop.unstash()
                    except:
                        pass

        if fFlip:
            t = p1[0]
            p1.setX(-p2[0])
            p2.setX(-t)
        d = p2 - p1
        biggest = max(d[0], d[2])
        if biggest == 0:
            return
        scale = dimension / biggest
        mid = (p1 + d / 2.0) * scale
        geomXform = hidden.attachNewNode('geomXform')
        for child in geom.getChildren():
            child.reparentTo(geomXform)
        geomXform.setPosHprScale(-mid[0], -mid[1] + 2, -mid[2] - 0.02,
                                180, 0, 0, scale, scale, scale)
        geomXform.reparentTo(geom)

    def generateNameText(self):
        self.tapNameLabel = TextNode('text')
        self.tapNameLabel.setText(self.avName)
        self.tapNameLabel.setAlign(TextNode.ACenter)
        self.tapNameLabel.setWordwrap(10)
        self.tapNameLabel.setTextColor(1, 1, 1, 1)
        try:
            self.tapNameLabel.setFont(self.avatar.getFont())
        except:
            self.tapNameLabel.setFont(ToontownGlobals.getToonFont())
        self.tapNameLabel.setShadow(0.05, 0.05)
        self.tapNameLabel.setShadowColor(0, 0, 0, 1)
        self.tapNameNodePath = self.tapMainFrame.attachNewNode(self.tapNameLabel)
        self.tapNameNodePath.setScale(0.042)
        self.tapNameNodePath.setPos(0, 0, 0.12)
        self.tapNameNodePath.setBin('sorted-gui-popup', 802)
        if self.tapNameLabel.getNumRows() > 1:
            self.tapNameNodePath.setPos(0, 0, 0.144)
            self.tapNameNodePath.setScale(0.038)

    def getAvatarBackground(self):
        backgroundId = getattr(self.avatar, 'profileBackground', TPG.DEFAULT_BACKGROUND)
        try:
            backgroundId = self.avatar.getProfileBackground()
        except:
            pass
        background = TPG.getBackground(backgroundId)
        node = self.profileBackgroundModel.find('**/%s' % background['node'])
        if node.isEmpty():
            node = self.profileBackgroundModel.find('**/default')
        if node.isEmpty():
            return self.profileBackgroundModel
        return node

    def __getRawNameplateValue(self):
        methodNames = (
            'getEquippedNameplate', 'getProfileNameplate', 'getNameplate',
            'getNameplateId', 'getNamePlate', 'getNamePlateId')
        for name in methodNames:
            if hasattr(self.avatar, name):
                try:
                    value = getattr(self.avatar, name)()
                    if value is not None:
                        return value
                except:
                    pass
        attrNames = (
            'equippedNameplate', 'profileNameplate', 'nameplate', 'nameplateId',
            'namePlate', 'namePlateId', 'equippedNameplateId')
        for name in attrNames:
            if hasattr(self.avatar, name):
                value = getattr(self.avatar, name)
                if value is not None:
                    return value
        return None

    def __normaliseNameplateNode(self, value):
        if value is None:
            return 'default_med_blue'
        if hasattr(value, 'getItemSubtype'):
            try:
                value = value.getItemSubtype()
            except:
                pass
        if isinstance(value, (list, tuple)):
            if not value:
                return 'default_med_blue'
            value = value[0]
        try:
            intValue = int(value)
            if intValue in NAMEPLATE_ID_TO_NODE:
                return NAMEPLATE_ID_TO_NODE[intValue]
        except:
            pass
        try:
            text = str(value).strip().lower().replace('_', ' ')
        except:
            return 'default_med_blue'
        if text.startswith('**/'):
            text = text[3:]
        if text in NAMEPLATE_NAME_TO_NODE:
            return NAMEPLATE_NAME_TO_NODE[text]
        compact = text.replace(' ', '')
        if compact in NAMEPLATE_NAME_TO_NODE:
            return NAMEPLATE_NAME_TO_NODE[compact]
        if 'dream' in text or 'skyclan' in text:
            return 'event_skyclan'
        if text == 'candy' or text.endswith(' candy'):
            return 'event_candy'
        return text if text else 'default_med_blue'

    def getAvatarNameplate(self):
        nameplateId = getattr(self.avatar, 'profileNameplate', TPG.DEFAULT_NAMEPLATE)
        try:
            nameplateId = self.avatar.getProfileNameplate()
        except:
            rawValue = self.__getRawNameplateValue()
            if rawValue is not None:
                nameplateId = rawValue
        nameplate = TPG.getNameplate(nameplateId)
        node = self.profileNameplateModel.find('**/%s' % nameplate['node'])
        if node.isEmpty():
            node = self.profileNameplateModel.find('**/default_med_blue')
        position = nameplate.get('position', (0, 0, 0.13))
        scale = nameplate.get('scale', (1, 1, 1))
        return node, position, scale

    def generateInfoText(self, hp=None, maxHp=None):
        if hp is None:
            hp = getattr(self.avatar, 'hp', 0)
        if maxHp is None:
            maxHp = getattr(self.avatar, 'maxHp', hp)
        level = getattr(self.avatar, 'level', 0) + 1
        toonId = 'TTPA-U-%s' % (self.avId - 100000000)
        online = self.isAvatarOnline()

        lines = ['Status: %s' % ('Online' if online else 'Offline'),
                 'Laff: %s / %s' % (hp, maxHp),
                 'Level: %s' % level,
                 'Toon ID: %s' % toonId]

        if online:
            shardId = getattr(self.avatar, 'defaultShard', 0)
            hoodId = getattr(self.avatar, 'lastHood', 0)
            try:
                shardName = base.cr.getShardName(shardId)
            except:
                shardName = 'Unknown District'
            try:
                hoodName = base.cr.hoodMgr.getFullnameFromId(hoodId)
            except:
                hoodName = 'Somewhere in Toontown'
            if ZoneUtil.isWelcomeValley(hoodId):
                try:
                    hoodName = '%s (%s)' % (TTLocalizer.WelcomeValley[-1], hoodName)
                except:
                    pass
            lines.insert(2, 'District: %s' % shardName)
            lines.insert(3, 'Location: %s' % hoodName)
        return '\n'.join(lines)

    def updateInfoText(self, hp, maxHp, quietly=None):
        if self.dInfoFrame and hasattr(self, 'detailsInfoText'):
            self.detailsInfoText['text'] = self.generateInfoText(hp, maxHp)

    def isAvatarOnline(self):
        if self.avId == base.localAvatar.doId:
            return True
        if self.avId in base.cr.doId2do:
            return True
        try:
            if base.cr.isFriend(self.avId):
                return bool(base.cr.isFriendOnline(self.avId))
        except:
            pass
        return False

    def refreshIgnoreButton(self):
        if not self.isLoaded or not hasattr(self, 'tapIgnoreButton'):
            return
        ignoreStr, ignoreCmd, ignoreScale = self.getIgnoreButtonInfo()
        self.tapIgnoreButton['text'] = ('', ignoreStr, ignoreStr)
        self.tapIgnoreButton['command'] = ignoreCmd
        self.__updateButtonStates()

    def cleanup(self):
        if self.waitingForDetails and self.lookupAvatar:
            try:
                base.cr.cancelAvatarDetailsRequest(self.lookupAvatar)
            except:
                pass
            self.waitingForDetails = False

        self.ignoreAll()

        for frame in self.questFrames:
            try:
                frame.destroy()
            except:
                pass
        self.questFrames = []

        for suit in self.dSuits:
            try:
                suit.delete()
            except:
                pass
        self.dSuits = []

        if self.toon:
            for node in self.toonClippingPlanes:
                try:
                    self.toon.setClipPlaneOff(node)
                    node.removeNode()
                except:
                    pass
            self.toonClippingPlanes = []
            try:
                self.toon.delete()
            except:
                pass
            self.toon = None

        if self.toonPoseRoot:
            try:
                self.toonPoseRoot.removeNode()
            except:
                pass
            self.toonPoseRoot = None

        if self.managedGuiElement:
            try:
                self.managedGuiElement.destroy()
            except:
                pass
            self.managedGuiElement = None

        for modelName in ('gui', 'detailsGui', 'profileBackgroundModel', 'profileNameplateModel'):
            model = getattr(self, modelName, None)
            if model:
                try:
                    model.removeNode()
                except:
                    pass
                setattr(self, modelName, None)

        if self.createdAvatar and self.lookupAvatar:
            try:
                self.lookupAvatar.delete()
            except:
                pass
            self.lookupAvatar = None

        try:
            base.localAvatar.obscureFriendsListButton(-1)
        except:
            pass

        self.isLoaded = False
        self.frame = None
        try:
            AvatarPanelBase.AvatarPanelBase.cleanup(self)
        except:
            pass

    def getAvId(self):
        return getattr(self, 'avId', None)

    def getPlayerId(self):
        return self.playerId

    def isHidden(self):
        if not self.managedGuiElement:
            return 1
        return self.managedGuiElement.isHidden()

    def getType(self):
        return 'toon'
