from direct.gui.DirectGui import DirectButton, DirectFrame, DirectScrolledFrame
from direct.gui import DirectGuiGlobals as DGG
from pandac.PandaModules import TextNode, Vec4

from toontown.toon.socialpanel.SocialPanelGUI import SelectorButton
from toontown.toon.socialpanel.SocialPanelGlobals import sp_gui, groupsPerCol
from toontown.toon.socialpanel.groups.SocialPanelGroup import SocialPanelGroup


class SocialPanelGroupBrowser(DirectScrolledFrame):
    DEFAULT_SIZE = (-1.93, 1.943, 0, 6.2)
    FILTER_SIZE = (-1.93, 1.943, 0, 4.23)
    SCROLLBAR_WIDTH = 0.39

    CATEGORY_ACTIVITIES = {
        'Cog Buildings': ('Cog Building',),
        'Bosses': ('VP', 'CFO', 'CJ', 'CEO'),
        'Minibosses': ('High Roller', 'Pacesetter', 'Chainsaw Consultant'),
        'Facilities': ('Sellbot Factory', 'Cashbot Mint', 'Lawbot DA Office', 'Bossbot Country Club'),
        'Activities': ('Racing', 'Golfing', 'Trolley', 'Fishing', 'Other'),
    }

    TYPE_OPTIONS = {
        'Cog Buildings': ('Any Cog Building', 'Cog Building'),
        'Bosses': ('Any Boss', 'VP', 'CFO', 'CJ', 'CEO'),
        'Minibosses': ('Any Miniboss', 'High Roller', 'Pacesetter', 'Chainsaw Consultant'),
        'Facilities': ('Any Facility', 'Sellbot Factory', 'Cashbot Mint', 'Lawbot DA Office', 'Bossbot Country Club'),
        'Activities': ('Any Activity', 'Racing', 'Golfing', 'Trolley', 'Fishing', 'Other'),
    }

    TYPE_ACTIVITIES = {
        'Any Cog Building': ('Cog Building',),
        'Any Boss': ('VP', 'CFO', 'CJ', 'CEO'),
        'Any Miniboss': ('High Roller', 'Pacesetter', 'Chainsaw Consultant'),
        'Any Facility': ('Sellbot Factory', 'Cashbot Mint', 'Lawbot DA Office', 'Bossbot Country Club'),
        'Any Activity': ('Racing', 'Golfing', 'Trolley', 'Fishing', 'Other'),
    }

    KNOWN_LOCATIONS = {
        'VP': 'Sellbot HQ',
        'CFO': 'Cashbot HQ',
        'CJ': 'Lawbot HQ',
        'CEO': 'Bossbot HQ',
        'Sellbot Factory': 'Sellbot HQ',
        'Cashbot Mint': 'Cashbot HQ',
        'Lawbot DA Office': 'Lawbot HQ',
        'Bossbot Country Club': 'Bossbot HQ',
        'High Roller': 'Mezzo Melodyland',
        'Pacesetter': 'Drowsy Dreamland',
        'Chainsaw Consultant': 'Acorn Acres',
        'Racing': 'Goofy Speedway',
        'Golfing': 'Golf Zone',
    }

    def __init__(self, parent, manager):
        self.manager = manager
        self.groups = []
        self.filterOpen = False
        self.restrictMode = True
        self.selectorButton_category = SelectorButton(
            parent=parent, pos=(0.07, 0, 0.365), width=0.6, title='Category',
            callback=self.selector_updateCategory, scale=0.42,
            darkCol=(0.231, 0.325, 0.212, 1), lightCol=(0.741, 0.91, 0.682, 1))
        self.selectorButton_type = SelectorButton(
            parent=parent, pos=(0.07, 0, 0.3063), width=0.6, title='Type',
            callback=self.selector_updateType, scale=0.42,
            darkCol=(0.231, 0.325, 0.212, 1), lightCol=(0.573, 0.753, 0.518, 1))
        self.selectorButton_location = SelectorButton(
            parent=parent, pos=(0.07, 0, 0.2476), width=0.6, title='Location',
            callback=self.selector_updateLocation, scale=0.42,
            darkCol=(0.231, 0.325, 0.212, 1), lightCol=(0.741, 0.91, 0.682, 1))
        for button in (self.selectorButton_category, self.selectorButton_type, self.selectorButton_location):
            button.titleText['text_pos'] = (-0.555, -0.020)
            button.titleText['text_scale'] = 0.08
        self.bottomFramePanel = DirectFrame(
            parent=parent, pos=(0.07, 0, 0.1889), relief=DGG.FLAT, scale=0.42,
            frameSize=(-0.723, 0.394, -0.07, 0.07), frameColor=(0.302, 0.6, 0.259, 0.33),
            text='Access', text_pos=(-0.555, -0.024), text_scale=0.08,
            text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1))
        self.button_availabilityAvailable = DirectButton(
            parent=parent, relief=None, pos=(0, 0, 0.188),
            text='Available', text_scale=0.035, text_fg=Vec4(1, 1, 1, 1),
            text_shadow=Vec4(0, 0, 0, 1), text_pos=(0, -0.009),
            geom=(sp_gui.find('**/OrangeButton_N'), sp_gui.find('**/OrangeButton_P'), sp_gui.find('**/OrangeButton_H')),
            geom_scale=(0.06 * (164.0 / 63.0), 1, 0.06), geom_color=(0.8, 0.8, 0.8, 1),
            scale=0.8, command=self.enableRestrictMode)
        self.button_availabilityAll = DirectButton(
            parent=parent, relief=None, pos=(0.14, 0, 0.188),
            text='All', text_scale=0.035, text_fg=Vec4(1, 1, 1, 1),
            text_shadow=Vec4(0, 0, 0, 1), text_pos=(0, -0.009),
            geom=(sp_gui.find('**/OrangeButton_N'), sp_gui.find('**/OrangeButton_P'), sp_gui.find('**/OrangeButton_H')),
            geom_scale=(0.06 * (164.0 / 63.0), 1, 0.06), geom_color=(0.329, 0.329, 0.329, 1),
            scale=0.8, command=self.disableRestrictMode)
        self.filterControls = [
            self.selectorButton_category, self.selectorButton_type, self.selectorButton_location,
            self.bottomFramePanel, self.button_availabilityAvailable, self.button_availabilityAll]
        for control in self.filterControls:
            control.hide()

        self.verticalScrollImage = DirectFrame(
            parent=parent, relief=None, scale=0.104, pos=(0.21, 0, 0.023),
            image=sp_gui.find('**/ScrollBar_BAR'),
            image_scale=((49.0 / 714.0) * 7.7, 1, 7.21))
        DirectScrolledFrame.__init__(
            self, parent=parent, relief=DGG.FLAT, scale=0.12, pos=(0, 0, -0.349),
            frameSize=self.DEFAULT_SIZE,
            canvasSize=self._canvasSize(1),
            scrollBarWidth=self.SCROLLBAR_WIDTH,
            manageScrollBars=1,
            autoHideScrollBars=0,
            frameColor=(0.224, 0.549, 0.259, 0.0),
            verticalScroll_relief=None,
            verticalScroll_thumb_frameColor=(1, 1, 1, 0),
            verticalScroll_resizeThumb=0,
            verticalScroll_thumb_image=sp_gui.find('**/ScrollBar'),
            verticalScroll_thumb_image_scale=(0.3987, 1, 0.39),
            verticalScroll_thumb_image_pos=(-0.0032, 0, 0))
        self.initialiseoptions(SocialPanelGroupBrowser)
        self.horizontalScroll.hide()
        try:
            self.verticalScroll.incButton.hide()
            self.verticalScroll.decButton.hide()
        except:
            pass
        self.loadingText = DirectFrame(
            parent=self, relief=None, pos=(-0.1564, 0, 3.5334),
            text='Loading...', text_fg=(0.122, 0.278, 0.106, 1),
            text_scale=0.36, text_pos=(0, -0.2))
        self.loadingText.hide()
        self.accept('group-tracker-browse', self.refresh)
        self.accept('group-tracker-state', self.refresh)
        self.setFilterChoices()
        self.refresh()

    def show(self):
        DirectScrolledFrame.show(self)
        if self.verticalScrollImage:
            self.verticalScrollImage.show()
        if self.filterOpen:
            for control in self.filterControls:
                control.show()

    def hide(self):
        if self.verticalScrollImage:
            self.verticalScrollImage.hide()
        for control in self.filterControls:
            control.hide()
        DirectScrolledFrame.hide(self)

    def destroy(self):
        self.ignoreAll()
        self._clearGroups()
        for control in self.filterControls:
            try:
                control.destroy()
            except:
                pass
        self.filterControls = []
        try:
            self.verticalScrollImage.destroy()
        except:
            pass
        self.verticalScrollImage = None
        self.manager = None
        DirectScrolledFrame.destroy(self)

    def _clearGroups(self):
        for group in self.groups:
            try:
                group.destroy()
            except:
                pass
        self.groups = []

    def switchFilterStatus(self):
        self.filterOpen = not self.filterOpen
        if self.filterOpen:
            self['frameSize'] = self.FILTER_SIZE
            self.verticalScrollImage.setPos(0.21, 0, -0.094)
            self.verticalScrollImage['image_scale'] = ((49.0 / 714.0) * 7.7, 1, 4.94)
            for control in self.filterControls:
                control.show()
        else:
            self['frameSize'] = self.DEFAULT_SIZE
            self.verticalScrollImage.setPos(0.21, 0, 0.023)
            self.verticalScrollImage['image_scale'] = ((49.0 / 714.0) * 7.7, 1, 7.21)
            for control in self.filterControls:
                control.hide()
        self.refresh()

    def setFilterMode(self, enabled):
        enabled = bool(enabled)
        if enabled != self.filterOpen:
            self.switchFilterStatus()

    def setFilterChoices(self):
        categories = ['Any', 'Cog Buildings', 'Bosses', 'Minibosses', 'Facilities', 'Activities']
        self.selectorButton_category.setOptions(values=categories, texts=categories, setIndex=0)
        self.selector_updateCategory()

    def selector_updateCategory(self, *args):
        category = self.selectorButton_category.getChoice()
        if category == 'Any':
            self.selectorButton_type.setOptions(values=[], texts=[], canDisable=True)
            self.selectorButton_location.setOptions(values=[], texts=[], canDisable=True)
            self.refresh()
            return
        types = list(self.TYPE_OPTIONS.get(category, ()))
        self.selectorButton_type.setOptions(values=types, texts=types, setIndex=0, canDisable=True)
        self.selector_updateType()

    def selector_updateType(self, *args):
        activities = self._selectedActivities()
        locations = ['Anywhere']
        for activity in activities:
            location = self.KNOWN_LOCATIONS.get(activity)
            if location and location not in locations:
                locations.append(location)
        for group in list(getattr(self.manager, 'joinableGroups', []) or []):
            if activities and group.get('activity') not in activities:
                continue
            location = str(group.get('location', '')).strip()
            if location and location not in locations:
                locations.append(location)
        self.selectorButton_location.setOptions(values=locations, texts=locations, setIndex=0, canDisable=True)
        self.refresh()

    def selector_updateLocation(self, *args):
        self.refresh()

    def enableRestrictMode(self):
        self.restrictMode = True
        self.button_availabilityAvailable['geom_color'] = (0.8, 0.8, 0.8, 1)
        self.button_availabilityAll['geom_color'] = (0.329, 0.329, 0.329, 1)
        self.refresh()

    def disableRestrictMode(self):
        self.restrictMode = False
        self.button_availabilityAvailable['geom_color'] = (0.329, 0.329, 0.329, 1)
        self.button_availabilityAll['geom_color'] = (0.8, 0.8, 0.8, 1)
        self.refresh()

    def _selectedActivities(self):
        category = self.selectorButton_category.getChoice()
        if category == 'Any' or category is None:
            return ()
        typeChoice = self.selectorButton_type.getChoice()
        if typeChoice in self.TYPE_ACTIVITIES:
            return self.TYPE_ACTIVITIES[typeChoice]
        if typeChoice:
            return (typeChoice,)
        return self.CATEGORY_ACTIVITIES.get(category, ())

    def _filteredGroups(self):
        groups = list(getattr(self.manager, 'joinableGroups', []) or [])
        activities = self._selectedActivities()
        locationChoice = self.selectorButton_location.getChoice()
        result = []
        for group in groups:
            if activities and group.get('activity') not in activities:
                continue
            if locationChoice and locationChoice != 'Anywhere':
                if str(group.get('location', '')).strip() != str(locationChoice):
                    continue
            if self.restrictMode:
                members = group.get('members', []) or []
                if len(members) >= int(group.get('maxSize', 4)):
                    continue
            result.append(group)
        return result

    def refresh(self, *args):
        self.loadingText.hide()
        self._clearGroups()
        groups = self._filteredGroups()
        groups.sort(key=lambda group: (len(group.get('members', [])) >= int(group.get('maxSize', 4)), -int(group.get('created', 0))))
        canvas = self.getCanvas()
        filtering = self.selectorButton_category.getChoice() not in (None, 'Any')
        if not groups:
            group = SocialPanelGroup(canvas, None, self.index2GroupPos(0), self.manager,
                                     empty=True, filtering=filtering)
            group.bindToScroll(self)
            self.groups.append(group)
        else:
            for index, groupData in enumerate(groups):
                group = SocialPanelGroup(canvas, groupData, self.index2GroupPos(index), self.manager)
                group.bindToScroll(self)
                self.groups.append(group)
        self['canvasSize'] = self._canvasSize(len(self.groups))
        try:
            self.setCanvasSize()
            self.verticalScroll.setValue(0)
        except:
            pass

    def index2GroupPos(self, index):
        top = self.FILTER_SIZE[3] if self.filterOpen else self.DEFAULT_SIZE[3]
        canvasSize = [self.DEFAULT_SIZE[0], self.DEFAULT_SIZE[1] - self.SCROLLBAR_WIDTH,
                      self.DEFAULT_SIZE[2] - 0.001, top]
        canvasWidth = canvasSize[1] - canvasSize[0]
        canvasHeight = canvasSize[2] - canvasSize[3]
        canvasXStart = canvasSize[0] + canvasWidth / 2.0
        canvasZStart = -canvasHeight
        zpos = canvasZStart + (index * (canvasHeight / float(groupsPerCol)))
        return (canvasXStart, 0, zpos)

    def _canvasSize(self, count):
        top = self.FILTER_SIZE[3] if self.filterOpen else self.DEFAULT_SIZE[3]
        bottom = self.DEFAULT_SIZE[2] - 0.001
        offscreen = max(0, count - groupsPerCol)
        if offscreen:
            bottom -= (top / float(groupsPerCol)) * offscreen
        return (self.DEFAULT_SIZE[0], self.DEFAULT_SIZE[1] - self.SCROLLBAR_WIDTH, bottom, top)
