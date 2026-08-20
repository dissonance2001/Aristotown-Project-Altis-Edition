from __future__ import absolute_import
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel, DirectScrolledFrame
from direct.gui import DirectGuiGlobals as DGG
from pandac.PandaModules import TextNode

from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals

from toontown.toon.socialpanel.SocialPanelGlobals import sp_gui, sp_gui_icons, getSocialPanelGroupBg
from toontown.toon.socialpanel.SocialPanelGUI import SocialPanelContextDropdown
from toontown.toon.socialpanel.groups.SocialPanelText import ExtendedOnscreenText
from six.moves import range


class SocialPanelGroupViewer(DirectFrame):
    def __init__(self, parent, manager):
        DirectFrame.__init__(self, parent=parent, relief=None)
        self.initialiseoptions(SocialPanelGroupViewer)
        self.manager = manager
        self.group = None
        self.contextMenu = None
        self.rowObjects = []
        self.infoFrame = ExtendedOnscreenText(
            parent=self, text='', pos=(-0.0701, 0.261),
            scale=0.034, fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 1), align=TextNode.ACenter)
        self.button_cancelView = DirectButton(
            parent=self, pos=(0.1657, 0, 0.3221), relief=None,
            geom=(sp_gui.find('**/OrangeButton_N'), sp_gui.find('**/OrangeButton_P'), sp_gui.find('**/OrangeButton_H')),
            text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
            text='Back', command=self.requestCancel,
            geom_scale=(0.1381, 1, 0.0533), text_scale=0.034, text_pos=(0, -0.01))
        self.button_groupAction = DirectButton(
            parent=self, pos=(0.1657, 0, 0.2688), relief=None,
            geom=(sp_gui.find('**/OrangeButton_N'), sp_gui.find('**/OrangeButton_P'), sp_gui.find('**/OrangeButton_H')),
            text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
            text='', geom_scale=(0.1381, 1, 0.0533),
            text_scale=0.034, text_pos=(0, -0.01))
        self.button_groupPrivacy = DirectFrame(
            parent=self, pos=(0.1657, 0, 0.2182), relief=None,
            geom=sp_gui.find('**/POPUPBAR_TITLEAREA'), geom_color=(1, 1, 1, 0),
            text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
            text='Public', geom_scale=(0.1381, 1, 0.05),
            text_scale=0.034, text_pos=(0, -0.01))
        self.frame_base = DirectFrame(
            parent=self, pos=(0.0012, 0, 0.4119), relief=None,
            frameColor=(1, 1, 1, 0), scale=0.1344,
            geom=sp_gui.find('**/SocialPanel_Groups_Box_Base'),
            geom_scale=(456.0 / 129.0, 1, 1), geom_color=(0.85, 0.85, 0.85, 1))
        self.frame_image = DirectFrame(
            parent=self.frame_base, relief=None, frameColor=(1, 1, 1, 0),
            geom=sp_gui.find('**/SocialPanel_Groups_Box_Base'),
            geom_scale=(0.96 * (456.0 / 129.0), 1, 0.83),
            geom_color=(0.7, 0.7, 0.7, 1))
        self.title_text = DirectLabel(
            parent=self.frame_base, relief=None, text='', scale=0.35,
            text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
            text_wordwrap=7.44, pos=(0, 0, -0.1))
        self.toonsList = DirectScrolledFrame(
            parent=self, relief=None, pos=(0.0, 0.0, 0.19694),
            frameSize=(-0.23399, 0.23415, -0.54534, 0.0),
            canvasSize=(-0.22, 0.23415, -0.54534, 0.0),
            scrollBarWidth=0.025, manageScrollBars=0, autoHideScrollBars=1,
            verticalScroll_relief=None,
            verticalScroll_thumb_frameColor=(1, 1, 1, 0),
            verticalScroll_resizeThumb=0)
        self.toonsList.horizontalScroll.hide()
        self.toonsList.verticalScroll.hide()
        self.accept('group-tracker-state', self._stateUpdate)

    def destroy(self):
        self.ignoreAll()
        self._clearRows()
        self.cleanupContextMenu()
        self.manager = None
        self.group = None
        DirectFrame.destroy(self)

    def cleanupContextMenu(self):
        if self.contextMenu:
            try:
                self.contextMenu.destroy()
            except:
                pass
            self.contextMenu = None

    def updateGroup(self, group):
        self.group = group or {}
        localId = int(getattr(base.localAvatar, 'doId', 0))
        members = self.group.get('members', [])
        memberIds = [int(member.get('avId', 0)) for member in members]
        ownerId = int(self.group.get('ownerId', 0))
        if localId not in memberIds:
            self.button_groupAction.configure(text='Join', command=self.requestJoin)
        else:
            self.button_groupAction.configure(text='Actions', command=self.expandActionsDropdown)
        district = self._districtName()
        self.infoFrame.setTextWithVerticalAlignment('%s\n%s\n%s/%s Toons' % (
            district, self.group.get('location', 'Current Area'),
            len(members), int(self.group.get('maxSize', 4))))
        self.title_text['text'] = self.group.get('activity', 'Group')
        self.frame_image['geom'] = getSocialPanelGroupBg(self.group, pgOnly=False)
        self.button_groupPrivacy['text'] = 'Public' if self.group.get('published', False) else 'Private'
        self._renderSlots()

    def _districtName(self):
        shardId = int(self.group.get('shardId', 0) or 0)
        if shardId:
            try:
                return str(base.cr.getShardName(shardId))
            except:
                pass
        try:
            return str(base.cr.getShardName(base.localAvatar.defaultShard))
        except:
            return 'District'

    def _stateUpdate(self, group):
        if self.group and group and int(self.group.get('id', 0)) == int(group.get('id', 0)):
            self.updateGroup(group)
        elif self.group and not group:
            self.requestCancel()

    def _clearRows(self):
        for row in self.rowObjects:
            try:
                row.destroy()
            except:
                pass
        self.rowObjects = []

    def _renderSlots(self):
        self._clearRows()
        canvas = self.toonsList.getCanvas()
        members = list(self.group.get('members', []) or [])
        maxSize = int(self.group.get('maxSize', 4))
        ownerId = int(self.group.get('ownerId', 0))
        localId = int(getattr(base.localAvatar, 'doId', 0))
        ownerMember = None
        for groupMember in members:
            if int(groupMember.get('avId', 0)) == ownerId:
                ownerMember = groupMember
                break
        y = -0.03
        rowHeight = 0.05
        for index in range(maxSize):
            member = members[index] if index < len(members) else None
            odd = index % 2
            if member:
                color = (0.537, 0.757, 0.525, 1.0) if not odd else (0.431, 0.655, 0.42, 1.0)
                frame = DirectFrame(
                    parent=canvas, relief=DGG.FLAT, pos=(-0.22, 0, y),
                    frameSize=(0, 0.454, -0.05, 0), frameColor=color)
                avId = int(member.get('avId', 0))
                name = str(member.get('name', 'Toon'))
                reserved = bool(member.get('reserved', False))
                labelText = name
                if avId == ownerId:
                    labelText += '  (Leader)'
                label = DirectLabel(
                    parent=frame, relief=None, pos=(0.058, 0, -0.036),
                    text=labelText, text_scale=0.032, text_align=TextNode.ALeft,
                    text_fg=(0, 0, 0, 1))
                self.rowObjects.extend([frame, label])
                icon = None
                if avId == ownerId:
                    icon = sp_gui_icons.find('**/star')
                elif reserved:
                    icon = sp_gui_icons.find('**/envelope')
                else:
                    present = False
                    if ownerMember:
                        memberZone = int(member.get('zoneId', 0) or 0)
                        ownerZone = int(ownerMember.get('zoneId', 0) or 0)
                        memberShard = int(member.get('shardId', 0) or 0)
                        ownerShard = int(ownerMember.get('shardId', 0) or 0)
                        present = bool(memberZone and ownerZone and memberShard and ownerShard and
                                       memberZone == ownerZone and memberShard == ownerShard)
                    icon = sp_gui_icons.find('**/thumbsup_green' if present else '**/thumbsup_grey')
                if icon is not None and not icon.isEmpty():
                    iconFrame = DirectFrame(
                        parent=frame, relief=None, pos=(0.0291, 0, -0.02587),
                        scale=0.04322, image=icon)
                    self.rowObjects.append(iconFrame)
                if localId == ownerId and avId != ownerId:
                    kick = DirectButton(
                        parent=frame, relief=None, pos=(0.382, 0, -0.026), scale=0.042,
                        image=(sp_gui.find('**/Foot_N'), sp_gui.find('**/Foot_P'), sp_gui.find('**/Foot_H')),
                        image_scale=(64.0 / 58.0, 1, 1),
                        command=self.manager.requestKick, extraArgs=[avId])
                    self.rowObjects.append(kick)
            else:
                color = (0.478, 0.624, 0.459, 1.0) if not odd else (0.388, 0.529, 0.369, 1.0)
                frame = DirectFrame(
                    parent=canvas, relief=DGG.FLAT, pos=(-0.22, 0, y),
                    frameSize=(0, 0.454, -0.05, 0), frameColor=color)
                label = DirectLabel(
                    parent=frame, relief=None, pos=(0.011, 0, -0.036),
                    text='Waiting for Toon...', text_scale=0.032,
                    text_align=TextNode.ALeft, text_fg=(0.149, 0.282, 0.125, 1))
                self.rowObjects.extend([frame, label])
            y -= rowHeight
        self.toonsList['canvasSize'] = (-0.22, 0.23415, min(-0.54534, y - 0.02), 0)
        try:
            self.toonsList.setCanvasSize()
        except:
            pass

    def requestCancel(self):
        messenger.send('social-panel-groups-browse')

    def requestJoin(self):
        if self.group:
            self.manager.requestJoin(int(self.group.get('id', 0)))

    def expandActionsDropdown(self):
        self.cleanupContextMenu()
        self.contextMenu = SocialPanelContextDropdown(labelText='Group Actions', survive=True)
        localId = int(getattr(base.localAvatar, 'doId', 0))
        ownerId = int(self.group.get('ownerId', 0))
        activity = str(self.group.get('activity', ''))
        if localId != ownerId:
            self.contextMenu.addButton('Teleport to Group Leader', self.teleportToGroupLeader)
        targetZone = self._groupDestinationZone()
        targetShard = int(self.group.get('shardId', 0) or 0)
        localZone = self._localZone()
        localShard = self._localShard()
        if targetZone and (targetZone != localZone or (targetShard and targetShard != localShard)):
            self.contextMenu.addButton('Teleport to Group Location', self.teleportToGroupLocation)
        bossCourtyards = {
            'VP': ToontownGlobals.SellbotHQ,
            'CFO': ToontownGlobals.CashbotHQ,
            'CJ': ToontownGlobals.LawbotHQ,
            'CEO': ToontownGlobals.BossbotHQ,
        }
        if activity in bossCourtyards and localZone == bossCourtyards[activity]:
            self.contextMenu.addButton('Teleport to Boss Doors', self.teleportToBossDoors)
        facility = self._facilityInfo(activity)
        if facility and localZone == facility[0]:
            self.contextMenu.addButton('Teleport to %s' % facility[2], self.teleportToFacilityElevator)
        if localId == ownerId:
            self.contextMenu.addButton('Mass Teleport', self.massTeleport)
            self.contextMenu.addButton('Invite Toons', self._invite)
            privacyText = 'Make Private' if self.group.get('published', False) else 'Make Public'
            self.contextMenu.addButton(privacyText, self._privacy)
            self.contextMenu.addButton('Disband Group', self.manager.requestDisband, red=True)
        else:
            self.contextMenu.addButton('Invite Toons', self._invite)
            self.contextMenu.addButton('Leave Group', self.manager.requestLeave, red=True)

    def _localZone(self):
        try:
            return int(base.localAvatar.getZoneId())
        except:
            return 0

    def _localShard(self):
        try:
            return int(base.localAvatar.defaultShard)
        except:
            return 0

    def _placeReadyForTeleport(self):
        try:
            place = base.cr.playGame.getPlace()
        except:
            return None
        if not place:
            return None
        try:
            state = place.getState()
        except:
            state = None
        if state not in ('walk', 'stickerBook'):
            self.manager.receiveNotification(2, 'You cannot teleport right now.')
            return None
        return place

    def _requestZoneTeleport(self, zoneId, shardId=None, extraStatus=None):
        place = self._placeReadyForTeleport()
        if not place:
            return
        try:
            hoodId = ZoneUtil.getHoodId(int(zoneId))
            place.requestTeleport(hoodId, int(zoneId), shardId, -1, extraStatus)
            self.cleanupContextMenu()
        except Exception as error:
            self.manager.notify.warning('Group teleport failed: %s' % error)
            self.manager.receiveNotification(2, 'That Group destination is not available right now.')

    def _disguiseForBossZone(self, zoneId):
        activity = str(self.group.get('activity', '')) if self.group else ''
        mapping = {
            'VP': (ToontownGlobals.SellbotLobby, 3),
            'CFO': (ToontownGlobals.CashbotLobby, 2),
            'CJ': (ToontownGlobals.LawbotLobby, 1),
            'CEO': (ToontownGlobals.BossbotLobby, 0),
        }
        value = mapping.get(activity)
        if value and int(value[0]) == int(zoneId):
            return value[1]
        return None

    def _prepareDisguiseTeleport(self, zoneId):
        deptIndex = self._disguiseForBossZone(zoneId)
        if deptIndex is None:
            return
        try:
            self.manager.prepareSuitTeleport(int(zoneId), int(deptIndex))
        except:
            pass

    def _groupDestinationZone(self):
        if not self.group:
            return 0
        activity = str(self.group.get('activity', ''))
        bossLobbies = {
            'VP': ToontownGlobals.SellbotLobby,
            'CFO': ToontownGlobals.CashbotLobby,
            'CJ': ToontownGlobals.LawbotLobby,
            'CEO': ToontownGlobals.BossbotLobby,
        }
        if activity in bossLobbies:
            return int(bossLobbies[activity])
        return int(self.group.get('zoneId', 0) or 0)

    def teleportToGroupLeader(self):
        if not self.group:
            return
        ownerId = int(self.group.get('ownerId', 0))
        if ownerId == int(getattr(base.localAvatar, 'doId', 0)):
            return
        if not self._placeReadyForTeleport():
            return
        ownerZone = 0
        for member in self.group.get('members', []):
            if int(member.get('avId', 0)) == ownerId and not member.get('reserved', False):
                ownerZone = int(member.get('zoneId', 0) or 0)
                break
        if ownerZone:
            self._prepareDisguiseTeleport(ownerZone)
        self.cleanupContextMenu()
        messenger.send('gotoAvatar', [ownerId, str(self.group.get('ownerName', 'Group Leader')), 'group-leader-%s' % ownerId])

    def teleportToGroupLocation(self):
        if not self.group:
            return
        zoneId = self._groupDestinationZone()
        if not zoneId:
            return
        if not self._placeReadyForTeleport():
            return
        shardId = int(self.group.get('shardId', 0) or 0)
        if self.manager.teleportToGroupZone(zoneId, shardId):
            self.cleanupContextMenu()
        else:
            self.manager.receiveNotification(2, 'That Group destination is not available right now.')

    def teleportToBossDoors(self):
        if not self.group:
            return
        activity = str(self.group.get('activity', ''))
        bossCourtyards = {
            'VP': ToontownGlobals.SellbotHQ,
            'CFO': ToontownGlobals.CashbotHQ,
            'CJ': ToontownGlobals.LawbotHQ,
            'CEO': ToontownGlobals.BossbotHQ,
        }
        zoneId = bossCourtyards.get(activity)
        if not zoneId or self._localZone() != zoneId:
            return
        self._requestZoneTeleport(zoneId, None, {'cogHQDoor': True})

    def _facilityInfo(self, activity):
        facilities = {
            'Sellbot Factory': (ToontownGlobals.SellbotFactoryExt, 'DistributedFactoryElevatorExt', 'Elevator'),
            'Cashbot Mint': (ToontownGlobals.CashbotHQ, 'DistributedMintElevatorExt', 'Elevator'),
            'Lawbot DA Office': (ToontownGlobals.LawbotOfficeExt, 'DistributedLawOfficeElevatorExt', 'Elevator'),
            'Bossbot Country Club': (ToontownGlobals.BossbotHQ, 'DistributedCogKart', 'Kart'),
        }
        return facilities.get(activity)

    def teleportToFacilityElevator(self):
        if not self.group:
            return
        info = self._facilityInfo(str(self.group.get('activity', '')))
        if not info or self._localZone() != info[0]:
            return
        elevatorObj = None
        distance = None
        try:
            objects = base.cr.doFindAll(info[1])
        except:
            objects = []
        for obj in objects:
            try:
                model = obj.getElevatorModel()
                thisDistance = base.localAvatar.getDistance(model)
            except:
                continue
            if elevatorObj is None or thisDistance < distance:
                elevatorObj = obj
                distance = thisDistance
        if elevatorObj is None:
            self.manager.receiveNotification(2, 'The Group entrance is not available right now.')
            return
        self._requestZoneTeleport(self._localZone(), None, {'elevatorId': int(elevatorObj.doId)})

    def massTeleport(self):
        self.cleanupContextMenu()
        self.manager.requestMassTeleport()

    def _invite(self):
        self.cleanupContextMenu()
        messenger.send('social-panel-groups-invite')

    def _privacy(self):
        self.cleanupContextMenu()
        self.manager.requestPublish(not bool(self.group.get('published', False)))
