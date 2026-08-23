from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel
from pandac.PandaModules import TextNode, Vec4

from toontown.groups import GroupGlobals
from toontown.hood import ZoneUtil
from toontown.toon.socialpanel.SocialPanelGUI import SelectorButton
from toontown.toon.socialpanel.SocialPanelGlobals import sp_gui
from toontown.toon.socialpanel.groups.SocialPanelGroupBrowser import SocialPanelGroupBrowser
from toontown.toon.socialpanel.groups.SocialPanelGroupQuickInvite import SocialPanelGroupQuickInvite
from toontown.toon.socialpanel.groups.SocialPanelGroupViewer import SocialPanelGroupViewer
from toontown.toonbase import TTLocalizer, ToontownGlobals


class SocialPanelGroupsTab(DirectFrame):
    def __init__(self, parent):
        DirectFrame.__init__(self, parent=parent, relief=None)
        self.initialiseoptions(SocialPanelGroupsTab)
        self.panel = parent
        self.mgr = getattr(base.cr, 'groupManager', None)
        if self.mgr is None:
            self.mgr = getattr(base.cr, 'groupMgr', None)
        self.page = 'browse'
        self.groupToView = None
        self.browseObjects = []
        self.createObjects = []
        self.viewObjects = []
        self.invitePanel = None
        self.filterMode = False
        self.pendingCreateInvites = []
        self.load()
        self.accept('group-tracker-state', self._stateUpdated)
        self.accept('group-tracker-joined', self._joinedGroup)
        self.accept('group-tracker-left', self._leftGroup)
        self.accept('group-tracker-browse', self._browseUpdated)
        self.accept('social-panel-groups-view', self.showView)
        self.accept('social-panel-groups-browse', self.showBrowse)
        self.accept('social-panel-groups-invite', self.showInvitePanel)
        self.accept('zoneChange', self._zoneChanged)
        self.reload()

    def destroy(self):
        self.ignoreAll()
        if self.invitePanel:
            self.invitePanel.destroy()
            self.invitePanel = None
        self.panel = None
        self.mgr = None
        DirectFrame.destroy(self)

    def load(self):
        self.scroll_groupList = SocialPanelGroupBrowser(self, self.mgr)
        self.button_groupCreate = DirectButton(
            parent=self, frameColor=(0.796, 0.702, 0.078, 1), relief=None,
            pos=(-0.127, 0, 0.4348), text='Create', text_align=TextNode.ACenter,
            text_scale=0.04, text_pos=(0.024, -0.011), text_fg=Vec4(1, 1, 1, 1),
            text_shadow=Vec4(0, 0, 0, 1), command=self.handleCreate,
            geom=(sp_gui.find('**/GroupAdd_N'), sp_gui.find('**/GroupAdd_P'), sp_gui.find('**/GroupAdd_H')),
            geom_scale=(0.08 * (221.0 / 84.0), 1, 0.08))
        self.button_groupFilter = DirectButton(
            parent=self, frameColor=(0.796, 0.702, 0.078, 1), relief=None,
            pos=(0.083, 0, 0.4348), text='Filter', text_align=TextNode.ACenter,
            text_scale=0.04, text_pos=(0.024, -0.011), text_fg=Vec4(1, 1, 1, 1),
            text_shadow=Vec4(0, 0, 0, 1), command=self.handleFilter,
            geom=(sp_gui.find('**/GroupSearch_N'), sp_gui.find('**/GroupSearch_P'), sp_gui.find('**/GroupSearch_H')),
            geom_scale=(0.08 * (221.0 / 84.0), 1, 0.08))
        self.button_groupInfo = DirectButton(
            parent=self, relief=None, pos=(0.2101, 0, 0.4348),
            geom=(sp_gui.find('**/Question_N'), sp_gui.find('**/Question_P'), sp_gui.find('**/Question_H')),
            geom_scale=(0.1 * (40.0 / 84.0), 1, 0.08), command=self.handleInfo)
        self.browseObjects = [self.scroll_groupList, self.button_groupCreate, self.button_groupFilter, self.button_groupInfo]

        top = 0.3828
        bottom = -0.09
        step = (bottom - top) / 3.0
        self.selectorButton_groupType = SelectorButton(
            parent=self, pos=(0, 0, top), width=0.6, title='Group Type', callback=self.updateGroupType)
        self.selectorButton_condition = SelectorButton(
            parent=self, pos=(0, 0, top + step), width=0.6, title='Condition', disabled=True)
        self.selectorButton_location = SelectorButton(
            parent=self, pos=(0, 0, bottom - step), width=0.6, title='Location', disabled=True)
        self.selectorButton_groupSize = SelectorButton(
            parent=self, pos=(-0.124, 0, bottom), width=0.20, title='Group Size', callback=self.updateCapacityText)
        self.selectorButton_privacy = SelectorButton(
            parent=self, pos=(0.124, 0, bottom), width=0.20, title='Privacy')
        self.selectorButton_privacy.titleText['text_pos'] = (-0.03, 0.086)
        self.button_groupPrivacyInfo = DirectButton(
            parent=self, relief=None, pos=(0.1921, 0, -0.02811), scale=0.6254,
            geom=(sp_gui.find('**/Question_N'), sp_gui.find('**/Question_P'), sp_gui.find('**/Question_H')),
            geom_scale=(0.047, 1, 0.0782), command=self.handleInfo)
        self.text_groupCapacity = DirectFrame(
            parent=self, relief=None, pos=(0, 0, -0.20262),
            text='1/4 Toons', text_scale=0.04,
            text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1))
        self.button_toggleInvitePanel = DirectButton(
            parent=self, pos=(0.00151, 0, -0.26443), relief=None,
            text='Invite Toons', text_pos=(0, -0.01), scale=0.8,
            geom=(sp_gui.find('**/OrangeButton_N'), sp_gui.find('**/OrangeButton_P'), sp_gui.find('**/OrangeButton_H')),
            geom_scale=(0.09 * (164.0 / 63.0), 1, 0.09), geom_color=(0.9, 0.9, 0.9, 1),
            text_scale=0.039, command=self.toggleInvitePanel,
            text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1))
        self.button_completeGroup = DirectButton(
            parent=self, pos=(-0.1149, 0, -0.38484), relief=None,
            text='Create', text_pos=(0, -0.01),
            geom=(sp_gui.find('**/OrangeButton_N'), sp_gui.find('**/OrangeButton_P'), sp_gui.find('**/OrangeButton_H')),
            geom_scale=(0.09 * (164.0 / 63.0), 1, 0.09), geom_color=(0.9, 0.9, 0.9, 1),
            text_scale=0.039, command=self.createGroup,
            text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1))
        self.button_cancelGroup = DirectButton(
            parent=self, pos=(0.11779, 0, -0.38484), relief=None,
            text='Cancel', text_pos=(0, -0.01),
            geom=(sp_gui.find('**/RedButton_N'), sp_gui.find('**/RedButton_P'), sp_gui.find('**/RedButton_H')),
            geom_scale=(0.23325, 1, 0.09), geom_color=(0.9, 0.9, 0.9, 1),
            text_scale=0.039, command=self.showBrowse,
            text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1))
        self.createObjects = [
            self.selectorButton_groupType, self.selectorButton_condition,
            self.selectorButton_location, self.selectorButton_groupSize,
            self.selectorButton_privacy, self.button_groupPrivacyInfo,
            self.text_groupCapacity, self.button_toggleInvitePanel,
            self.button_completeGroup, self.button_cancelGroup]

        self.socialPanelGroupsView = SocialPanelGroupViewer(self, self.mgr)
        self.viewObjects = [self.socialPanelGroupsView]
        self.invitePanel = SocialPanelGroupQuickInvite(self, createMode=True)
        self.invitePanel.hide()
        self.invitePanelOpen = False
        self._hideAll()

    def _hideAll(self):
        for obj in self.browseObjects + self.createObjects + self.viewObjects:
            obj.hide()
        if self.invitePanel:
            self.invitePanel.hide()

    def reload(self, *args):
        if self.mgr is None:
            self.mgr = getattr(base.cr, 'groupManager', None) or getattr(base.cr, 'groupMgr', None)
        if self.mgr is None:
            return
        self.mgr.requestState()
        self.mgr.requestBrowse()
        if self.mgr.group:
            self.showView(self.mgr.group)
        else:
            self.showBrowse()

    def showBrowse(self, *args):
        self.page = 'browse'
        self._hideAll()
        for obj in self.browseObjects:
            obj.show()
        if self.mgr and self.mgr.group:
            self.button_groupCreate['text'] = 'View'
            self.button_groupCreate['geom'] = (
                sp_gui.find('**/GroupView_N'), sp_gui.find('**/GroupView_P'), sp_gui.find('**/GroupView_H'))
        else:
            self.button_groupCreate['text'] = 'Create'
            self.button_groupCreate['geom'] = (
                sp_gui.find('**/GroupAdd_N'), sp_gui.find('**/GroupAdd_P'), sp_gui.find('**/GroupAdd_H'))
        self.scroll_groupList.refresh()

    def showCreate(self):
        self.page = 'create'
        self._hideAll()
        for obj in self.createObjects:
            obj.show()
        self.invitePanelOpen = False
        self.invitePanel.createMode = True
        self.invitePanel.hide()
        self._refreshCreateOptions()

    def showView(self, group=None):
        if group is None:
            group = self.mgr.group
        if not group:
            self.showBrowse()
            return
        self.page = 'view'
        self.groupToView = group
        self._hideAll()
        for obj in self.viewObjects:
            obj.show()
        self.socialPanelGroupsView.updateGroup(group)

    def handleCreate(self):
        if self.mgr.group:
            self.showView(self.mgr.group)
        else:
            self.showCreate()

    def handleFilter(self):
        self.scroll_groupList.switchFilterStatus()

    def handleInfo(self):
        try:
            base.localAvatar.setSystemMessage(0, 'Create or join Groups for activities across Toontown.')
        except:
            pass

    def _refreshCreateOptions(self):
        activities = self._getAvailableActivities()
        if not activities:
            self.showBrowse()
            return
        self.selectorButton_groupType.setOptions(activities, activities, setIndex=0)
        self.selectorButton_condition.setOptions(values=[None], texts=[''], setIndex=0)
        self.selectorButton_location.setOptions(values=[None], texts=[self._getLocationLabel()], setIndex=0)
        self.selectorButton_privacy.setOptions(values=[True, False], texts=['Public', 'Private'], setIndex=0, wraparound=True)
        self.updateGroupType(self.selectorButton_groupType.getChoice())
        if self.invitePanel:
            self.invitePanel.selected = {}
        self.updateCapacityText()

    def _getAvailableActivities(self):
        activities = list(GroupGlobals.ACTIVITY_NAMES)
        if not self._isInPlayground():
            activities = [activity for activity in activities if activity not in ('Trolley', 'Fishing')]
        return activities

    def _isInPlayground(self):
        try:
            return ZoneUtil.getWhereName(self._getZoneId(), True) == 'playground'
        except:
            return False

    def updateGroupType(self, activity):
        options = self._capacityOptions(activity)
        texts = [str(value) for value in options]
        self.selectorButton_groupSize.setOptions(values=options, texts=texts, setIndex=len(options) - 1)
        zoneId, location = self._getActivityDestination(activity)
        self.selectorButton_location.setOptions(values=[zoneId], texts=[location], setIndex=0)
        self.updateCapacityText()

    def _capacityOptions(self, activity):
        maxSize = int(GroupGlobals.ACTIVITY_SIZES.get(activity, 4))
        if maxSize >= 8:
            return [2, 4, 6, 8]
        if maxSize == 6:
            return [2, 4, 6]
        if maxSize == 4:
            return [4]
        return [maxSize]

    def getSelectedCapacity(self):
        choice = self.selectorButton_groupSize.getChoice()
        try:
            return int(choice)
        except:
            return 4

    def updateCapacityText(self, *args):
        cap = self.getSelectedCapacity()
        invited = []
        if self.invitePanel:
            invited = self.invitePanel.getInvitedAvIds()[:max(0, cap - 1)]
        self.text_groupCapacity['text'] = '%s/%s Toons' % (len(invited) + 1, cap)

    def createGroup(self):
        activity = self.selectorButton_groupType.getChoice()
        zoneId, location = self._getActivityDestination(activity)
        size = self.getSelectedCapacity()
        published = bool(self.selectorButton_privacy.getChoice())
        self.pendingCreateInvites = []
        if self.invitePanel:
            self.pendingCreateInvites = self.invitePanel.getInvitedAvIds()[:max(0, size - 1)]
        self.mgr.requestCreate(activity, location, zoneId, size, published)
        self.invitePanelOpen = False
        self.invitePanel.hide()

    def toggleInvitePanel(self):
        if self.page != 'create':
            self.showInvitePanel()
            return
        if self.invitePanelOpen:
            self.closeCreateInvitePanel()
        else:
            self.openCreateInvitePanel()

    def showInvitePanel(self):
        if self.page == 'create':
            self.openCreateInvitePanel()
            return
        if self.page == 'view' and self.mgr.group:
            self._showGroupInviteList()

    def openCreateInvitePanel(self):
        if self.page != 'create':
            return
        self.invitePanelOpen = True
        self.invitePanel.createMode = True
        self.invitePanel.show()
        for obj in [self.selectorButton_groupType, self.selectorButton_condition,
                    self.selectorButton_location, self.selectorButton_groupSize,
                    self.selectorButton_privacy]:
            try:
                obj.setButtonState(False)
            except:
                pass
        try:
            self.button_groupPrivacyInfo['state'] = 'disabled'
        except:
            pass

    def closeCreateInvitePanel(self):
        self.invitePanelOpen = False
        self.invitePanel.hide()
        for obj in [self.selectorButton_groupType, self.selectorButton_condition,
                    self.selectorButton_location, self.selectorButton_groupSize,
                    self.selectorButton_privacy]:
            try:
                obj.updateButtons()
            except:
                try:
                    obj.setButtonState(True)
                except:
                    pass
        try:
            self.button_groupPrivacyInfo['state'] = 'normal'
        except:
            pass
        self.updateCapacityText()

    def _showGroupInviteList(self):
        self.page = 'group-invite'
        self._hideAll()
        self.invitePanel.createMode = False
        self.invitePanel.selected = {}
        self.invitePanel.setBackCommand(self._backFromGroupInvite)
        self.invitePanel.show()

    def _backFromGroupInvite(self):
        selected = self.invitePanel.getInvitedAvIds()
        candidates = dict(self._candidateToons())
        for avId in selected:
            self.mgr.requestInvite(avId, candidates.get(avId, ''))
        self.invitePanel.setBackCommand(None)
        self.showView(self.mgr.group)

    def _candidateToons(self):
        entries = {}
        try:
            toonDClass = base.cr.dclassesByName.get('DistributedToon')
        except:
            toonDClass = None
        try:
            for avId, obj in list(base.cr.doId2do.items()):
                if int(avId) == int(base.localAvatar.doId) or not hasattr(obj, 'getName'):
                    continue
                isToon = False
                try:
                    isToon = obj.dclass == toonDClass
                except:
                    pass
                if not isToon:
                    className = obj.__class__.__name__
                    isToon = className == 'DistributedToon' or className.endswith('Toon')
                if isToon and not getattr(obj, 'ghostMode', 0):
                    entries[int(avId)] = str(obj.getName())
        except:
            pass
        for friend in getattr(base.localAvatar, 'friendsList', []):
            try:
                avId = int(friend[0])
            except:
                continue
            if avId == int(base.localAvatar.doId):
                continue
            try:
                if not base.cr.isFriendOnline(avId):
                    continue
            except:
                pass
            try:
                handle = base.cr.identifyFriend(avId)
            except:
                handle = None
            if handle is not None and hasattr(handle, 'getName'):
                entries.setdefault(avId, str(handle.getName()))
        group = getattr(self.mgr, 'group', None) or {}
        memberIds = set(int(member.get('avId', 0)) for member in group.get('members', []))
        return [(avId, name) for avId, name in list(entries.items()) if avId not in memberIds]

    def _stateUpdated(self, group):
        if group and self.pendingCreateInvites:
            candidates = dict(self._candidateToons())
            pending = self.pendingCreateInvites[:]
            self.pendingCreateInvites = []
            for avId in pending:
                self.mgr.requestInvite(avId, candidates.get(avId, ''))
            self.showView(group)
            return
        if self.page == 'create' and group:
            self.showView(group)
        elif self.page == 'view' and group:
            self.groupToView = group
            self.socialPanelGroupsView.updateGroup(group)
        elif self.page == 'view' and not group:
            self.showBrowse()
        elif self.page == 'browse':
            self.showBrowse()

    def _joinedGroup(self, group):
        if group:
            self.showView(group)

    def _leftGroup(self, *args):
        self.pendingCreateInvites = []
        self.groupToView = None
        self.showBrowse()

    def _browseUpdated(self, groups):
        if self.page == 'browse':
            self.scroll_groupList.refresh()

    def _zoneChanged(self, *args):
        if self.page == 'create':
            self._refreshCreateOptions()

    def _getActivityDestination(self, activity):
        fixed = {
            'VP': (ToontownGlobals.SellbotHQ, 'Sellbot HQ'),
            'CFO': (ToontownGlobals.CashbotHQ, 'Cashbot HQ'),
            'CJ': (ToontownGlobals.LawbotHQ, 'Lawbot HQ'),
            'CEO': (ToontownGlobals.BossbotHQ, 'Bossbot HQ'),
            'Sellbot Factory': (ToontownGlobals.SellbotFactoryExt, 'Sellbot HQ'),
            'Cashbot Mint': (ToontownGlobals.CashbotHQ, 'Cashbot HQ'),
            'Lawbot DA Office': (ToontownGlobals.LawbotOfficeExt, 'Lawbot HQ'),
            'Bossbot Country Club': (ToontownGlobals.BossbotHQ, 'Bossbot HQ'),
            'Racing': (ToontownGlobals.GoofySpeedway, getattr(TTLocalizer, 'lGoofySpeedway', 'Goofy Speedway')),
            'Golfing': (ToontownGlobals.GolfZone, getattr(TTLocalizer, 'lGolfZone', 'Golf Zone')),
            'High Roller': (ToontownGlobals.MajorPlayerLobby, getattr(TTLocalizer, 'lMinniesMelodyland', 'Mezzo Melodyland')),
            'Pacesetter': (ToontownGlobals.PacesetterLobby, getattr(TTLocalizer, 'lDonaldsDreamland', 'Drowsy Dreamland')),
            'Chainsaw Consultant': (ToontownGlobals.ChainsawLobby, getattr(TTLocalizer, 'lOutdoorZone', 'Acorn Acres')),
        }
        if activity in fixed:
            return fixed[activity]
        return self._getZoneId(), self._getLocationLabel()

    def _getZoneId(self):
        try:
            return int(base.localAvatar.getZoneId())
        except:
            try:
                return int(base.localAvatar.getLocation()[1])
            except:
                return 0

    def _getLocationLabel(self):
        zoneId = self._getZoneId()
        try:
            hoodId = ZoneUtil.getCanonicalHoodId(zoneId)
        except:
            hoodId = zoneId
        try:
            branchId = ZoneUtil.getCanonicalBranchZone(zoneId)
        except:
            try:
                branchId = ZoneUtil.getCanonicalZoneId(zoneId)
            except:
                branchId = zoneId

        if branchId == hoodId:
            try:
                name = ToontownGlobals.hoodNameMap.get(hoodId)
                if name:
                    if isinstance(name, tuple):
                        if len(name) > 2:
                            return str(name[2])
                        return str(name[0])
                    return str(name)
            except:
                pass

        try:
            street = TTLocalizer.GlobalStreetNames.get(branchId)
            if street and len(street) > 2 and street[2]:
                return str(street[2])
        except:
            pass

        try:
            title = TTLocalizer.zone2TitleDict.get(zoneId)
            if title and title[0]:
                return str(title[0])
        except:
            pass

        try:
            name = ToontownGlobals.hoodNameMap.get(hoodId)
            if name:
                if isinstance(name, tuple):
                    if len(name) > 2:
                        return str(name[2])
                    return str(name[0])
                return str(name)
        except:
            pass
        return 'Zone %s' % zoneId
