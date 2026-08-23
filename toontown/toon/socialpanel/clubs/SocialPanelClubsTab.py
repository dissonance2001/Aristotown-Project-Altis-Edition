# Altis Clubs Build 85: working Club invite selector for nearby Toons and friends.
import time
import textwrap

from direct.gui.DirectGui import DirectButton, DirectEntry, DirectFrame, DirectLabel, DirectScrolledFrame, DirectWaitBar
from direct.gui import DirectGuiGlobals as DGG
from pandac.PandaModules import AntialiasAttrib, TextNode, Texture, TransparencyAttrib, Vec4

from toontown.club import ClubGlobals
from toontown.club import ClubShopCatalog
from toontown.club.ClubClasses import ClubIcon
from toontown.club.ClubIconGUI import ClubIconGUI
from toontown.quest.QuestPoster import QuestPoster
from toontown.toon.gui.ClubJellybeanDonationGUI import ClubJellybeanDonationGUI
from toontown.toon.socialpanel.SocialPanelGlobals import sp_gui
from toontown.toon.socialpanel.clubs.general.ClubLevelShield import ClubLevelShield
from toontown.toonbase import ToontownGlobals


class SocialPanelClubsTab(DirectFrame):
    """Python 2-compatible Clash-style Club tab for Project Altis."""

    def __init__(self, parent):
        DirectFrame.__init__(
            self,
            parent=parent,
            relief=None,
            frameSize=(-0.25, 0.25, -0.45, 0.45),
        )
        self.initialiseoptions(SocialPanelClubsTab)
        self.setTransparency(TransparencyAttrib.MAlpha)

        self.panel = parent
        self.manager = base.cr.clubMgr
        self.page = 'main'
        self.pageObjects = []
        self.navButtons = []
        self.selectedMember = None
        self.donationGui = None
        self.boosterTooltip = None
        self.boosterTooltipTime = None
        self.boosterTooltipEndTime = 0
        self.boosterTooltipTaskName = 'club-booster-tooltip-%s' % id(self)
        self.boosterTooltipCoveredObjects = []
        self.taskScroll = None
        self.taskScrollCanvas = None
        self.taskScrollOffset = 0.0
        self.taskScrollMaxOffset = 0.0
        self.logsScroll = None
        self.membersScroll = None
        self.inviteScroll = None
        self.invitesSent = set()
        self.memberActionObjects = []

        # Source models used by the exact Clash main-tab status block. Keep
        # these alive for the lifetime of the tab because DirectFrame images
        # instance their nodes.
        try:
            self._mainJarGui = loader.loadModel('phase_3.5/models/gui/jar_gui')
        except:
            self._mainJarGui = None
        try:
            self._mainClubShopGui = loader.loadModel(
                'phase_3.5/models/gui/clubs/club_shop')
        except:
            self._mainClubShopGui = None

        # Keep the standard ToonTask GUI/icon models alive.  The Club
        # Task page now builds each entry through Altis's real QuestPoster
        # nodes, matching Clash's blue Club Task poster instead of stretching
        # a raw questCard node into a thin scroll.
        try:
            self._clubTaskGui = loader.loadModel(
                'phase_3.5/models/gui/stickerbook_gui')
        except:
            self._clubTaskGui = None
        try:
            self._clubTaskCogGui = loader.loadModel(
                'phase_3/models/gui/cog_icons')
        except:
            self._clubTaskCogGui = None
        try:
            self._clubTaskSosGui = loader.loadModel(
                'phase_3.5/models/gui/sos_textures')
        except:
            self._clubTaskSosGui = None
        try:
            self._clubBoosterGui = loader.loadModel(
                'phase_3.5/models/gui/boosters')
        except:
            self._clubBoosterGui = None
        try:
            self._clubRerollGui = loader.loadModel(
                'phase_3/models/gui/tt_m_gui_mat_mainGui')
        except:
            self._clubRerollGui = None
        try:
            self._clubTaskDiceGui = loader.loadModel(
                'phase_4/models/minigames/dice')
        except:
            self._clubTaskDiceGui = None

        for model in (self._clubTaskGui, self._clubTaskCogGui,
                      self._clubTaskSosGui, self._clubBoosterGui,
                      self._clubRerollGui, self._clubTaskDiceGui):
            self._improveTextureQuality(model)

        self.accept('club-state-updated', self._stateUpdated)
        self.accept('club-logs-updated', self._logsUpdated)
        self.accept('club-notification', self._notification)

        self._makeNavigation()
        self.showPage('main')

    # ------------------------------------------------------------------
    # Generic GUI helpers
    # ------------------------------------------------------------------
    def _improveTextureQuality(self, model):
        """Use linear filtering on scaled GUI artwork.

        The legacy Altis texture defaults make the small blue task posters
        and Booster icons look blocky when they are reduced to panel size.
        """
        if model is None:
            return
        try:
            model.setAntialias(AntialiasAttrib.MAuto)
        except:
            pass
        try:
            textures = model.findAllTextures()
            for index in range(textures.getNumTextures()):
                texture = textures.getTexture(index)
                texture.setMinfilter(Texture.FTLinear)
                texture.setMagfilter(Texture.FTLinear)
                try:
                    texture.setAnisotropicDegree(4)
                except:
                    pass
        except:
            pass

    def _findNode(self, name):
        node = sp_gui.find('**/%s' % name)
        if node.isEmpty():
            return None
        return node

    def _buttonImages(self, prefix):
        normal = self._findNode('%s_N' % prefix)
        pressed = self._findNode('%s_P' % prefix)
        hover = self._findNode('%s_H' % prefix)
        if normal is None:
            return None
        if pressed is None:
            pressed = normal
        if hover is None:
            hover = normal
        return (normal, pressed, hover, normal)

    def _add(self, obj):
        self.pageObjects.append(obj)
        return obj

    def _clearPage(self):
        self._hideBoosterTooltip()
        self.boosterTooltipCoveredObjects = []
        self.ignore('wheel_up')
        self.ignore('wheel_down')
        self.taskScroll = None
        self.taskScrollCanvas = None
        self.taskScrollOffset = 0.0
        self.taskScrollMaxOffset = 0.0
        self.logsScroll = None
        self.membersScroll = None
        self.inviteScroll = None
        self.memberActionObjects = []
        for obj in self.pageObjects:
            try:
                obj.destroy()
            except:
                try:
                    obj.removeNode()
                except:
                    pass
        self.pageObjects = []
        self.clubMotdEntry = None

    def _makeSmallButton(self, text, pos, command, extraArgs=None,
                         frameColor=(0.25, 0.55, 0.30, 0.95), scale=1.0):
        if extraArgs is None:
            extraArgs = []
        return DirectButton(
            parent=self,
            relief=DGG.RAISED,
            borderWidth=(0.006, 0.006),
            frameSize=(-0.075, 0.075, -0.024, 0.026),
            frameColor=frameColor,
            pos=pos,
            scale=scale,
            text=text,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.020,
            text_pos=(0, -0.006),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            command=command,
            extraArgs=extraArgs,
        )

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def _makeNavigation(self):
        data = (
            ('Tree', 'Main', 'main'),
            ('Scroll', 'Tasks', 'tasks'),
            (None, 'Members', 'members'),
            ('Logs', 'History', 'logs'),
            ('ClubGear', 'Settings', 'settings'),
        )
        xStart = -0.185
        xEnd = 0.188
        count = len(data)

        for index, item in enumerate(data):
            prefix, label, page = item
            amount = float(index) / float(count - 1)
            xPos = xStart + ((xEnd - xStart) * amount)

            # The Altis social_panel BAM contains a full-height geometry under
            # the nodes that Clash uses for its Members icon. Reusing either
            # List_N or ToonButton_N directly causes the dark strip through the
            # entire panel. Copy the already-rendering bottom Groups icon state
            # instead, then place an invisible click target over it.
            if page == 'members':
                iconCopy = None
                try:
                    sourceButton = self.panel.tabs.button_groupsTab
                    iconCopy = sourceButton.stateNodePath[0].copyTo(self)
                    iconCopy.setPos(xPos, 0, 0.442)
                    iconCopy.setScale(0.065)
                    iconCopy.setBin('gui-popup', 101)
                except:
                    iconCopy = DirectLabel(
                        parent=self,
                        relief=None,
                        pos=(xPos, 0, 0.442),
                        text='TT',
                        text_font=ToontownGlobals.getInterfaceFont(),
                        text_scale=0.027,
                        text_fg=(1, 1, 1, 1),
                        text_shadow=(0, 0, 0, 1),
                    )

                button = DirectButton(
                    parent=self,
                    relief=None,
                    pos=(xPos, 0, 0.442),
                    scale=0.065,
                    frameSize=(-0.72, 0.72, -0.51, 0.51),
                    text=('', label, label, ''),
                    text_fg=(1, 1, 1, 1),
                    text_bg=(0, 0, 0, 0.65),
                    text_shadow=(0, 0, 0, 1),
                    text_scale=0.5,
                    text_align=TextNode.ACenter,
                    text_pos=(0, 0.27),
                    command=self.showPage,
                    extraArgs=[page],
                    pressEffect=0,
                )
                button._membersIconCopy = iconCopy
                self.navButtons.append(button)
                continue

            images = self._buttonImages(prefix)
            if images is not None:
                button = DirectButton(
                    parent=self,
                    relief=None,
                    pos=(xPos, 0, 0.442),
                    scale=0.065,
                    image=images,
                    image_scale=(121.0 / 84.0, 1, 1),
                    frameSize=(-0.72, 0.72, -0.51, 0.51),
                    text=('', label, label, ''),
                    text_fg=(1, 1, 1, 1),
                    text_bg=(0, 0, 0, 0.65),
                    text_shadow=(0, 0, 0, 1),
                    text_scale=0.5,
                    text_align=TextNode.ACenter,
                    text_pos=(0, 0.27),
                    command=self.showPage,
                    extraArgs=[page],
                    pressEffect=0,
                )
            else:
                button = DirectButton(
                    parent=self,
                    relief=DGG.RAISED,
                    pos=(xPos, 0, 0.442),
                    scale=1.0,
                    frameSize=(-0.040, 0.040, -0.020, 0.022),
                    frameColor=(0.32, 0.65, 0.38, 0.95),
                    text=label,
                    text_scale=0.021,
                    command=self.showPage,
                    extraArgs=[page],
                )
            self.navButtons.append(button)

    def reload(self):
        self.showPage(self.page)

    def showPage(self, page):
        self.page = page
        self._clearPage()

        if not self.manager.isInClub():
            self._showNoClub()
            return

        method = getattr(self, '_show%s' % page.title(), self._showMain)
        method()

    # ------------------------------------------------------------------
    # Main page
    # ------------------------------------------------------------------
    def _club(self):
        return self.manager.club or {}

    def _compactNumber(self, value):
        value = max(0, int(value or 0))
        if value >= 1000000000:
            number = value / 1000000000.0
            suffix = 'B'
        elif value >= 1000000:
            number = value / 1000000.0
            suffix = 'M'
        elif value >= 1000:
            number = value / 1000.0
            suffix = 'K'
        else:
            return str(value)
        if number >= 100 or int(number) == number:
            return '%d%s' % (int(number), suffix)
        return ('%.1f%s' % (number, suffix)).replace('.0', '')

    def _modelNode(self, model, name):
        if model is None:
            return None
        try:
            node = model.find('**/%s' % name)
            if node.isEmpty():
                return None
            return node
        except:
            return None

    def _boosterPrefixForItemId(self, itemId):
        try:
            itemId = int(itemId)
        except:
            return None
        if 2100 <= itemId < 2200:
            itemId -= 100
        return {
            2000: 'gag_support', 2001: 'gag_power',
            2002: 'gag_all', 2003: 'racing', 2004: 'trolley',
            2005: 'golf', 2006: 'fishing', 2007: 'jellybean',
            2008: 'jellybean2', 2009: 'merit_sell',
            2010: 'merit_cash', 2011: 'merit_law',
            2012: 'merit_boss', 2014: 'merit',
            2015: 'sellboss', 2016: 'cashboss',
            2017: 'lawboss', 2018: 'bossboss', 2020: 'eyes',
            2021: 'sellbot', 2022: 'cashbot', 2023: 'lawbot',
            2024: 'bossbot', 2026: 'cog', 2027: 'mainwashere',
        }.get(itemId)

    def _boosterDisplayInfo(self, key):
        """Return ``(name, description, BAM node)`` for a Booster."""
        prefix = None
        boosterType = None
        name = None
        description = None
        try:
            itemId = int(key)
        except:
            itemId = 0

        if itemId:
            entry = ClubShopCatalog.SHOP_ITEMS.get(itemId)
            if entry and str(entry[1]).startswith('booster-'):
                name = str(entry[0])
                description = str(entry[6])
                boosterType = str(entry[1]).split('-', 1)[-1]
                prefix = self._boosterPrefixForItemId(itemId)

        if name is None:
            legacy = {
                'gag': (
                    'Gag XP Booster',
                    'All members in your Club earn extra Gag Experience.',
                    'gag_all'),
                'activity': (
                    'Activity XP Booster',
                    'All members in your Club earn extra Activity Experience.',
                    'trolley'),
                'merit': (
                    'Merit Booster',
                    'All members in your Club earn extra Cog disguise merits.',
                    'merit'),
                'department': (
                    'Department XP Booster',
                    'All members in your Club earn extra Department Experience.',
                    'cog'),
                'reward': (
                    'Boss Reward Booster',
                    'All members in your Club receive increased Boss rewards.',
                    'eyes'),
                'universal': (
                    'All-Star Booster',
                    'All members in your Club receive multiple reward boosts.',
                    'mainwashere'),
            }
            boosterType = str(key)
            name, description, prefix = legacy.get(
                boosterType,
                (str(key).title(), 'This Booster is active for your Club.', None),
            )

        node = self._modelNode(self._clubBoosterGui, prefix)
        if node is None:
            fallbackNodes = {
                'gag': ('gag_all', 'gag_support', 'gag_power'),
                'activity': ('racing', 'trolley', 'golf', 'fishing'),
                'merit': ('merit', 'merit_sell', 'merit_cash',
                          'merit_law', 'merit_boss'),
                'department': ('cog', 'sellbot', 'cashbot',
                               'lawbot', 'bossbot'),
                'reward': ('eyes', 'sellboss', 'cashboss',
                           'lawboss', 'bossboss'),
                'universal': ('mainwashere', 'gag_all', 'jellybean'),
            }
            for fallbackName in fallbackNodes.get(boosterType, ()):
                node = self._modelNode(self._clubBoosterGui, fallbackName)
                if node is not None:
                    break
        if node is None:
            node = self._modelNode(self._clubBoosterGui, 'mainwashere')
        return name, description, node

    def _formatBoosterTime(self, seconds):
        seconds = max(0, int(seconds))
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secondsOnly = seconds % 60

        if days:
            return '%sd %sh %sm' % (days, hours, minutes)
        if hours:
            return '%sh %sm' % (hours, minutes)
        if minutes:
            return '%sm %ss' % (minutes, secondsOnly)
        return '%ss' % secondsOnly

    def _forceBoosterTooltipForeground(self, guiObject, sort):
        """Keep every DirectGUI state node above the Club page widgets."""
        try:
            guiObject.setBin('gui-popup', sort)
            guiObject.setDepthTest(False)
            guiObject.setDepthWrite(False)
        except:
            pass
        try:
            for stateNode in guiObject.stateNodePath:
                stateNode.setBin('gui-popup', sort)
                stateNode.setDepthTest(False)
                stateNode.setDepthWrite(False)
        except:
            pass

    def _showBoosterTooltip(self, name, description, endTime, event=None):
        self._hideBoosterTooltip()
        self.boosterTooltipEndTime = int(endTime)

        self.boosterTooltip = DirectFrame(
            parent=self,
            relief=DGG.RAISED,
            borderWidth=(0.006, 0.006),
            frameSize=(-0.232, 0.232, -0.112, 0.112),
            frameColor=(0.055, 0.070, 0.120, 1.0),
            # Sit directly below the Task Progress header. The previous
            # lower position left a large empty dark gap after the covered
            # task bars were hidden.
            pos=(0, 0, -0.117),
            state=DGG.DISABLED,
        )
        self._forceBoosterTooltipForeground(self.boosterTooltip, 1000)

        # DirectWaitBar state geometry can render above a later DirectFrame in
        # this legacy Panda3D build. Hide only the covered task bars while the
        # tooltip is open, then restore them when hovering ends.
        for coveredObject in self.boosterTooltipCoveredObjects:
            try:
                coveredObject.hide()
            except:
                pass

        titleLabel = DirectLabel(
            parent=self.boosterTooltip,
            relief=None,
            text=name,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.038,
            text_pos=(0, -0.010),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(0, 0, 0.080),
        )
        self._forceBoosterTooltipForeground(titleLabel, 1002)
        descriptionLabel = DirectLabel(
            parent=self.boosterTooltip,
            relief=None,
            text=description,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.024,
            text_wordwrap=18.0,
            text_align=TextNode.ACenter,
            text_fg=(0.90, 0.94, 1.0, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(0, 0, 0.014),
        )
        self._forceBoosterTooltipForeground(descriptionLabel, 1002)
        self.boosterTooltipTime = DirectLabel(
            parent=self.boosterTooltip,
            relief=None,
            text='',
            text_font=ToontownGlobals.getInterfaceFont(),
            # Larger than the description's old timer so the remaining
            # duration is readable at the Social Panel's in-game scale.
            text_scale=0.024,
            text_fg=(0.55, 0.85, 1.0, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(0, 0, -0.084),
        )
        self._forceBoosterTooltipForeground(self.boosterTooltipTime, 1002)
        self._updateBoosterTooltipTime()
        try:
            taskMgr.doMethodLater(
                1.0,
                self._boosterTooltipTick,
                self.boosterTooltipTaskName,
            )
        except:
            pass

    def _updateBoosterTooltipTime(self):
        if self.boosterTooltipTime is None:
            return
        remaining = max(0, self.boosterTooltipEndTime - int(time.time()))
        try:
            self.boosterTooltipTime['text'] = 'Time left: %s' % (
                self._formatBoosterTime(remaining))
        except:
            pass

    def _boosterTooltipTick(self, task):
        if self.boosterTooltip is None:
            return task.done
        self._updateBoosterTooltipTime()
        if self.boosterTooltipEndTime <= int(time.time()):
            self._hideBoosterTooltip()
            return task.done
        return task.again

    def _hideBoosterTooltip(self, event=None):
        try:
            taskMgr.remove(self.boosterTooltipTaskName)
        except:
            pass
        if self.boosterTooltip is not None:
            try:
                self.boosterTooltip.destroy()
            except:
                pass
        self.boosterTooltip = None
        self.boosterTooltipTime = None
        self.boosterTooltipEndTime = 0
        for coveredObject in self.boosterTooltipCoveredObjects:
            try:
                coveredObject.show()
            except:
                pass

    def _showNoClub(self):
        self._add(DirectLabel(
            parent=self,
            relief=None,
            text='You are not in a Club.\n\nTalk to Doe Vinci in Toon Hall\nto create one, or accept an invite\nfrom another Toon.',
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.030,
            text_wordwrap=15,
            pos=(0, 0, 0.08),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
        ))

    def _showMain(self):
        """Build the Clash main Club page shown in the reference screenshot."""
        club = self._club()

        self._add(DirectFrame(
            parent=self,
            relief=DGG.FLAT,
            frameSize=(-0.232, 0.234, -0.040, 0.040),
            frameColor=(0.455, 0.784, 0.376, 0.50),
            pos=(0.001, 0, 0.370),
            text=club.get('name', 'Club'),
            text_font=ToontownGlobals.getInterfaceFont(),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_align=TextNode.ACenter,
            text_scale=0.043,
            text_pos=(0, -0.014),
        ))

        iconData = club.get('icon', {})
        icon = ClubIcon(
            iconData.get('iconId', 1),
            iconData.get('backgroundId', 1),
            iconData.get('themeId', 0),
            iconData.get('backgroundColorId', 0),
        )
        self._add(ClubIconGUI(
            parent=self,
            clubIcon=icon,
            pos=(-0.140, 0, 0.240),
            scale=0.160,
        ))

        members = self.manager.getMembers()
        onlineCount = 0
        for member in members:
            if self._memberIsOnline(member):
                onlineCount += 1

        # Exact Clash three-line status block: online members, shared Club
        # Jellybeans and Club Coins, each with its original image node.
        status = self._add(DirectFrame(
            parent=self,
            relief=None,
            pos=(-0.178, 0, 0.130),
            scale=0.032,
            text='%s Online\n%s\n%s' % (
                onlineCount,
                self._compactNumber(club.get('jellybeans', 0)),
                self._compactNumber(club.get('coins', 0))),
            text_font=ToontownGlobals.getInterfaceFont(),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_align=TextNode.ALeft,
        ))

        onlineNode = self._findNode('OnlineMembers')
        if onlineNode is not None:
            DirectFrame(
                parent=status,
                relief=None,
                image=onlineNode,
                image_scale=(1.0, 1.0, 0.886),
                image_pos=(-0.765, 0.0, 0.351),
            )
        jarNode = self._modelNode(self._mainJarGui, 'Jar')
        if jarNode is not None:
            DirectFrame(
                parent=status,
                relief=None,
                image=jarNode,
                image_scale=(1.915, 1, 1.915),
                image_pos=(-0.754, 0, -0.676),
            )
        coinNode = self._modelNode(self._mainClubShopGui, 'choc')
        if coinNode is not None:
            DirectFrame(
                parent=status,
                relief=None,
                image=coinNode,
                image_scale=(1.0, 1.0, 1.0),
                image_pos=(-0.721, 0.0, -1.649),
            )

        experience = max(0, int(club.get('experience', club.get('xp', 0))))
        # Derive the displayed level and bar directly from total XP using the
        # same current Clash curve as the UberDOG backend.
        level, levelProgress, levelRange = ClubGlobals.calculateClubLevel(
            experience)

        self._add(DirectWaitBar(
            parent=self,
            pos=(0.1069, 0.0, 0.2897),
            scale=0.25,
            frameSize=(-0.43, 0.45, -0.08, 0.08),
            relief=DGG.SUNKEN,
            borderWidth=(0.014, 0.014),
            frameColor=(0.10, 0.22, 0.10, 1),
            barColor=(0.35, 0.76, 0.35, 1),
            value=levelProgress,
            range=max(1, levelRange),
            text='%s / %s XP' % (levelProgress, levelRange),
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.108,
            text_align=TextNode.ACenter,
            text_pos=(0.02, -0.03672),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
        ))
        levelShield = self._add(ClubLevelShield(
            parent=self,
            pos=(-0.030, 0, 0.291),
            scale=0.25,
        ))
        levelShield.setClubLevel(level)

        # Corporate Clash displays the Club message itself as the editable
        # field.  Clicking this area gives it a typing cursor; pressing Enter
        # sends the updated message to the Club manager.  Keep the original
        # main-page position instead of moving the message under the XP bar.
        canEditMotd = self.manager.localAvHasPermission(
            ClubGlobals.PERMISSION_MOTD)
        self.clubMotdEntry = self._add(DirectEntry(
            parent=self,
            relief=DGG.FLAT,
            frameSize=(-0.006, 0.273, -0.101, 0.029),
            frameColor=(0, 0, 0, 0.20),
            initialText=club.get('motd', '') or '',
            width=9.3,
            numLines=4,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.029,
            text_align=TextNode.ALeft,
            text_pos=(0.010, -0.030),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(-0.044, 0, 0.223),
            state=DGG.NORMAL if canEditMotd else DGG.DISABLED,
            cursorKeys=1,
            suppressKeys=1,
            command=self._submitClubMotd,
        ))

        helperData = (
            ('Plus', 'Invite Member', self._openInvitePage),
            ('AddBeans', 'Donate Jellybeans', self._openJellybeanDonation),
            ('Exclaim', 'Club Shout', self._openClubChat),
            ('Megaphone', 'Club Info', self._showClubInfo),
        )
        xStart = -0.014
        xEnd = 0.192
        for index, helper in enumerate(helperData):
            prefix, label, command = helper
            amount = float(index) / float(len(helperData) - 1)
            xPos = xStart + ((xEnd - xStart) * amount)
            images = self._buttonImages(prefix)
            if images is None:
                continue
            self._add(DirectButton(
                parent=self,
                relief=None,
                pos=(xPos, 0, 0.087),
                scale=0.045,
                image=images,
                image_scale=(147.0 / 106.0, 1, 1),
                text=('', label, label, ''),
                text_pos=(0, 0.90),
                text_scale=0.70,
                text_fg=(1, 1, 1, 1),
                text_bg=(0, 0, 0, 0.70),
                text_shadow=(0, 0, 0, 1),
                command=command,
                pressEffect=0,
            ))

        self._add(DirectLabel(
            parent=self,
            relief=DGG.FLAT,
            frameSize=(-0.231, 0.234, -0.054, 0),
            frameColor=(0.536, 1.0, 0.5, 0.331),
            pos=(0, 0, 0.049),
            text='Task Progress',
            text_font=ToontownGlobals.getInterfaceFont(),
            text_pos=(0, -0.038),
            text_scale=0.040,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
        ))

        tasks = club.get('tasks', [])[:ClubGlobals.MAX_ACTIVE_TASKS]
        if tasks:
            zPos = -0.028
            for task in tasks:
                progressType = str(task.get('progressType', ''))
                progress = max(0, int(task.get('progress', 0)))
                goal = max(1, int(task.get('goal', 1)))
                progress = min(progress, goal)
                taskProgressBar = self._add(DirectWaitBar(
                    parent=self,
                    relief=DGG.SUNKEN,
                    borderWidth=(0.004, 0.004),
                    frameSize=(-0.210, 0.210, -0.018, 0.020),
                    frameColor=(0.12, 0.12, 0.12, 1),
                    barColor=(0.50, 0.72, 0.50, 1),
                    value=progress,
                    range=goal,
                    pos=(0.002, 0, zPos),
                    text=self._clubTaskProgressText(
                        progressType, progress, goal),
                    text_font=ToontownGlobals.getInterfaceFont(),
                    text_scale=0.024,
                    text_pos=(0, -0.007),
                    text_fg=(1, 1, 1, 1),
                    text_shadow=(0, 0, 0, 1),
                ))
                self.boosterTooltipCoveredObjects.append(taskProgressBar)
                zPos -= 0.047
        else:
            self._add(DirectLabel(
                parent=self,
                relief=None,
                text='Club Tasks are being assigned automatically.',
                text_font=ToontownGlobals.getInterfaceFont(),
                text_scale=0.023,
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                pos=(0, 0, -0.060),
            ))

        boosters = club.get('boosters', {})
        activeBoosters = []
        now = int(time.time())
        for key, endTime in list(boosters.items()):
            remaining = max(0, int(endTime) - now)
            if remaining:
                activeBoosters.append((key, remaining))
        activeBoosters.sort(key=lambda booster: str(booster[0]))

        maxBoosters = max(1, int(club.get('maxBoosters', 1)))
        self._add(DirectLabel(
            parent=self,
            relief=DGG.FLAT,
            frameSize=(-0.231, 0.234, -0.054, 0),
            frameColor=(0.536, 1.0, 0.5, 0.331),
            pos=(0, 0, -0.158),
            text='Club Boosters (%s/%s)' % (
                len(activeBoosters), maxBoosters),
            text_font=ToontownGlobals.getInterfaceFont(),
            text_pos=(0, -0.038),
            text_scale=0.040,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
        ))

        if not activeBoosters:
            self._add(DirectLabel(
                parent=self,
                relief=None,
                text='Your Club has no active Boosters.',
                text_font=ToontownGlobals.getInterfaceFont(),
                text_scale=0.028,
                text_wordwrap=12,
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                pos=(0, 0, -0.270),
            ))
        else:
            shown = activeBoosters[:3]
            count = len(shown)
            if count == 1:
                xPositions = (0.0,)
            elif count == 2:
                xPositions = (-0.115, 0.115)
            else:
                xPositions = (-0.145, 0.0, 0.145)

            for index, booster in enumerate(shown):
                key, remaining = booster
                endTime = int(boosters.get(key, int(time.time()) + remaining))
                name, description, iconNode = self._boosterDisplayInfo(key)
                xPos = xPositions[index]

                # Use the authored Booster node at the same visual size as
                # Clash's main Club page.  The hit frame remains slightly
                # larger than the artwork so hovering is comfortable.
                icon = self._add(DirectFrame(
                    parent=self,
                    relief=None,
                    frameSize=(-0.075, 0.075, -0.075, 0.075),
                    state=DGG.NORMAL,
                    image=iconNode,
                    image_scale=0.120,
                    image_pos=(0, 0, 0.0095),
                    pos=(xPos, 0, -0.285),
                ))
                icon.setTransparency(TransparencyAttrib.MAlpha)
                icon.bind(
                    DGG.ENTER,
                    self._showBoosterTooltip,
                    extraArgs=[name, description, endTime],
                )
                icon.bind(DGG.EXIT, self._hideBoosterTooltip)

    def _submitClubMotd(self, *unused):
        entry = getattr(self, 'clubMotdEntry', None)
        if entry is None:
            return
        if not self.manager.localAvHasPermission(ClubGlobals.PERMISSION_MOTD):
            return
        try:
            motd = entry.get()
        except:
            return
        motd = str(motd).strip()[:ClubGlobals.CLUB_MOTD_MAX]
        try:
            entry.enterText(motd)
            entry['focus'] = 0
        except:
            pass
        self.manager.requestSetMotd(motd)

    def _openInvitePage(self):
        if not self.manager.localAvHasPermission(ClubGlobals.PERMISSION_INVITE):
            self._notification(
                ClubGlobals.NOTIFY_ERROR,
                'You do not have permission to invite Toons to this Club.')
            return
        if len(self.manager.getMembers()) >= ClubGlobals.CLUB_MAX_MEMBERS:
            self._notification(ClubGlobals.NOTIFY_ERROR, 'Your Club is full.')
            return
        self.invitesSent = set()
        self.showPage('invite')

    def _openClubChat(self):
        chatLog = getattr(base.cr, 'chatLog', None)
        if chatLog is None:
            return
        try:
            chatLog._selectTab(chatLog.TAB_CLUBS)
            chatLog.open(focus=True)
        except:
            pass

    def _showClubInfo(self):
        self._notification(ClubGlobals.NOTIFY_INFO, 'Use the tabs above to manage your Club.')

    # ------------------------------------------------------------------
    # Tasks page
    # ------------------------------------------------------------------
    def _pageTitle(self, text):
        return self._add(DirectFrame(
            parent=self,
            relief=DGG.FLAT,
            frameSize=(-0.232, 0.234, -0.040, 0.040),
            frameColor=(0.455, 0.784, 0.376, 0.55),
            pos=(0.001, 0, 0.370),
            text=text,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_scale=0.040,
            text_pos=(0, -0.014),
        ))

    def _clubTasksPageTitle(self):
        """Use the authored Social Panel title strip from the reference UI."""
        titleNode = self._findNode('TitleBarThing')
        if titleNode is None:
            return self._pageTitle('Club Tasks')
        return self._add(DirectLabel(
            parent=self,
            relief=None,
            image=titleNode,
            image_scale=(492.0 / 74.0, 1, 1),
            scale=0.0704,
            pos=(0.001, 0, 0.370),
            text='Club Tasks',
            text_font=ToontownGlobals.getInterfaceFont(),
            text_pos=(0, -0.178),
            text_scale=0.625,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
        ))

    def _clubTaskNode(self, name):
        """Return a Club ToonTask GUI node without exposing an empty NodePath."""
        model = getattr(self, '_clubTaskGui', None)
        if model is None:
            return None
        try:
            node = model.find('**/%s' % name)
        except:
            return None
        if node.isEmpty():
            return None
        return node

    def _clubTaskIcon(self, progressType):
        """Return the normal ToonTask objective icon and its poster scale."""
        model = None
        nodeName = None

        if progressType == 'buildings':
            model = self._clubTaskGui
            nodeName = 'COG_building'
        elif progressType == 'trolley':
            model = self._clubTaskGui
            nodeName = 'trolley'
        elif progressType == 'fish':
            model = self._clubTaskSosGui
            nodeName = 'fish'
        elif progressType in ('cogs', 'bosses'):
            model = self._clubTaskCogGui
            nodeName = 'cog'

        if model is None or nodeName is None:
            return None, 0.13

        try:
            node = model.find('**/%s' % nodeName)
        except:
            return None, 0.13
        if node.isEmpty():
            return None, 0.13
        return node, 0.13

    def _clubTaskProgressText(self, progressType, progress, goal):
        if progressType == 'fish':
            return '%s of %s caught' % (progress, goal)
        if progressType in ('trolley', 'buildings'):
            return '%s of %s completed' % (progress, goal)
        return '%s of %s defeated' % (progress, goal)

    def _clubTaskDiceImages(self):
        model = getattr(self, '_clubTaskDiceGui', None)
        if model is None:
            return None
        normal = self._modelNode(model, 'dice_button1')
        pressed = self._modelNode(model, 'dice_button1_down')
        hover = self._modelNode(model, 'dice_button1_ro')
        if normal is None:
            return None
        if pressed is None:
            pressed = normal
        if hover is None:
            hover = normal
        return (normal, pressed, hover, normal)

    def _makeClubTaskPoster(self, task, slot, zPos, parent):
        """Create one large Club Task poster and its unframed reward row."""
        posterX = -0.020
        poster = self._add(QuestPoster())
        poster.reparentTo(parent)
        poster.setPos(posterX, 0, zPos)
        poster.setScale(0.46)
        poster.setTransparency(TransparencyAttrib.MAlpha)
        poster.setAntialias(AntialiasAttrib.MAuto)
        poster['image_color'] = Vec4(0.42, 0.671, 1.0, 1.0)
        poster.questFrame.hide()

        normalText = (0.20, 0.16, 0.12, 1)
        progressType = str(task.get('progressType', ''))
        progress = max(0, int(task.get('progress', 0)))
        goal = max(1, int(task.get('goal', 1)))
        progress = min(progress, goal)

        self._add(DirectLabel(
            parent=parent,
            relief=None,
            text='WANTED',
            text_font=ToontownGlobals.getMinnieFont(),
            text_scale=0.021,
            text_fg=normalText,
            pos=(posterX, 0, zPos + 0.104),
        ))

        pictureFrame = self._clubTaskNode('questPictureFrame')
        if pictureFrame is not None:
            self._add(DirectFrame(
                parent=parent,
                relief=None,
                image=pictureFrame,
                image_color=Vec4(0.42, 0.671, 1.0, 1.0),
                image_scale=0.058,
                pos=(-0.118, 0, zPos + 0.004),
            ))

        icon, unusedIconScale = self._clubTaskIcon(progressType)
        if icon is not None:
            self._add(DirectFrame(
                parent=parent,
                relief=None,
                geom=icon,
                geom_scale=0.058,
                pos=(-0.118, 0, zPos + 0.004),
            ))

        self._add(DirectLabel(
            parent=parent,
            relief=None,
            text=task.get('name', 'Club Task'),
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.021,
            text_wordwrap=10.5,
            text_align=TextNode.ACenter,
            text_fg=normalText,
            text_shadow=(1, 1, 1, 0.28),
            pos=(0.024, 0, zPos + 0.004),
        ))
        self._add(DirectLabel(
            parent=parent,
            relief=None,
            text='Anywhere',
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.016,
            text_fg=normalText,
            pos=(0.012, 0, zPos - 0.061),
        ))

        self._add(DirectWaitBar(
            parent=parent,
            relief=DGG.SUNKEN,
            borderWidth=(0.003, 0.003),
            frameSize=(-0.112, 0.112, -0.011, 0.012),
            frameColor=(0.945, 0.875, 0.706, 1),
            barColor=(0.5, 0.7, 0.5, 1),
            range=goal,
            value=progress,
            text=self._clubTaskProgressText(progressType, progress, goal),
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.0135,
            text_fg=(0.05, 0.14, 0.4, 1),
            text_shadow=(1, 1, 1, 0.35),
            text_pos=(0, -0.004),
            pos=(posterX, 0, zPos - 0.116),
        ))

        # The reference screenshot used a content-pack background behind this
        # row.  Keep the reward and amount, but do not draw our own frame.
        rewardCoins = max(0, int(task.get('rewardCoins', 0)))
        rewardZ = zPos - 0.176
        self._add(DirectLabel(
            parent=parent,
            relief=None,
            text='Reward:',
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.027,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(-0.190, 0, rewardZ - 0.008),
        ))

        coinNode = self._modelNode(self._mainClubShopGui, 'choc')
        if coinNode is not None:
            self._add(DirectFrame(
                parent=parent,
                relief=None,
                image=coinNode,
                image_scale=0.030,
                pos=(-0.078, 0, rewardZ),
            ))
        self._add(DirectLabel(
            parent=parent,
            relief=None,
            text='%s Club Coins' % rewardCoins,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.026,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(-0.043, 0, rewardZ - 0.008),
        ))

        if self.manager.localAvHasPermission(
                ClubGlobals.PERMISSION_PURCHASE_TASKS):
            rerollCost = max(0, int(task.get('rerollCost', 0)))
            diceImages = self._clubTaskDiceImages()
            if diceImages is not None:
                button = self._add(DirectButton(
                    parent=parent,
                    relief=None,
                    image=diceImages,
                    scale=0.040,
                    pos=(0.160, 0, rewardZ),
                    frameSize=(-0.62, 0.62, -0.62, 0.62),
                    text=('', 'Reroll (%s JB)' % rerollCost,
                          'Reroll (%s JB)' % rerollCost, ''),
                    text_font=ToontownGlobals.getInterfaceFont(),
                    text_scale=0.27,
                    text_pos=(0, 0.90),
                    text_fg=(1, 1, 1, 1),
                    text_bg=(0, 0, 0, 0.75),
                    text_shadow=(0, 0, 0, 1),
                    command=self.manager.requestRerollTask,
                    extraArgs=[slot],
                    pressEffect=0,
                ))
                button.setTransparency(TransparencyAttrib.MAlpha)
            else:
                rotateUp = self._modelNode(
                    self._clubRerollGui, 'tt_t_gui_mat_arrowRotateUp')
                rotateDown = self._modelNode(
                    self._clubRerollGui, 'tt_t_gui_mat_arrowRotateDown')
                if rotateUp is not None:
                    if rotateDown is None:
                        rotateDown = rotateUp
                    button = self._add(DirectButton(
                        parent=parent,
                        relief=None,
                        image=(rotateUp, rotateDown, rotateUp, rotateUp),
                        scale=0.036,
                        pos=(0.160, 0, rewardZ),
                        command=self.manager.requestRerollTask,
                        extraArgs=[slot],
                        pressEffect=0,
                    ))
                    button.setTransparency(TransparencyAttrib.MAlpha)

    def _scrollClubTasks(self, direction):
        """Move the authored vertical Club Settings-style scrollbar."""
        if self.taskScroll is None:
            return
        try:
            scrollBar = self.taskScroll.verticalScroll
            try:
                value = float(scrollBar.getValue())
            except:
                value = float(scrollBar['value'])
            value += float(direction) * 0.16
            value = max(0.0, min(1.0, value))
            scrollBar.setValue(value)
        except:
            pass

    def _showTasks(self):
        self._clubTasksPageTitle()
        tasks = self._club().get('tasks', [])
        if not tasks:
            self._add(DirectLabel(
                parent=self,
                relief=None,
                text='Club Tasks are being assigned automatically.',
                text_font=ToontownGlobals.getInterfaceFont(),
                text_scale=0.030,
                text_wordwrap=18,
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                pos=(0, 0, 0.11),
            ))
            return

        visibleTasks = tasks[:ClubGlobals.MAX_ACTIVE_TASKS]
        self.taskScroll = self._add(DirectScrolledFrame(
            parent=self,
            relief=None,
            pos=(0.002, 0, 0),
            frameSize=(-0.233, 0.233, -0.349, 0.329),
            canvasSize=(-0.225, 0.183, -0.930, 0.329),
            frameColor=(0, 0, 0, 0),
            scrollBarWidth=0.05,
            manageScrollBars=0,
            autoHideScrollBars=0,

            # Reuse the exact vertical scrollbar authored for Club Settings.
            verticalScroll_relief=None,
            verticalScroll_pos=(0.208, 0, 0),
            verticalScroll_frameSize=(-0.025, 0.025, -0.346, 0.329),
            verticalScroll_manageButtons=0,
            verticalScroll_resizeThumb=0,
            verticalScroll_image=sp_gui.find('**/ScrollBar_BAR'),
            verticalScroll_image_scale=(0.057, 1.0, 0.678),
            verticalScroll_image_pos=(0.0, 0.0, -0.010),

            verticalScroll_thumb_relief=None,
            verticalScroll_thumb_frameColor=(1, 1, 1, 0),
            verticalScroll_thumb_frameSize=(-0.025, 0.025, -0.059, 0.118),
            verticalScroll_thumb_image=sp_gui.find('**/ScrollBar'),
            verticalScroll_thumb_image_scale=(0.053, 1.0, 0.181),
            verticalScroll_thumb_image_pos=(0.0, 0.0, 0.029),
        ))
        self.taskScroll.setTransparency(TransparencyAttrib.MAlpha)
        self.taskScroll.horizontalScroll.hide()
        self.taskScroll.verticalScroll.incButton.hide()
        self.taskScroll.verticalScroll.decButton.hide()
        self.taskScroll.verticalScroll.setValue(0)
        self.taskScrollCanvas = self.taskScroll.getCanvas()

        zPositions = (0.175, -0.225, -0.625)
        for slot, task in enumerate(visibleTasks):
            self._makeClubTaskPoster(
                task, slot, zPositions[slot], self.taskScrollCanvas)

        if len(visibleTasks) > 2:
            self.accept('wheel_up', self._scrollClubTasks, [-1])
            self.accept('wheel_down', self._scrollClubTasks, [1])

    def _openJellybeanDonation(self):
        if self.donationGui is not None:
            try:
                self.donationGui.show()
                return
            except:
                self.donationGui = None
        self.donationGui = ClubJellybeanDonationGUI(
            self, self.manager, doneCallback=self._donationGuiClosed)

    def _donationGuiClosed(self):
        self.donationGui = None

    # ------------------------------------------------------------------
    # Invite page
    # ------------------------------------------------------------------
    def _scrollClubInvites(self, direction):
        if self.inviteScroll is None:
            return
        try:
            scrollBar = self.inviteScroll.verticalScroll
            try:
                value = float(scrollBar.getValue())
            except:
                value = float(scrollBar['value'])
            value += float(direction) * 0.13
            value = max(0.0, min(1.0, value))
            scrollBar.setValue(value)
        except:
            pass

    def _isInviteToon(self, obj, toonDClass=None):
        if obj is None or not hasattr(obj, 'getName'):
            return False

        # Prefer the exact DistributedToon dclass so NPC Toons and other
        # Toon-shaped distributed objects never appear in the invite list.
        if toonDClass is not None:
            try:
                if obj.dclass != toonDClass:
                    return False
                return not bool(getattr(obj, 'ghostMode', 0))
            except:
                pass

        try:
            className = obj.__class__.__name__
        except:
            return False
        if className not in ('DistributedToon', 'LocalToon'):
            return False
        return not bool(getattr(obj, 'ghostMode', 0))

    def _getInviteFriendAvIds(self):
        result = []
        for friend in getattr(base.localAvatar, 'friendsList', []):
            try:
                avId = int(friend[0])
            except:
                continue
            if avId not in result:
                result.append(avId)

        avatarFriendsManager = getattr(base.cr, 'avatarFriendsManager', None)
        if avatarFriendsManager is not None:
            for avId in getattr(avatarFriendsManager, 'avatarFriendsList', []):
                try:
                    avId = int(avId)
                except:
                    continue
                if avId not in result:
                    result.append(avId)
        return result

    def _identifyInviteHandle(self, avId):
        handle = None
        try:
            handle = base.cr.identifyFriend(avId)
        except:
            pass
        if handle is None and hasattr(base.cr, 'playerFriendsManager'):
            try:
                handle = base.cr.playerFriendsManager.getAvHandleFromId(avId)
            except:
                handle = None
        if handle is None:
            avatar = base.cr.doId2do.get(avId)
            if avatar is not None and hasattr(avatar, 'getName'):
                handle = avatar
        if handle is None and hasattr(base.cr, 'avatarFriendsManager'):
            try:
                handle = base.cr.avatarFriendsManager.getFriendInfo(avId)
                if handle is not None and not hasattr(handle, 'doId'):
                    handle.doId = avId
            except:
                handle = None
        return handle

    def _getClubInviteCandidates(self):
        localAvId = int(getattr(base.localAvatar, 'doId', 0))
        memberIds = set()
        for member in self.manager.getMembers():
            try:
                memberIds.add(int(member.get('avId', 0)))
            except:
                pass

        candidates = {}
        toonDClass = None
        try:
            toonDClass = base.cr.dclassesByName.get('DistributedToon')
        except:
            pass

        # Nearby Toons are shown first. This uses the same filtering as the
        # Friends tab, but clicking a row sends the Club invite immediately.
        for avId, obj in list(base.cr.doId2do.items()):
            try:
                avId = int(avId)
            except:
                continue
            if avId == localAvId or avId in memberIds:
                continue
            if not self._isInviteToon(obj, toonDClass):
                continue
            try:
                name = str(obj.getName())
            except:
                continue
            candidates[avId] = {
                'avId': avId,
                'name': name,
                'nearby': True,
                'online': True,
            }

        # Add friends that are not currently nearby. Offline invitations are
        # retained by the Club UD and delivered when that Toon requests state.
        for avId in self._getInviteFriendAvIds():
            if avId == localAvId or avId in memberIds or avId in candidates:
                continue
            handle = self._identifyInviteHandle(avId)
            if handle is None or not hasattr(handle, 'getName'):
                continue
            try:
                online = bool(base.cr.isFriendOnline(avId))
            except:
                online = avId in base.cr.doId2do
            try:
                name = str(handle.getName())
            except:
                continue
            candidates[avId] = {
                'avId': avId,
                'name': name,
                'nearby': False,
                'online': online,
            }

        result = list(candidates.values())
        try:
            result = list(result)
        except:
            pass
        result.sort(key=lambda candidate: (
            0 if candidate.get('nearby') else 1,
            0 if candidate.get('online') else 1,
            candidate.get('name', '').lower(),
        ))
        return result

    def _makeInviteSectionHeader(self, parent, text, count, yPos):
        DirectFrame(
            parent=parent,
            relief=DGG.FLAT,
            frameSize=(-0.214, 0.218, -0.025, 0.025),
            frameColor=(0.185, 0.365, 0.245, 0.92),
            pos=(-0.010, 0, yPos),
        )
        DirectLabel(
            parent=parent,
            relief=None,
            text='%s (%s)' % (text, count),
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.026,
            text_align=TextNode.ALeft,
            text_pos=(-0.195, -0.009),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(0, 0, yPos),
        )
        return yPos - 0.049

    def _makeClubInviteRow(self, parent, candidate, index, yPos):
        avId = int(candidate.get('avId', 0))
        name = str(candidate.get('name', 'Toon'))
        online = bool(candidate.get('online', False))
        nearby = bool(candidate.get('nearby', False))
        sent = avId in self.invitesSent

        rowColor = ((0.075, 0.090, 0.125, 0.94) if index % 2 == 0 else
                    (0.055, 0.066, 0.096, 0.94))
        hoverColor = (0.120, 0.165, 0.215, 0.98)
        row = DirectButton(
            parent=parent,
            relief=DGG.FLAT,
            borderWidth=(0.002, 0.002),
            frameSize=(-0.214, 0.218, -0.032, 0.032),
            frameColor=(rowColor, rowColor, hoverColor, rowColor),
            pos=(-0.010, 0, yPos),
            command=self._sendClubInvite if not sent else None,
            extraArgs=[avId, name],
            pressEffect=0,
            state=DGG.DISABLED if sent else DGG.NORMAL,
        )

        statusNode = self._findNode('WhiteCircle')
        statusColor = ((0.38, 0.95, 0.48, 1) if online else
                       (0.42, 0.45, 0.52, 1))
        if statusNode is not None:
            status = DirectFrame(
                parent=row,
                relief=None,
                image=statusNode,
                image_color=statusColor,
                image_scale=(97.0 / 86.0, 1, 1),
                pos=(-0.188, 0, 0.001),
                scale=0.0125,
            )
            status.setTransparency(TransparencyAttrib.MAlpha)

        DirectLabel(
            parent=row,
            relief=None,
            text=name,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.027,
            text_align=TextNode.ALeft,
            text_pos=(-0.160, -0.007),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(0, 0, 0.001),
        )
        if sent:
            statusText = 'Invite Sent'
        elif nearby:
            statusText = 'Nearby'
        elif online:
            statusText = 'Online Friend'
        else:
            statusText = 'Offline Friend'
        DirectLabel(
            parent=row,
            relief=None,
            text=statusText,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.0205,
            text_align=TextNode.ARight,
            text_pos=(0.190, -0.007),
            text_fg=((0.48, 1.0, 0.56, 1) if online or sent else
                     (0.64, 0.67, 0.75, 1)),
            text_shadow=(0, 0, 0, 1),
            pos=(0, 0, 0.001),
        )
        return yPos - 0.070

    def _sendClubInvite(self, avId, name):
        avId = int(avId)
        if avId == int(getattr(base.localAvatar, 'doId', 0)):
            return
        if not self.manager.isInClub():
            self.showPage('main')
            return
        if not self.manager.localAvHasPermission(ClubGlobals.PERMISSION_INVITE):
            self._notification(
                ClubGlobals.NOTIFY_ERROR,
                'You do not have permission to invite Toons to this Club.')
            return
        if self.manager.getMember(avId):
            self._notification(
                ClubGlobals.NOTIFY_ERROR,
                'That Toon is already in your Club.')
            self.showPage('invite')
            return
        if len(self.manager.getMembers()) >= ClubGlobals.CLUB_MAX_MEMBERS:
            self._notification(ClubGlobals.NOTIFY_ERROR, 'Your Club is full.')
            self.showPage('main')
            return

        self.invitesSent.add(avId)
        self.manager.requestInvite(avId, name)
        self.showPage('invite')

    def _showInvite(self):
        self._pageTitle('Invite a Toon')

        backImages = self._buttonImages('Arrow')
        if backImages is not None:
            self._add(DirectButton(
                parent=self,
                relief=None,
                pos=(-0.196, 0, 0.370),
                scale=0.035,
                image=backImages,
                image_scale=(-30.0 / 35.0, 1, 1),
                command=self.showPage,
                extraArgs=['main'],
                pressEffect=0,
            ))
        else:
            self._add(self._makeSmallButton(
                'Back', (-0.177, 0, 0.370), self.showPage, ['main'],
                scale=0.82))

        if not self.manager.localAvHasPermission(ClubGlobals.PERMISSION_INVITE):
            self._add(DirectLabel(
                parent=self,
                relief=None,
                text='You do not have permission to invite Toons.',
                text_font=ToontownGlobals.getInterfaceFont(),
                text_scale=0.029,
                text_wordwrap=16,
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                pos=(0, 0, 0.08),
            ))
            return

        if len(self.manager.getMembers()) >= ClubGlobals.CLUB_MAX_MEMBERS:
            self._add(DirectLabel(
                parent=self,
                relief=None,
                text='Your Club is full.',
                text_font=ToontownGlobals.getInterfaceFont(),
                text_scale=0.032,
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                pos=(0, 0, 0.08),
            ))
            return

        candidates = self._getClubInviteCandidates()
        nearby = [candidate for candidate in candidates if candidate.get('nearby')]
        friends = [candidate for candidate in candidates if not candidate.get('nearby')]

        self.inviteScroll = self._add(DirectScrolledFrame(
            parent=self,
            relief=None,
            pos=(0.002, 0, 0),
            frameSize=(-0.233, 0.233, -0.349, 0.329),
            canvasSize=(-0.225, 0.183, -0.349, 0.309),
            frameColor=(0, 0, 0, 0),
            scrollBarWidth=0.05,
            manageScrollBars=0,
            autoHideScrollBars=0,

            verticalScroll_relief=None,
            verticalScroll_pos=(0.208, 0, 0),
            verticalScroll_frameSize=(-0.025, 0.025, -0.346, 0.329),
            verticalScroll_manageButtons=0,
            verticalScroll_resizeThumb=0,
            verticalScroll_image=sp_gui.find('**/ScrollBar_BAR'),
            verticalScroll_image_scale=(0.057, 1.0, 0.678),
            verticalScroll_image_pos=(0.0, 0.0, -0.010),

            verticalScroll_thumb_relief=None,
            verticalScroll_thumb_frameColor=(1, 1, 1, 0),
            verticalScroll_thumb_frameSize=(-0.025, 0.025, -0.059, 0.118),
            verticalScroll_thumb_image=sp_gui.find('**/ScrollBar'),
            verticalScroll_thumb_image_scale=(0.053, 1.0, 0.181),
            verticalScroll_thumb_image_pos=(0.0, 0.0, 0.029),
        ))
        self.inviteScroll.setTransparency(TransparencyAttrib.MAlpha)
        self.inviteScroll.horizontalScroll.hide()
        self.inviteScroll.verticalScroll.incButton.hide()
        self.inviteScroll.verticalScroll.decButton.hide()
        self.inviteScroll.verticalScroll.setValue(0)
        canvas = self.inviteScroll.getCanvas()

        yPos = 0.286
        rowIndex = 0
        if nearby:
            yPos = self._makeInviteSectionHeader(
                canvas, 'NEARBY TOONS', len(nearby), yPos)
            for candidate in nearby:
                yPos = self._makeClubInviteRow(
                    canvas, candidate, rowIndex, yPos)
                rowIndex += 1

        if friends:
            if nearby:
                yPos -= 0.010
            yPos = self._makeInviteSectionHeader(
                canvas, 'FRIENDS', len(friends), yPos)
            for candidate in friends:
                yPos = self._makeClubInviteRow(
                    canvas, candidate, rowIndex, yPos)
                rowIndex += 1

        if not candidates:
            DirectLabel(
                parent=canvas,
                relief=None,
                text='No eligible nearby Toons or friends were found.',
                text_font=ToontownGlobals.getInterfaceFont(),
                text_scale=0.028,
                text_wordwrap=15,
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                pos=(-0.010, 0, 0.10),
            )

        canvasBottom = min(-0.350, yPos - 0.025)
        self.inviteScroll['canvasSize'] = (
            -0.225, 0.183, canvasBottom, 0.309)
        if canvasBottom < -0.360:
            self.accept('wheel_up', self._scrollClubInvites, [-1])
            self.accept('wheel_down', self._scrollClubInvites, [1])

    # ------------------------------------------------------------------
    # Members page
    # ------------------------------------------------------------------
    def _scrollClubMembers(self, direction):
        if self.membersScroll is None:
            return
        try:
            scrollBar = self.membersScroll.verticalScroll
            try:
                value = float(scrollBar.getValue())
            except:
                value = float(scrollBar['value'])
            value += float(direction) * 0.13
            value = max(0.0, min(1.0, value))
            scrollBar.setValue(value)
        except:
            pass

    def _memberIsOnline(self, member):
        """Return the member's actual online state.

        Altis Club member dictionaries can contain both ``online`` and
        ``avatarOnline``.  The older fallback expression treated a present but
        false ``online`` value as authoritative, even when ``avatarOnline``
        was true.  The local avatar is necessarily online while viewing this
        panel, and all known server fields are otherwise combined.
        """
        try:
            avId = int(member.get(
                'avId', member.get('avatarId', member.get('toonId', 0))) or 0)
        except:
            avId = 0

        try:
            if avId == int(base.localAvatar.doId):
                return True
        except:
            pass

        for key in ('online', 'avatarOnline', 'isOnline'):
            if key not in member:
                continue
            value = member.get(key)
            try:
                if isinstance(value, str):
                    value = value.strip().lower()
                    if value in ('1', 'true', 'yes', 'online'):
                        return True
                    continue
            except:
                pass
            if bool(value):
                return True
        return False

    def _memberRankIconName(self, rank):
        ownerRank = getattr(ClubGlobals, 'RANK_OWNER', 3)
        deputyRank = getattr(ClubGlobals, 'RANK_DEPUTY', 2)
        officerRank = getattr(ClubGlobals, 'RANK_OFFICER', 1)
        if rank >= ownerRank:
            return 'Star_Gold'
        if rank >= deputyRank:
            return 'Star_Silver'
        if rank >= officerRank:
            return 'Star_Bronze'
        return None

    def _makeMembersSectionHeader(self, parent, text, count, yPos, online):
        headerColor = ((0.185, 0.365, 0.245, 0.92) if online else
                       (0.145, 0.155, 0.190, 0.92))
        DirectFrame(
            parent=parent,
            relief=DGG.FLAT,
            frameSize=(-0.214, 0.218, -0.025, 0.025),
            frameColor=headerColor,
            pos=(-0.010, 0, yPos),
        )
        DirectLabel(
            parent=parent,
            relief=None,
            text='%s (%s)' % (text, count),
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.026,
            text_align=TextNode.ALeft,
            text_pos=(-0.195, -0.009),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(0, 0, yPos),
        )
        return yPos - 0.049

    def _makeClubMemberRow(self, parent, member, index, yPos):
        online = self._memberIsOnline(member)
        rankValue = int(member.get('rank', 0))
        rankName = ClubGlobals.RANK_NAMES.get(rankValue, 'Member')
        toonName = str(member.get('name', 'Toon'))
        avId = int(member.get('avId', 0))
        isLocal = avId == base.localAvatar.doId

        rowColor = ((0.075, 0.090, 0.125, 0.94) if index % 2 == 0 else
                    (0.055, 0.066, 0.096, 0.94))
        hoverColor = (0.120, 0.165, 0.215, 0.98)
        row = DirectButton(
            parent=parent,
            relief=DGG.FLAT,
            borderWidth=(0.002, 0.002),
            frameSize=(-0.214, 0.218, -0.032, 0.032),
            frameColor=(rowColor, rowColor, hoverColor, rowColor),
            pos=(-0.010, 0, yPos),
            command=self._selectMember,
            extraArgs=[member],
            pressEffect=0,
        )

        statusNode = self._findNode('WhiteCircle')
        statusColor = ((0.38, 0.95, 0.48, 1) if online else
                       (0.42, 0.45, 0.52, 1))
        if statusNode is not None:
            status = DirectFrame(
                parent=row,
                relief=None,
                image=statusNode,
                image_color=statusColor,
                image_scale=(97.0 / 86.0, 1, 1),
                pos=(-0.188, 0, 0.001),
                scale=0.0125,
            )
            status.setTransparency(TransparencyAttrib.MAlpha)
        else:
            DirectFrame(
                parent=row,
                relief=DGG.FLAT,
                frameSize=(-0.007, 0.007, -0.007, 0.007),
                frameColor=statusColor,
                pos=(-0.188, 0, 0.001),
            )

        iconName = self._memberRankIconName(rankValue)
        icon = self._findNode(iconName) if iconName else None
        if icon is not None:
            rankIcon = DirectFrame(
                parent=row,
                relief=None,
                image=icon,
                image_scale=(63.0 / 73.0, 1, 1),
                pos=(-0.158, 0, 0.001),
                scale=0.024,
            )
            rankIcon.setTransparency(TransparencyAttrib.MAlpha)

        DirectLabel(
            parent=row,
            relief=None,
            text=toonName,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.0265,
            text_align=TextNode.ALeft,
            text_pos=(-0.133, -0.004),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(0, 0, 0.012),
        )
        DirectLabel(
            parent=row,
            relief=None,
            text=('%s  -  You' % rankName) if isLocal else rankName,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.0195,
            text_align=TextNode.ALeft,
            text_pos=(-0.133, -0.006),
            text_fg=(0.72, 0.80, 0.92, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(0, 0, -0.017),
        )
        DirectLabel(
            parent=row,
            relief=None,
            text='Online' if online else 'Offline',
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.0205,
            text_align=TextNode.ARight,
            text_pos=(0.189, -0.007),
            text_fg=((0.48, 1.0, 0.56, 1) if online else
                     (0.64, 0.67, 0.75, 1)),
            text_shadow=(0, 0, 0, 1),
            pos=(0, 0, 0.001),
        )
        return yPos - 0.070

    def _showMembers(self):
        members = list(self.manager.getMembers())
        members.sort(
            key=lambda member: (
                -int(self._memberIsOnline(member)),
                -int(member.get('rank', 0)),
                str(member.get('name', '')).lower(),
            )
        )
        self._pageTitle('Club Members (%s/%s)' % (
            len(members), ClubGlobals.CLUB_MAX_MEMBERS))

        onlineMembers = []
        offlineMembers = []
        for member in members:
            if self._memberIsOnline(member):
                onlineMembers.append(member)
            else:
                offlineMembers.append(member)

        self.membersScroll = self._add(DirectScrolledFrame(
            parent=self,
            relief=None,
            pos=(0.002, 0, 0),
            frameSize=(-0.233, 0.233, -0.349, 0.329),
            canvasSize=(-0.225, 0.183, -0.349, 0.309),
            frameColor=(0, 0, 0, 0),
            scrollBarWidth=0.05,
            manageScrollBars=0,
            autoHideScrollBars=0,

            verticalScroll_relief=None,
            verticalScroll_pos=(0.208, 0, 0),
            verticalScroll_frameSize=(-0.025, 0.025, -0.346, 0.329),
            verticalScroll_manageButtons=0,
            verticalScroll_resizeThumb=0,
            verticalScroll_image=sp_gui.find('**/ScrollBar_BAR'),
            verticalScroll_image_scale=(0.057, 1.0, 0.678),
            verticalScroll_image_pos=(0.0, 0.0, -0.010),

            verticalScroll_thumb_relief=None,
            verticalScroll_thumb_frameColor=(1, 1, 1, 0),
            verticalScroll_thumb_frameSize=(-0.025, 0.025, -0.059, 0.118),
            verticalScroll_thumb_image=sp_gui.find('**/ScrollBar'),
            verticalScroll_thumb_image_scale=(0.053, 1.0, 0.181),
            verticalScroll_thumb_image_pos=(0.0, 0.0, 0.029),
        ))
        self.membersScroll.setTransparency(TransparencyAttrib.MAlpha)
        self.membersScroll.horizontalScroll.hide()
        self.membersScroll.verticalScroll.incButton.hide()
        self.membersScroll.verticalScroll.decButton.hide()
        self.membersScroll.verticalScroll.setValue(0)
        canvas = self.membersScroll.getCanvas()

        yPos = 0.286
        rowIndex = 0
        if onlineMembers:
            yPos = self._makeMembersSectionHeader(
                canvas, 'ONLINE', len(onlineMembers), yPos, True)
            for member in onlineMembers:
                yPos = self._makeClubMemberRow(
                    canvas, member, rowIndex, yPos)
                rowIndex += 1

        if offlineMembers:
            if onlineMembers:
                yPos -= 0.010
            yPos = self._makeMembersSectionHeader(
                canvas, 'OFFLINE', len(offlineMembers), yPos, False)
            for member in offlineMembers:
                yPos = self._makeClubMemberRow(
                    canvas, member, rowIndex, yPos)
                rowIndex += 1

        if not members:
            DirectLabel(
                parent=canvas,
                relief=None,
                text='No Club members were found.',
                text_font=ToontownGlobals.getInterfaceFont(),
                text_scale=0.028,
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                pos=(-0.010, 0, 0.10),
            )

        canvasBottom = min(-0.350, yPos - 0.025)
        self.membersScroll['canvasSize'] = (
            -0.225, 0.183, canvasBottom, 0.309)
        if canvasBottom < -0.360:
            self.accept('wheel_up', self._scrollClubMembers, [-1])
            self.accept('wheel_down', self._scrollClubMembers, [1])

    def _clearMemberActions(self):
        for obj in self.memberActionObjects:
            try:
                obj.destroy()
            except:
                try:
                    obj.removeNode()
                except:
                    pass
        self.memberActionObjects = []

    def _addMemberAction(self, obj):
        self.memberActionObjects.append(obj)
        self.pageObjects.append(obj)
        return obj

    def _selectMember(self, member):
        self.selectedMember = member
        self._clearMemberActions()

        avId = int(member.get('avId', 0))
        name = str(member.get('name', 'Toon'))
        if avId == base.localAvatar.doId:
            self._addMemberAction(DirectLabel(
                parent=self,
                relief=DGG.FLAT,
                frameSize=(-0.199, 0.199, -0.024, 0.024),
                frameColor=(0.055, 0.066, 0.096, 0.96),
                text='%s is your Toon.' % name,
                text_font=ToontownGlobals.getInterfaceFont(),
                text_scale=0.021,
                text_pos=(0, -0.007),
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                pos=(-0.021, 0, -0.318),
            ))
            return

        self._addMemberAction(DirectLabel(
            parent=self,
            relief=DGG.FLAT,
            frameSize=(-0.199, 0.199, -0.022, 0.022),
            frameColor=(0.055, 0.066, 0.096, 0.96),
            text='Selected: %s' % name,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.021,
            text_pos=(0, -0.007),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(-0.021, 0, -0.260),
        ))

        if self.manager.localAvHasPermission(ClubGlobals.PERMISSION_RANK):
            self._addMemberAction(self._makeSmallButton(
                'Member', (-0.145, 0, -0.302), self.manager.requestSetRank,
                [avId, ClubGlobals.RANK_MEMBER], scale=0.88))
            self._addMemberAction(self._makeSmallButton(
                'Officer', (0, 0, -0.302), self.manager.requestSetRank,
                [avId, ClubGlobals.RANK_OFFICER], scale=0.88))
            self._addMemberAction(self._makeSmallButton(
                'Deputy', (0.145, 0, -0.302), self.manager.requestSetRank,
                [avId, ClubGlobals.RANK_DEPUTY], scale=0.88))

        if self.manager.localAvHasPermission(ClubGlobals.PERMISSION_KICK):
            self._addMemberAction(self._makeSmallButton(
                'Remove', (-0.075, 0, -0.343), self.manager.requestKick,
                [avId], frameColor=(0.72, 0.22, 0.22, 0.95), scale=0.88))

        if self.manager.localAvIsOwner():
            self._addMemberAction(self._makeSmallButton(
                'Transfer Leader', (0.095, 0, -0.343),
                self.manager.requestTransferOwner, [avId],
                frameColor=(0.70, 0.48, 0.15, 0.95), scale=0.88))

    # ------------------------------------------------------------------
    # Logs page
    # ------------------------------------------------------------------
    def _showLogs(self):
        self._pageTitle('Club History')
        self._add(DirectLabel(
            parent=self,
            relief=None,
            text='Loading...',
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.027,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(0, 0, 0.10),
        ))
        self.manager.requestLogs(0)

    def _scrollClubLogs(self, direction):
        if self.logsScroll is None:
            return
        try:
            scrollBar = self.logsScroll.verticalScroll
            try:
                value = float(scrollBar.getValue())
            except:
                value = float(scrollBar['value'])
            value += float(direction) * 0.12
            value = max(0.0, min(1.0, value))
            scrollBar.setValue(value)
        except:
            pass

    def _logsUpdated(self, logs):
        if self.page != 'logs':
            return
        self._clearPage()
        self._pageTitle('Club History')

        if not logs:
            self._add(DirectLabel(
                parent=self,
                relief=None,
                text='No Club history yet.',
                text_font=ToontownGlobals.getInterfaceFont(),
                text_scale=0.028,
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                pos=(0, 0, 0.10),
            ))
            return

        # The old History page used one fixed-height label per entry. Wrapped
        # messages therefore overlapped and long text continued outside the
        # panel. Use a clipped vertical list with row heights based on the
        # actual number of wrapped lines instead.
        self.logsScroll = self._add(DirectScrolledFrame(
            parent=self,
            relief=None,
            pos=(0.002, 0, 0),
            frameSize=(-0.233, 0.233, -0.349, 0.329),
            canvasSize=(-0.225, 0.183, -0.349, 0.309),
            frameColor=(0, 0, 0, 0),
            scrollBarWidth=0.05,
            manageScrollBars=0,
            autoHideScrollBars=0,

            verticalScroll_relief=None,
            verticalScroll_pos=(0.208, 0, 0),
            verticalScroll_frameSize=(-0.025, 0.025, -0.346, 0.329),
            verticalScroll_manageButtons=0,
            verticalScroll_resizeThumb=0,
            verticalScroll_image=sp_gui.find('**/ScrollBar_BAR'),
            verticalScroll_image_scale=(0.057, 1.0, 0.678),
            verticalScroll_image_pos=(0.0, 0.0, -0.010),

            verticalScroll_thumb_relief=None,
            verticalScroll_thumb_frameColor=(1, 1, 1, 0),
            verticalScroll_thumb_frameSize=(-0.025, 0.025, -0.059, 0.118),
            verticalScroll_thumb_image=sp_gui.find('**/ScrollBar'),
            verticalScroll_thumb_image_scale=(0.053, 1.0, 0.181),
            verticalScroll_thumb_image_pos=(0.0, 0.0, 0.029),
        ))
        self.logsScroll.setTransparency(TransparencyAttrib.MAlpha)
        self.logsScroll.horizontalScroll.hide()
        self.logsScroll.verticalScroll.incButton.hide()
        self.logsScroll.verticalScroll.decButton.hide()
        self.logsScroll.verticalScroll.setValue(0)
        canvas = self.logsScroll.getCanvas()

        yTop = 0.292
        for index, log in enumerate(logs):
            message = str(log.get('message', '') or '')
            wrappedLines = textwrap.wrap(
                message,
                width=39,
                break_long_words=False,
                break_on_hyphens=False,
            ) or ['']
            wrappedMessage = '\n'.join(wrappedLines)
            lineCount = len(wrappedLines)
            rowHeight = 0.031 + (lineCount * 0.027)
            rowCenter = yTop - (rowHeight * 0.5)

            DirectFrame(
                parent=canvas,
                relief=DGG.FLAT,
                frameSize=(-0.214, 0.184, -rowHeight * 0.5,
                           rowHeight * 0.5),
                frameColor=(0.020, 0.024, 0.040,
                            0.72 if index % 2 == 0 else 0.50),
                pos=(-0.010, 0, rowCenter),
            )
            DirectLabel(
                parent=canvas,
                relief=None,
                text=wrappedMessage,
                text_font=ToontownGlobals.getInterfaceFont(),
                text_scale=0.0205,
                text_align=TextNode.ALeft,
                text_pos=(-0.198, -0.020),
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                pos=(0, 0, yTop),
            )
            yTop -= rowHeight + 0.008

        canvasBottom = min(-0.350, yTop - 0.025)
        self.logsScroll['canvasSize'] = (
            -0.225, 0.183, canvasBottom, 0.309)

        if canvasBottom < -0.360:
            self.accept('wheel_up', self._scrollClubLogs, [-1])
            self.accept('wheel_down', self._scrollClubLogs, [1])

    # ------------------------------------------------------------------
    # Settings page
    # ------------------------------------------------------------------
    def _showSettings(self):
        self._pageTitle('Club Settings')

        # Corporate Clash's settings page is a compact, transparent scrolling
        # list. The Social Panel/content-pack artwork remains visible behind it.
        self.settingsScroll = self._add(DirectScrolledFrame(
            parent=self,
            relief=None,
            pos=(0.002, 0, 0),
            frameSize=(-0.233, 0.233, -0.349, 0.329),
            canvasSize=(-0.233, 0.183, -1.72, 0.329),
            frameColor=(0, 0, 0, 0),
            scrollBarWidth=0.05,
            manageScrollBars=0,
            autoHideScrollBars=0,

            # These are Corporate Clash's exact Club Settings scrollbar
            # dimensions.  The scrollbar is manually positioned so Panda's
            # automatic scroll-piece manager cannot move the thumb outside
            # the authored track.
            verticalScroll_relief=None,
            verticalScroll_pos=(0.208, 0, 0),
            verticalScroll_frameSize=(-0.025, 0.025, -0.346, 0.329),
            verticalScroll_manageButtons=0,
            verticalScroll_resizeThumb=0,
            verticalScroll_image=sp_gui.find('**/ScrollBar_BAR'),
            # The authored track model is one unit tall. Scale and center it to
            # the authored scrollbar track bounds. The thumb lower travel limit is
            # is set halfway between the previous two tested positions.
            verticalScroll_image_scale=(0.057, 1.0, 0.678),
            verticalScroll_image_pos=(0.0, 0.0, -0.010),

            verticalScroll_thumb_relief=None,
            verticalScroll_thumb_frameColor=(1, 1, 1, 0),
            verticalScroll_thumb_frameSize=(-0.025, 0.025, -0.059, 0.118),
            verticalScroll_thumb_image=sp_gui.find('**/ScrollBar'),
            verticalScroll_thumb_image_scale=(0.053, 1.0, 0.181),
            verticalScroll_thumb_image_pos=(0.0, 0.0, 0.029),
        ))
        self.settingsScroll.setTransparency(TransparencyAttrib.MAlpha)
        self.settingsScroll.horizontalScroll.hide()
        self.settingsScroll.verticalScroll.incButton.hide()
        self.settingsScroll.verticalScroll.decButton.hide()
        self.settingsScroll.verticalScroll.setValue(0)
        canvas = self.settingsScroll.getCanvas()

        yPos = 0.270
        yPos = self._settingsSection(canvas, 'Personal', yPos)
        yPos -= 0.008
        for settingKey in ClubGlobals.PERSONAL_SETTING_KEYS:
            yPos = self._settingsCheckbox(
                canvas,
                ClubGlobals.PERSONAL_SETTING_LABELS.get(settingKey, settingKey),
                self.manager.getPersonalSetting(settingKey),
                yPos,
                self._togglePersonalSetting,
                [settingKey],
                enabled=True,
                xOffset=0.008,
                zOffset=0.012,
            )

        owner = self.manager.localAvIsOwner()
        if owner:
            yPos -= 0.020
            yPos = self._settingsSection(canvas, 'Permissions', yPos)
            yPos -= 0.006

            rankOrder = (
                (ClubGlobals.RANK_DEPUTY, 'Star_Silver'),
                (ClubGlobals.RANK_OFFICER, 'Star_Bronze'),
                (ClubGlobals.RANK_MEMBER, None),
            )
            for rank, iconName in rankOrder:
                yPos = self._settingsRankSection(
                    canvas,
                    ClubGlobals.SETTINGS_RANK_NAMES.get(rank, 'Members'),
                    yPos,
                    iconName,
                )
                yPos -= 0.007
                for permission in ClubGlobals.EDITABLE_PERMISSION_KEYS:
                    yPos = self._settingsCheckbox(
                        canvas,
                        ClubGlobals.PERMISSION_LABELS.get(permission, permission),
                        self.manager.getRankPermission(rank, permission),
                        yPos,
                        self._toggleRankPermission,
                        [rank, permission],
                        enabled=True,
                        xOffset=0.008,
                        zOffset=0.012,
                    )
                yPos -= 0.020
        else:
            # Corporate Clash only exposes the rank-permission editor to the
            # Club owner. Captains, Scouts and Members keep the Personal
            # settings and the Leave Club action, without empty/disabled rows.
            yPos -= 0.028

        redImages = self._buttonImages('RedButton')
        leaveY = yPos - 0.060
        if redImages is not None:
            DirectButton(
                parent=canvas,
                relief=None,
                pos=(-0.010, 0, leaveY),
                scale=0.07138,
                image=redImages,
                image_scale=(164.0 / 63.0, 1, 1),
                text='Leave Club',
                text_pos=(-0.02107, -0.13006),
                text_scale=(0.38469, 0.38469),
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                command=self._attemptLeaveClub,
                pressEffect=0,
            )
        else:
            DirectButton(
                parent=canvas,
                relief=DGG.RAISED,
                borderWidth=(0.006, 0.006),
                frameSize=(-0.095, 0.095, -0.028, 0.030),
                frameColor=(0.72, 0.22, 0.22, 0.95),
                pos=(-0.010, 0, leaveY),
                text='Leave Club',
                text_font=ToontownGlobals.getInterfaceFont(),
                text_scale=0.024,
                text_pos=(0, -0.008),
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                command=self._attemptLeaveClub,
            )

        # Fit the canvas to the actual contents so the thumb size and bottom
        # position match the real Clash page rather than leaving blank space.
        self.settingsScroll['canvasSize'] = (-0.225, 0.205, leaveY - 0.090, 0.300)

    def _settingsSection(self, parent, text, yPos):
        DirectFrame(
            parent=parent,
            relief=DGG.FLAT,
            frameSize=(-0.222, 0.202, -0.030, 0.030),
            frameColor=(0.212, 0.224, 0.247, 0.25),
            text=text,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.040,
            text_pos=(-0.010, -0.014),
            text_align=TextNode.ACenter,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(0, 0, yPos),
        )
        return yPos - 0.060

    def _settingsRankSection(self, parent, text, yPos, iconName=None):
        DirectFrame(
            parent=parent,
            relief=DGG.FLAT,
            frameSize=(-0.222, 0.202, -0.030, 0.030),
            frameColor=(0.212, 0.224, 0.247, 0.25),
            text=text,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.040,
            text_pos=(-0.010, -0.014),
            text_align=TextNode.ACenter,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(0, 0, yPos),
        )
        if iconName:
            icon = self._findNode(iconName)
            if icon is not None:
                for xPos in (-0.105, 0.085):
                    star = DirectFrame(
                        parent=parent,
                        relief=None,
                        image=icon,
                        image_scale=(63.0 / 73.0, 1, 1),
                        pos=(xPos, 0, yPos - 0.002),
                        scale=0.030,
                    )
                    star.setTransparency(TransparencyAttrib.MAlpha)
        return yPos - 0.060

    def _settingsCheckbox(self, parent, label, checked, yPos, command,
                          extraArgs=None, enabled=True, xOffset=0.0,
                          zOffset=0.0):
        if extraArgs is None:
            extraArgs = []

        unchecked = self._findNode('WhiteCircle')
        checkedImage = self._findNode('WhiteCheck')
        image = checkedImage if checked and checkedImage is not None else unchecked

        if image is not None:
            button = DirectButton(
                parent=parent,
                relief=None,
                pos=(-0.211 + xOffset, 0, yPos - 0.018 + zOffset),
                scale=0.03099,
                image=(image, image, image, image),
                image_scale=(97.0 / 86.0, 1.0, 1.0),
                image_color=(1, 1, 1, 1 if enabled else 0.45),
                command=command if enabled else None,
                extraArgs=extraArgs,
                pressEffect=0,
            )
            button.setTransparency(TransparencyAttrib.MAlpha)
            if not enabled:
                button['state'] = DGG.DISABLED
        else:
            DirectButton(
                parent=parent,
                relief=DGG.RAISED,
                frameSize=(-0.014, 0.014, -0.014, 0.014),
                frameColor=((0.3, 0.8, 0.3, 1) if checked else (0.35, 0.35, 0.35, 1)),
                pos=(-0.211 + xOffset, 0, yPos - 0.018 + zOffset),
                text='X' if checked else '',
                text_scale=0.020,
                command=command if enabled else None,
                extraArgs=extraArgs,
            )

        DirectLabel(
            parent=parent,
            relief=None,
            text=label,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.027,
            text_pos=(-0.191, -0.027),
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1 if enabled else 0.55),
            text_shadow=(0, 0, 0, 1 if enabled else 0.45),
            pos=(xOffset, 0, yPos + zOffset),
        )
        return yPos - 0.03738

    def _togglePersonalSetting(self, settingKey):
        current = self.manager.getPersonalSetting(settingKey)
        self.manager.setPersonalSetting(settingKey, not current)
        self.showPage('settings')

    def _toggleRankPermission(self, rank, permission):
        if not self.manager.localAvIsOwner():
            return
        current = self.manager.getRankPermission(rank, permission)
        self.manager.requestSetPermission(rank, permission, not current)

    def _attemptLeaveClub(self):
        members = self.manager.getMembers()
        if self.manager.localAvIsOwner() and len(members) > 1:
            try:
                base.localAvatar.setSystemMessage(
                    0, 'Transfer Club ownership before leaving the Club.')
            except:
                pass
            return
        try:
            from toontown.toontowngui import TTDialog
            self.leaveDialog = TTDialog.TTGlobalDialog(
                doneEvent='clubLeaveDialogDone',
                message='Are you sure you want to leave your Club?',
                style=TTDialog.TwoChoice)
            self.leaveDialog.show()
            self.acceptOnce('clubLeaveDialogDone', self._leaveDialogDone)
        except:
            self.manager.requestLeave()

    def _leaveDialogDone(self):
        try:
            status = self.leaveDialog.doneStatus
        except:
            status = None
        try:
            self.leaveDialog.cleanup()
            del self.leaveDialog
        except:
            pass
        if status == 'ok':
            self.manager.requestLeave()

    # ------------------------------------------------------------------
    # Club events / cleanup
    # ------------------------------------------------------------------
    def _stateUpdated(self, club):
        self.showPage(self.page)

    def _notification(self, notifyType, message):
        chatLog = getattr(base.cr, 'chatLog', None)
        if chatLog is not None:
            try:
                chatLog.addToLog(
                    '\1orangeText\1Club Update\2: %s' % message,
                    category=chatLog.TAB_CLUBS,
                )
            except:
                pass

    def destroy(self):
        if self.donationGui is not None:
            try:
                self.donationGui.destroy()
            except:
                pass
            self.donationGui = None
        self.ignoreAll()
        self._clearPage()
        for button in self.navButtons:
            try:
                button.destroy()
            except:
                pass
        self.navButtons = []
        for modelName in ('_mainJarGui', '_mainClubShopGui', '_clubTaskGui',
                          '_clubTaskCogGui', '_clubTaskSosGui',
                          '_clubBoosterGui', '_clubRerollGui',
                          '_clubTaskDiceGui'):
            model = getattr(self, modelName, None)
            if model is not None:
                try:
                    model.removeNode()
                except:
                    pass
                setattr(self, modelName, None)
        DirectFrame.destroy(self)
