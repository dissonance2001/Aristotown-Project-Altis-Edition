from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel, DirectScrolledFrame
from direct.gui import DirectGuiGlobals as DGG
from pandac.PandaModules import TextNode

from toontown.toon.socialpanel.SocialPanelGlobals import sp_gui, sp_gui_icons
from toontown.toon.socialpanel.friends.SocialPanelFriend import COLOR_DEFAULT, COLOR_SELECTED


class QuickInviteCheck(DirectButton):
    def __init__(self, parent, checked=False, partial=False, command=None, pos=(0, 0, 0)):
        self.checked = bool(checked)
        self.partial = bool(partial)
        self.callback = command
        DirectButton.__init__(
            self, parent=parent, relief=None, frameColor=(0, 0, 0, 0),
            frameSize=(-0.5, 0.5, -0.5, 0.5), pos=pos, scale=0.45,
            command=self._click)
        self.initialiseoptions(QuickInviteCheck)
        self._updateImage()

    def _click(self):
        self.checked = not self.checked
        self.partial = False
        self._updateImage()
        if self.callback:
            self.callback(self.checked)

    def setCheckedState(self, checked, partial=False):
        self.checked = bool(checked)
        self.partial = bool(partial)
        self._updateImage()

    def _updateImage(self):
        if self.partial:
            name = '**/CIRCLE2'
        elif self.checked:
            name = '**/CIRCLE3'
        else:
            name = '**/CIRCLE1'
        node = sp_gui_icons.find(name)
        if not node.isEmpty():
            self['image'] = node
            self['image_scale'] = (1, 1, 1)


class SocialPanelGroupQuickInvite(DirectFrame):
    DEFAULT_SIZE = (-1.93, 1.943, -0.06, 5.14)
    SCROLLBAR_WIDTH = 0.39
    ROW_HEIGHT = 0.5
    ROW_STEP = 0.485
    SCALE = 0.12
    POS_Z = -0.143

    def __init__(self, parent, createMode=False):
        DirectFrame.__init__(self, parent=parent, relief=None)
        self.initialiseoptions(SocialPanelGroupQuickInvite)
        self.groupsTab = parent
        self.createMode = bool(createMode)
        self.selected = {}
        self.rows = []
        self._fullPage = False
        self._backCommand = None
        self._background = DirectFrame(
            parent=self, relief=DGG.FLAT,
            frameSize=(self.DEFAULT_SIZE[0] * self.SCALE,
                       self.DEFAULT_SIZE[1] * self.SCALE,
                       self.DEFAULT_SIZE[2] * self.SCALE + self.POS_Z,
                       self.DEFAULT_SIZE[3] * self.SCALE + self.POS_Z),
            frameColor=(46.0 / 255.0, 97.0 / 255.0, 50.0 / 255.0, 200.0 / 255.0))
        self.scroll = DirectScrolledFrame(
            parent=self, relief=DGG.FLAT, scale=self.SCALE, pos=(0, 0, self.POS_Z),
            frameSize=self.DEFAULT_SIZE,
            canvasSize=self._defaultCanvasSize(),
            scrollBarWidth=self.SCROLLBAR_WIDTH,
            manageScrollBars=0,
            frameColor=(46.0 / 255.0, 97.0 / 255.0, 50.0 / 255.0, 200.0 / 255.0),
            verticalScroll_image=sp_gui.find('**/ScrollBar_BAR'),
            verticalScroll_image_scale=(0.4583, 1.0, 5.24837),
            verticalScroll_image_pos=(1.7627, 0, 2.54119),
            verticalScroll_relief=None,
            verticalScroll_thumb_frameColor=(1, 1, 1, 0),
            verticalScroll_resizeThumb=0,
            verticalScroll_thumb_image=sp_gui.find('**/ScrollBar'),
            verticalScroll_thumb_image_scale=(0.3913, 1, 0.3971),
            verticalScroll_thumb_image_pos=(0.0095, 0, 0))
        try:
            self.scroll.horizontalScroll.destroy()
        except:
            try:
                self.scroll.horizontalScroll.hide()
            except:
                pass
        try:
            self.scroll.verticalScroll.incButton.destroy()
            self.scroll.verticalScroll.decButton.destroy()
        except:
            try:
                self.scroll.verticalScroll.incButton.hide()
                self.scroll.verticalScroll.decButton.hide()
            except:
                pass
        self.backButton = DirectButton(
            parent=self, pos=(0.00151, 0, -0.26443), relief=None,
            text='Back', text_pos=(0, -0.01), scale=0.8,
            geom=(sp_gui.find('**/OrangeButton_N'), sp_gui.find('**/OrangeButton_P'), sp_gui.find('**/OrangeButton_H')),
            geom_scale=(0.09 * (164.0 / 63.0), 1, 0.09), geom_color=(0.9, 0.9, 0.9, 1.0),
            text_scale=0.039, command=self._back,
            text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1))
        self._bindWheel(self.scroll)
        try:
            self._bindWheel(self.scroll.verticalScroll)
            self._bindWheel(self.scroll.verticalScroll.thumb)
        except:
            pass
        self.backButton.hide()
        self.hide()

    def destroy(self):
        self._clearRows()
        self.groupsTab = None
        DirectFrame.destroy(self)

    def _defaultCanvasSize(self):
        return (self.DEFAULT_SIZE[0], self.DEFAULT_SIZE[1] - self.SCROLLBAR_WIDTH,
                self.DEFAULT_SIZE[2] - 0.001, self.DEFAULT_SIZE[3])

    def _canvasLeft(self):
        return self._defaultCanvasSize()[0]

    def _canvasRight(self):
        return self._defaultCanvasSize()[1]

    def _canvasCenter(self):
        return (self._canvasLeft() + self._canvasRight()) / 2.0

    def _clearRows(self):
        for row in self.rows:
            try:
                row.destroy()
            except:
                pass
        self.rows = []

    def _bindWheel(self, widget):
        try:
            widget.bind(DGG.WHEEL_UP, lambda event: self._scroll(-1))
            widget.bind(DGG.WHEEL_DOWN, lambda event: self._scroll(1))
        except:
            pass

    def _scroll(self, direction):
        try:
            canvas = self.scroll['canvasSize']
            frame = self.scroll['frameSize']
            canvasHeight = abs(float(canvas[3] - canvas[2]))
            frameHeight = abs(float(frame[3] - frame[2]))
            if canvasHeight <= frameHeight:
                return
            value = float(self.scroll.verticalScroll['value'])
            value += (0.8 / canvasHeight) * direction
            if value < 0:
                value = 0
            if value > 1:
                value = 1
            self.scroll.verticalScroll['value'] = value
        except:
            pass

    def getInvitedAvIds(self):
        result = []
        for avId, selected in self.selected.items():
            if selected:
                result.append(avId)
        return result

    def show(self):
        self.refresh()
        if self.createMode:
            self._fullPage = False
            self.backButton.hide()
        else:
            self._fullPage = True
            self.backButton.show()
        DirectFrame.show(self)

    def hide(self):
        DirectFrame.hide(self)

    def setBackCommand(self, command):
        self._backCommand = command

    def _back(self):
        if self._backCommand:
            self._backCommand()
        else:
            self.hide()

    def _memberIds(self):
        group = getattr(self.groupsTab.mgr, 'group', None) or {}
        result = set()
        for member in group.get('members', []):
            try:
                result.add(int(member.get('avId', 0)))
            except:
                pass
        for invite in group.get('invites', []):
            try:
                result.add(int(invite.get('avId', 0)))
            except:
                pass
        return result

    def _nearbyToons(self):
        memberIds = self._memberIds()
        localId = int(getattr(base.localAvatar, 'doId', 0))
        result = {}
        try:
            toonDClass = base.cr.dclassesByName.get('DistributedToon')
        except:
            toonDClass = None
        try:
            for avId, obj in base.cr.doId2do.items():
                avId = int(avId)
                if avId == localId or avId in memberIds or not hasattr(obj, 'getName'):
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
                    result[avId] = str(obj.getName())
        except:
            pass
        return sorted(result.items(), key=lambda item: item[1].lower())

    def _onlineFriends(self):
        memberIds = self._memberIds()
        localId = int(getattr(base.localAvatar, 'doId', 0))
        result = {}
        for friend in getattr(base.localAvatar, 'friendsList', []):
            try:
                avId = int(friend[0])
            except:
                continue
            if avId == localId or avId in memberIds:
                continue
            try:
                if not base.cr.isFriendOnline(avId):
                    continue
            except:
                if avId not in getattr(base.cr, 'doId2do', {}):
                    continue
            try:
                handle = base.cr.identifyFriend(avId)
            except:
                handle = None
            if handle is None:
                handle = getattr(base.cr, 'doId2do', {}).get(avId)
            if handle is not None and hasattr(handle, 'getName'):
                result[avId] = str(handle.getName())
        return sorted(result.items(), key=lambda item: item[1].lower())

    def _onlineClubmates(self):
        memberIds = self._memberIds()
        localId = int(getattr(base.localAvatar, 'doId', 0))
        result = {}
        clubMgr = getattr(base.cr, 'clubMgr', None)
        if not clubMgr or not hasattr(clubMgr, 'isInClub') or not clubMgr.isInClub():
            return []
        try:
            members = clubMgr.getMembers()
        except:
            members = []
        for member in members:
            try:
                avId = int(member.get('avId', 0))
            except:
                continue
            if not avId or avId == localId or avId in memberIds:
                continue
            online = avId in getattr(base.cr, 'doId2do', {})
            if not online:
                try:
                    online = bool(base.cr.isFriendOnline(avId))
                except:
                    online = False
            if online:
                result[avId] = str(member.get('name', 'Toon'))
        return sorted(result.items(), key=lambda item: item[1].lower())

    def _availableSelectionCount(self):
        if self.createMode:
            return max(0, int(self.groupsTab.getSelectedCapacity()) - 1)
        group = getattr(self.groupsTab.mgr, 'group', None) or {}
        maxSize = int(group.get('maxSize', 4))
        used = len(group.get('members', [])) + len(group.get('invites', []))
        return max(0, maxSize - used)

    def _canSelect(self, avId):
        if self.selected.get(avId, False):
            return True
        return len(self.getInvitedAvIds()) < self._availableSelectionCount()

    def refresh(self):
        self._clearRows()
        canvas = self.scroll.getCanvas()
        groups = [
            ('Nearby Toons', self._nearbyToons()),
            ('Online Friends', self._onlineFriends()),
        ]
        clubmates = self._onlineClubmates()
        if clubmates:
            groups.append(('Online Clubmates', clubmates))
        y = self.DEFAULT_SIZE[3]
        totalRows = 0
        for title, entries in groups:
            self._makeHeader(canvas, title, entries, y)
            totalRows += 1
            y -= self.ROW_STEP
            for avId, name in entries:
                self._makeToonRow(canvas, avId, name, y)
                totalRows += 1
                y -= self.ROW_STEP
        if totalRows == len(groups):
            label = DirectLabel(
                parent=canvas, relief=None,
                pos=(self._canvasCenter(), 0, 2.63),
                text='No Toons available to invite.', text_scale=0.24,
                text_align=TextNode.ACenter, text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1))
            self.rows.append(label)
        defaultCanvas = self._defaultCanvasSize()
        contentBottom = y + self.ROW_STEP - self.ROW_HEIGHT
        bottom = min(defaultCanvas[2], contentBottom)
        self.scroll['canvasSize'] = (defaultCanvas[0], defaultCanvas[1], bottom, defaultCanvas[3])
        try:
            self.scroll.setCanvasSize()
            self.scroll.verticalScroll['value'] = 0
        except:
            pass
        visibleHeight = defaultCanvas[3] - defaultCanvas[2]
        contentHeight = defaultCanvas[3] - bottom
        if contentHeight > visibleHeight + 0.001:
            try:
                self.scroll.verticalScroll.show()
            except:
                pass
        else:
            try:
                self.scroll.verticalScroll.hide()
            except:
                pass

    def _makeHeader(self, canvas, title, entries, y):
        selectedCount = 0
        for avId, name in entries:
            if self.selected.get(avId, False):
                selectedCount += 1
        checked = bool(entries) and selectedCount == len(entries)
        partial = bool(entries) and selectedCount > 0 and selectedCount < len(entries)
        frame = DirectButton(
            parent=canvas, relief=DGG.FLAT, pos=(0, 0, y),
            geom=(sp_gui.find('**/Box_N'), sp_gui.find('**/Box_P'), sp_gui.find('**/Box_H')),
            geom_scale=(self.ROW_HEIGHT * (455.0 / 42.0), 1, self.ROW_HEIGHT),
            geom_pos=(self._canvasCenter(), 0, -self.ROW_HEIGHT / 2.0),
            geom_color=(0.755, 0.763, 0.778, 1.0),
            frameSize=(self._canvasLeft(), self._canvasRight(), -self.ROW_HEIGHT, 0),
            frameColor=(0.755, 0.763, 0.778, 1.0),
            text=title, text_scale=0.26,
            text_pos=(self._canvasCenter(), -0.31),
            text_fg=(0, 0, 0, 1), command=self._toggleGroup, extraArgs=[entries])
        self.rows.append(frame)
        self._bindWheel(frame)
        if entries:
            check = QuickInviteCheck(
                parent=frame, checked=checked, partial=partial,
                command=lambda mode, entries=entries: self._setGroup(entries, mode),
                pos=(self._canvasLeft() + 0.21, 0, -0.2467))
            self.rows.append(check)
            self._bindWheel(check)

    def _makeToonRow(self, canvas, avId, name, y):
        selected = bool(self.selected.get(avId, False))
        color = COLOR_SELECTED if selected else COLOR_DEFAULT
        row = DirectButton(
            parent=canvas, relief=DGG.FLAT, pos=(0, 0, y),
            geom=(sp_gui.find('**/Box_N'), sp_gui.find('**/Box_P'), sp_gui.find('**/Box_H')),
            geom_scale=(self.ROW_HEIGHT * (455.0 / 42.0), 1, self.ROW_HEIGHT),
            geom_pos=(self._canvasCenter(), 0, -self.ROW_HEIGHT / 2.0),
            geom_color=color,
            frameSize=(self._canvasLeft(), self._canvasRight(), -self.ROW_HEIGHT, 0),
            frameColor=color,
            text=name, text_scale=0.23,
            text_pos=(self._canvasCenter(), -0.31),
            text_fg=(0, 0, 0, 1), command=self._toggle, extraArgs=[avId])
        self.rows.append(row)
        self._bindWheel(row)
        check = QuickInviteCheck(
            parent=row, checked=selected,
            command=lambda mode, avId=avId: self._setOne(avId, mode),
            pos=(self._canvasLeft() + 0.21, 0, -0.2467))
        self.rows.append(check)
        self._bindWheel(check)

    def _toggle(self, avId):
        self._setOne(avId, not bool(self.selected.get(avId, False)))

    def _setOne(self, avId, mode):
        if mode and not self._canSelect(avId):
            return
        self.selected[avId] = bool(mode)
        self.refresh()
        self.groupsTab.updateCapacityText()

    def _toggleGroup(self, entries):
        if not entries:
            return
        allSelected = True
        for avId, name in entries:
            if not self.selected.get(avId, False):
                allSelected = False
                break
        self._setGroup(entries, not allSelected)

    def _setGroup(self, entries, mode):
        if not mode:
            for avId, name in entries:
                self.selected[avId] = False
        else:
            for avId, name in entries:
                if self.selected.get(avId, False):
                    continue
                if not self._canSelect(avId):
                    break
                self.selected[avId] = True
        self.refresh()
        self.groupsTab.updateCapacityText()
