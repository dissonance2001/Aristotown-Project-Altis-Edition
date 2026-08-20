from __future__ import absolute_import
from pandac.PandaModules import TextNode, Vec3
from direct.gui.DirectGui import (DirectFrame, DirectLabel, DirectButton,
                                  DirectEntry, DirectScrolledFrame)
from direct.gui import DirectGuiGlobals as DGG
from toontown.toonbase import ToontownGlobals
from otp.otpbase import OTPGlobals
from toontown.toon.socialpanel.SocialPanelGlobals import *
from toontown.toon.socialpanel.friends.SocialPanelFriend import SocialPanelFriend
from toontown.toon.socialpanel.SocialPanelGUI import SocialPanelContextDropdown

SORT_ONLINE_FRIENDS = 0
SORT_ALL_FRIENDS = 1
SORT_NEARBY_TOONS = 2

LEFT = -1
RIGHT = 1
FRIEND_COUNT = 10


class SocialPanelFriendsTab(DirectFrame):
    sortOrder = (SORT_NEARBY_TOONS, SORT_ONLINE_FRIENDS, SORT_ALL_FRIENDS)
    sortNames = {
        SORT_NEARBY_TOONS: 'Nearby Toons',
        SORT_ONLINE_FRIENDS: 'Online Friends',
        SORT_ALL_FRIENDS: 'All Friends',
    }

    BOTTOM_PADDING = 0.4
    defaultCanvasSize = (-1.931, 2.3251, -5.78, 0)
    initialSearchText = 'Search...'

    text_panel_ratio = 492.0 / 74.0
    text_panel_scale = 0.0704
    arrow_button_ratio = 30.0 / 35.0
    arrow_button_scale = 0.6

    def __init__(self, parent):
        DirectFrame.__init__(self, parent=parent, relief=None)
        self.initialiseoptions(SocialPanelFriendsTab)
        self.panel = parent
        self.selectedSort = SORT_ONLINE_FRIENDS
        self.searchText = ''
        self.configureMode = False
        self.friendPanels = []
        self.selectedUsers = set()
        self.contextMenu = None
        self.confirmationMenu = None
        self.contextSelectedUsers = set()
        self._searchTaskName = 'altis-social-panel-search-%s' % id(self)
        self.load()
        self.accept('friendsListChanged', self.reload)
        self.accept('friendsMapComplete', self.reload)
        self.accept('friendOnline', self.reload)
        self.accept('friendOffline', self.reload)
        self.accept('ignoreListChanged', self.reload)
        self.accept('favorite-friends-updated', self.reload)
        self.accept(OTPGlobals.AvatarFriendAddEvent, self.reload)
        self.accept(OTPGlobals.AvatarFriendUpdateEvent, self.reload)
        self.accept(OTPGlobals.AvatarFriendRemoveEvent, self.reload)
        self.accept(OTPGlobals.AvatarNewFriendAddEvent, self.reload)
        self.accept('FriendsListManagerAddEvent', self.reload)
        taskMgr.add(self._searchTask, self._searchTaskName)

    def load(self):
        buttonOffset = 2.8

        self.text_sort = DirectLabel(
            parent=self,
            relief=None,
            scale=self.text_panel_scale,
            pos=(0.001, 0, 0.44),
            image=sp_gui.find('**/TitleBarThing'),
            image_scale=(self.text_panel_ratio, 1, 1),
            text='',
            text_pos=(-0.037, -0.178),
            text_scale=0.625,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
        )
        self.text_sort['state'] = DGG.NORMAL

        self.button_sortLeft = DirectButton(
            parent=self.text_sort,
            relief=None,
            image=(sp_gui.find('**/Arrow_N'),
                   sp_gui.find('**/Arrow_P'),
                   sp_gui.find('**/Arrow_H'),
                   sp_gui.find('**/Arrow_D')),
            image_scale=(-self.arrow_button_ratio, 1, 1),
            pos=(-buttonOffset, 0, 0),
            scale=self.arrow_button_scale,
            command=self.sortChange,
            extraArgs=[LEFT],
        )
        self.button_sortRight = DirectButton(
            parent=self.text_sort,
            relief=None,
            image=(sp_gui.find('**/Arrow_N'),
                   sp_gui.find('**/Arrow_P'),
                   sp_gui.find('**/Arrow_H'),
                   sp_gui.find('**/Arrow_D')),
            image_scale=(self.arrow_button_ratio, 1, 1),
            pos=(buttonOffset, 0, 0),
            scale=self.arrow_button_scale,
            command=self.sortChange,
            extraArgs=[RIGHT],
        )

        self.button_configure = DirectButton(
            parent=self,
            relief=None,
            pos=(-0.194, 0, 0.372),
            scale=0.067,
            command=self.toggleConfigure,
            image_scale=(1.2143, 1, 1.0238),
            image=(sp_gui.find('**/Gear_N'),
                   sp_gui.find('**/Gear_P'),
                   sp_gui.find('**/Gear_H')),
            text=('', 'Configure', 'Configure', ''),
            text_scale=0.5,
            text_fg=(1, 1, 1, 1),
            text_bg=(0, 0, 0, 0.56),
            text_shadow=(0, 0, 0, 1),
            text_pos=(-0.05, 0.8),
        )

        self.button_addFriend = DirectButton(
            parent=self,
            relief=None,
            pos=(-0.1188, 0, 0.372),
            scale=0.067,
            command=self.addFriend,
            image_scale=(1.2143, 1, 1.0238),
            image=(sp_gui.find('**/Add_N'),
                   sp_gui.find('**/Add_P'),
                   sp_gui.find('**/Add_H')),
            text=('', 'Add Friend', 'Add Friend', ''),
            text_scale=0.5,
            text_fg=(1, 1, 1, 1),
            text_bg=(0, 0, 0, 0.56),
            text_shadow=(0, 0, 0, 1),
            text_pos=(-0.05, 0.8),
        )

        self.type_searchBar = DirectEntry(
            parent=self,
            relief=None,
            scale=0.051,
            pos=(-0.0748, 0, 0.3632),
            borderWidth=(0.05, 0.05),
            frameColor=((1, 1, 1, 1),
                        (1, 1, 1, 1),
                        (0.5, 0.5, 0.5, 0.5)),
            state=DGG.NORMAL,
            text_align=TextNode.ALeft,
            text_scale=0.7,
            width=8.3,
            numLines=1,
            focus=0,
            backgroundFocus=0,
            cursorKeys=1,
            text_fg=(0, 0, 0, 1),
            autoCapitalize=0,
            image=sp_gui.find('**/TextBox'),
            image_scale=(6.1984, 1, 1.2633),
            image_pos=(2.9857, 0, 0.1968),
            initialText=self.initialSearchText,
            focusInCommand=self._searchFocusIn,
            focusOutCommand=self._searchFocusOut,
            command=self._searchSubmitted,
        )

        self.scroll_friendsList = DirectScrolledFrame(
            parent=self,
            relief=None,
            scale=0.12,
            pos=(0, 0, 0.296),
            frameSize=(-1.931, 1.95, -5.78, 0),
            canvasSize=self.defaultCanvasSize,
            scrollBarWidth=0.3751,
            manageScrollBars=1,
            autoHideScrollBars=0,
            verticalScroll_image=sp_gui.find('**/ScrollBar_BAR'),
            verticalScroll_image_scale=(0.4389, 1, 5.43),
            verticalScroll_image_pos=(1.7645, 0, -2.69),
            verticalScroll_relief=None,
            verticalScroll_thumb_frameColor=(1, 1, 1, 0),
            verticalScroll_resizeThumb=0,
            verticalScroll_thumb_image=sp_gui.find('**/ScrollBar'),
            verticalScroll_thumb_image_scale=(0.3813, 1, 1.35),
            verticalScroll_thumb_image_pos=(0, 0, 0.012),
        )
        self.scroll_friendsList.horizontalScroll.hide()
        self.scroll_friendsList.verticalScroll.incButton.hide()
        self.scroll_friendsList.verticalScroll.decButton.hide()

        self.frame_infoBar = DirectFrame(
            parent=self,
            relief=None,
            pos=(-0.021, 0, 0.318),
            scale=0.05,
            geom=sp_gui.find('**/TitleBarThing'),
            geom_scale=(8.4, 1, 0.8587),
            geom_pos=(-0.0386, 0, 0.0129),
            text='No friends online',
            text_scale=0.7,
            text_pos=(0, -0.2),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_bg=(1, 1, 1, 0),
            frameSize=(-4.3, 1, -0.45, 0.45),
        )
        self.frame_infoBar['state'] = DGG.NORMAL

        self.button_openContext = DirectButton(
            parent=self,
            relief=None,
            command=self.openContextMenu,
            extraArgs=[True],
            pos=(0.212, 0, 0.319),
            scale=0.045,
            image_scale=(1.0315, 1, 1),
            image=(sp_gui.find('**/ARROWBUTTON_N'),
                   sp_gui.find('**/ARROWBUTTON_P'),
                   sp_gui.find('**/ARROWBUTTON_H'),
                   sp_gui.find('**/ARROWBUTTON_D')),
            image_pos=(-0.0032, 0, -0.0257),
            text=('', 'Configure Selected', 'Configure Selected', ''),
            text_scale=0.75,
            text_fg=(1, 1, 1, 1),
            text_bg=(0, 0, 0, 0.67),
            text_shadow=(0, 0, 0, 1),
            text_pos=(-2.62, 0.8),
        )
        self.button_openContext['state'] = DGG.DISABLED

        self.reload()
        self.scroll_friendsList.verticalScroll.setValue(0)

    def destroy(self):
        self.ignoreAll()
        taskMgr.remove(self._searchTaskName)
        self.cleanupContextMenu()
        self._destroyFriendPanels()
        self.panel = None
        DirectFrame.destroy(self)

    def _destroyFriendPanels(self):
        for friendPanel in self.friendPanels:
            try:
                friendPanel.destroy()
            except:
                pass
        self.friendPanels = []
        self.selectedUsers.clear()

    def reload(self, *args):
        self.cleanupContextMenu()
        self._destroyFriendPanels()
        entries = self._getSortedEntries()
        for avId, handle, online in entries:
            name = handle.getName().lower().replace(' ', '')
            search = self.searchText.lower().replace(' ', '')
            if search and search not in name:
                continue
            friendPanel = SocialPanelFriend(
                self.scroll_friendsList,
                handle,
                len(self.friendPanels),
                self,
                configureMode=self.configureMode,
                online=online,
            )
            self.friendPanels.append(friendPanel)
        self._updateCanvas()
        self._updateLabels()
        self._updateButtons()

    def _getFriendAvIds(self):
        result = []

        friends = getattr(base.localAvatar, 'friendsList', [])
        for friend in friends:
            try:
                avId = friend[0]
            except:
                continue
            if avId not in result:
                result.append(avId)

        avatarFriendsManager = getattr(base.cr, 'avatarFriendsManager', None)
        if avatarFriendsManager is not None:
            for avId in getattr(avatarFriendsManager, 'avatarFriendsList', []):
                if avId not in result:
                    result.append(avId)

        return result

    def _getNearbyToons(self):
        result = []
        toonDClass = None
        try:
            toonDClass = base.cr.dclassesByName.get('DistributedToon')
        except:
            pass

        for avId, obj in base.cr.doId2do.items():
            if not hasattr(obj, 'getName'):
                continue

            isToon = False
            try:
                isToon = obj.dclass == toonDClass
            except:
                pass

            if not isToon:
                className = obj.__class__.__name__
                isToon = className == 'DistributedToon' or className.endswith('Toon')

            if not isToon:
                continue
            if getattr(obj, 'ghostMode', 0):
                continue

            result.append((avId, obj, True))
        return result

    def _identifyHandle(self, avId):
        handle = base.cr.identifyFriend(avId)
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

    def _getSortedEntries(self):
        if self.selectedSort == SORT_NEARBY_TOONS:
            entries = self._getNearbyToons()
        else:
            entries = []
            for avId in self._getFriendAvIds():
                online = False
                try:
                    online = bool(base.cr.isFriendOnline(avId))
                except:
                    online = avId in base.cr.doId2do
                if self.selectedSort == SORT_ONLINE_FRIENDS and not online:
                    continue
                handle = self._identifyHandle(avId)
                if handle is not None:
                    entries.append((avId, handle, online))
                else:
                    try:
                        base.cr.fillUpFriendsMap()
                    except:
                        pass
        favorites = set(self.getFavoriteFriends())
        entries.sort(key=lambda entry: (0 if entry[0] in favorites else 1,
                                        entry[1].getName().lower()))
        return entries

    def _updateCanvas(self):
        count = len(self.friendPanels)
        if count > FRIEND_COUNT:
            bottom = -(count * friendYOffset) - self.BOTTOM_PADDING
            canvas = (self.defaultCanvasSize[0], self.defaultCanvasSize[1],
                      bottom, self.defaultCanvasSize[3])
        else:
            canvas = self.defaultCanvasSize
        self.scroll_friendsList['canvasSize'] = canvas
        self.scroll_friendsList.setCanvasSize()
        if count > FRIEND_COUNT:
            self.scroll_friendsList.verticalScroll.show()
        else:
            self.scroll_friendsList.verticalScroll.hide()

    def _updateLabels(self):
        self.text_sort['text'] = self.sortNames[self.selectedSort]
        count = len(self.friendPanels)
        if self.configureMode:
            selectedCount = len(self.selectedUsers)
            if selectedCount == 0:
                text = 'No Toons selected'
            elif selectedCount == 1:
                text = '1 Toon selected'
            else:
                text = '%s Toons selected' % selectedCount
        else:
            if self.selectedSort == SORT_NEARBY_TOONS:
                noun = 'Toon nearby' if count == 1 else 'Toons nearby'
            elif self.selectedSort == SORT_ONLINE_FRIENDS:
                noun = 'friend online' if count == 1 else 'friends online'
            else:
                noun = 'friend total' if count == 1 else 'friends total'
            if count == 0:
                text = 'No %s' % noun
            else:
                text = '%s %s' % (count, noun)
        self.frame_infoBar['text'] = text

    def _updateButtons(self):
        index = self.sortOrder.index(self.selectedSort)
        self.button_sortLeft['state'] = DGG.NORMAL if index > 0 else DGG.DISABLED
        self.button_sortRight['state'] = DGG.NORMAL if index < len(self.sortOrder) - 1 else DGG.DISABLED
        self.button_openContext['state'] = DGG.NORMAL if self.selectedUsers else DGG.DISABLED

    def sortChange(self, direction):
        index = self.sortOrder.index(self.selectedSort) + direction
        if index < 0 or index >= len(self.sortOrder):
            return
        self.selectedSort = self.sortOrder[index]
        self.reload()
        self.scroll_friendsList.verticalScroll.setValue(0)

    def addFriend(self):
        messenger.send('wakeup')
        messenger.send('friendAvatar', [None, None, None])

    def toggleConfigure(self, force=None):
        if force is None:
            self.configureMode = not self.configureMode
        else:
            self.configureMode = bool(force)
        self.selectedUsers.clear()
        for friendPanel in self.friendPanels:
            friendPanel.setConfigure(self.configureMode)
        self.cleanupContextMenu()
        self._updateLabels()
        self._updateButtons()

    def friendButtonClicked(self, friendPanel):
        messenger.send('wakeup')
        messenger.send('clickedNametag', [friendPanel.handle])

    def friendRightClicked(self, friendPanel):
        if not self.configureMode:
            self.toggleConfigure(True)
        if not friendPanel.selected:
            friendPanel.toggleSelected(True)
        self.openContextMenu()

    def friendSelectionChanged(self, friendPanel):
        if friendPanel.selected:
            self.selectedUsers.add(friendPanel)
        elif friendPanel in self.selectedUsers:
            self.selectedUsers.remove(friendPanel)
        if self.selectedUsers and not self.configureMode:
            self.toggleConfigure(True)
        self.cleanupContextMenu()
        self._updateLabels()
        self._updateButtons()

    def _searchFocusIn(self):
        if self.type_searchBar.get() == self.initialSearchText:
            self.type_searchBar.enterText('')

    def _searchFocusOut(self):
        if not self.type_searchBar.get():
            self.type_searchBar.enterText(self.initialSearchText)

    def _searchSubmitted(self, text):
        self._applySearchText(text)

    def _searchTask(self, task):
        text = self.type_searchBar.get()
        self._applySearchText(text)
        return task.cont

    def _applySearchText(self, text):
        if text == self.initialSearchText:
            text = ''
        if text != self.searchText:
            self.searchText = text
            self.reload()

    def cleanupContextMenu(self):
        if self.contextMenu is not None:
            self.contextMenu.destroy()
            self.contextMenu = None
        if self.confirmationMenu is not None:
            self.confirmationMenu.destroy()
            self.confirmationMenu = None

    def openContextMenu(self, fromButton=False):
        if not self.selectedUsers:
            return
        if not base.mouseWatcherNode.hasMouse():
            return

        self.cleanupContextMenu()
        self.contextSelectedUsers = set(self.selectedUsers)
        selected = list(self.contextSelectedUsers)
        one = len(selected) == 1

        if one:
            friendPanel = selected[0]
            isLocalAvatar = friendPanel.avId == base.localAvatar.doId
            isFriend = self._isFriend(friendPanel.avId)
            label = friendPanel.handle.getName()
        else:
            isLocalAvatar = False
            isFriend = self._allSelectedAreFriends()
            label = 'Multiple Toons'

        self.contextMenu = SocialPanelContextDropdown(
            parent=self,
            labelText=label,
            survive=fromButton,
        )

        if one:
            self.contextMenu.addButton('Send Whisper', self.contextWhisper)
            clubMgr = getattr(base.cr, 'clubMgr', None)
            if clubMgr and clubMgr.isInClub() and clubMgr.localAvHasPermission('invite'):
                target = selected[0]
                if target.avId != base.localAvatar.doId and not clubMgr.getMember(target.avId):
                    self.contextMenu.addButton('Invite to Club', self.contextInviteToClub)
            groupMgr = getattr(base.cr, 'groupManager', None)
            if groupMgr and groupMgr.isInGroup():
                target = selected[0]
                group = groupMgr.group or {}
                memberIds = [int(member.get('avId', 0)) for member in group.get('members', [])]
                if target.avId != base.localAvatar.doId and target.avId not in memberIds:
                    self.contextMenu.addButton('Invite to Group', self.contextInviteToGroup)
            if not isLocalAvatar:
                if isFriend:
                    favoriteText = 'Remove Favorite' if self._allSelectedAreFavorites() else 'Add Favorite'
                    self.contextMenu.addButton(
                        favoriteText,
                        self.contextToggleFavorite,
                        red=self._allSelectedAreFavorites(),
                    )
                    self.contextMenu.addButton('Remove Friend', self.contextConfirmRemove, red=True)
                else:
                    self.contextMenu.addButton('Add as Friend', self.contextAddFriend)
        else:
            if isFriend:
                favoriteText = 'Remove Favorites' if self._allSelectedAreFavorites() else 'Mark as Favorites'
                self.contextMenu.addButton(
                    favoriteText,
                    self.contextToggleFavorite,
                    red=self._allSelectedAreFavorites(),
                )
                self.contextMenu.addButton('Remove Friends', self.contextConfirmRemove, red=True)

        if self.contextMenu.getButtonCount() == 0:
            self.cleanupContextMenu()

    def _singleContextSelected(self):
        if len(self.contextSelectedUsers) != 1:
            return None
        return list(self.contextSelectedUsers)[0]

    def _finishContextAction(self, reloadPanel=False):
        self.cleanupContextMenu()
        self.contextSelectedUsers.clear()
        if self.configureMode:
            self.toggleConfigure(False)
        elif reloadPanel:
            self.reload()

    def contextWhisper(self):
        friendPanel = self._singleContextSelected()
        if friendPanel is not None:
            base.localAvatar.chatMgr.whisperTo(
                friendPanel.handle.getName(), friendPanel.avId, None)
        self._finishContextAction()

    def contextInviteToClub(self):
        panel = self._singleContextSelected()
        if panel is None:
            return
        clubMgr = getattr(base.cr, 'clubMgr', None)
        if clubMgr:
            try:
                name = panel.handle.getName()
            except:
                name = ''
            clubMgr.requestInvite(panel.avId, name)
        self._finishContextAction()

    def contextInviteToGroup(self):
        panel = self._singleContextSelected()
        if panel is None:
            return
        groupMgr = getattr(base.cr, 'groupManager', None)
        if groupMgr:
            try:
                name = panel.handle.getName()
            except:
                name = ''
            groupMgr.requestInvite(panel.avId, name)
        self._finishContextAction()

    def contextAddFriend(self):
        friendPanel = self._singleContextSelected()
        if friendPanel is not None and friendPanel.avId != base.localAvatar.doId:
            disableName = 'disable-%s' % friendPanel.avId

            # Prefer the live DistributedToon's disable event.  A projected
            # friend handle can have a different unique-name namespace and
            # make FriendInviter think the Toon disappeared mid-request.
            avatar = base.cr.doId2do.get(friendPanel.avId)
            if avatar is not None and hasattr(avatar, 'uniqueName'):
                disableName = avatar.uniqueName('disable')
            else:
                try:
                    disableName = friendPanel.handle.uniqueName('disable')
                except:
                    pass

            messenger.send('friendAvatar', [friendPanel.avId,
                                            friendPanel.handle.getName(),
                                            disableName])
        self._finishContextAction()

    def contextToggleFavorite(self):
        avIds = [panel.avId for panel in self.contextSelectedUsers
                 if panel.avId != base.localAvatar.doId and self._isFriend(panel.avId)]
        if not avIds:
            self._finishContextAction()
            return
        if self._allSelectedAreFavorites():
            self.removeFavoriteFriends(avIds)
        else:
            self.addFavoriteFriends(avIds)
        self._finishContextAction(reloadPanel=True)

    def contextConfirmRemove(self):
        if not self.contextSelectedUsers:
            return
        if self.contextMenu is not None:
            self.contextMenu.destroy()
            self.contextMenu = None
        self.confirmationMenu = SocialPanelContextDropdown(
            parent=self,
            labelText='Are you sure?',
            survive=True,
        )
        self.confirmationMenu.addButton('Yes', self.contextRemove)
        self.confirmationMenu.addButton('No', self._cancelContextRemove, red=True)

    def _cancelContextRemove(self):
        self._finishContextAction()

    def contextRemove(self):
        avIds = [panel.avId for panel in self.contextSelectedUsers
                 if panel.avId != base.localAvatar.doId and self._isFriend(panel.avId)]
        self.removeFavoriteFriends(avIds)
        self.cleanupContextMenu()
        legacyFriendIds = []
        for friend in getattr(base.localAvatar, 'friendsList', []):
            try:
                legacyFriendIds.append(friend[0])
            except:
                pass
        avatarFriendsManager = getattr(base.cr, 'avatarFriendsManager', None)
        avatarFriendIds = set(getattr(avatarFriendsManager, 'avatarFriendsList', []))

        for avId in avIds:
            if avId in legacyFriendIds:
                try:
                    base.cr.removeFriend(avId)
                except:
                    pass
            if avatarFriendsManager is not None and avId in avatarFriendIds:
                try:
                    avatarFriendsManager.sendRequestRemove(avId)
                except:
                    pass
        self.contextSelectedUsers.clear()
        if self.configureMode:
            self.toggleConfigure(False)
        self.reload()

    def _isFriend(self, avId):
        return avId in self._getFriendAvIds()

    def _allSelectedAreFriends(self):
        if not self.contextSelectedUsers:
            return False
        return all(self._isFriend(panel.avId) for panel in self.contextSelectedUsers)

    def _allSelectedAreFavorites(self):
        if not self.contextSelectedUsers:
            return False
        favorites = set(self.getFavoriteFriends())
        relevant = [panel.avId for panel in self.contextSelectedUsers
                    if panel.avId != base.localAvatar.doId and self._isFriend(panel.avId)]
        return bool(relevant) and all(avId in favorites for avId in relevant)

    def getFavoriteFriends(self):
        try:
            perToonFavorites = settings.get('favoriteFriends', {})
            stored = perToonFavorites.get(str(base.localAvatar.doId), [])
        except:
            stored = []
        favorites = []
        for avId in stored:
            try:
                avId = int(avId)
            except:
                continue
            if avId not in favorites:
                favorites.append(avId)
        return favorites

    def _setFavoriteFriends(self, avIds):
        cleaned = []
        validFriends = set(self._getFriendAvIds())
        for avId in avIds:
            try:
                avId = int(avId)
            except:
                continue
            if avId in validFriends and avId != base.localAvatar.doId and avId not in cleaned:
                cleaned.append(avId)
        try:
            perToonFavorites = dict(settings.get('favoriteFriends', {}))
        except:
            perToonFavorites = {}
        perToonFavorites[str(base.localAvatar.doId)] = cleaned
        settings['favoriteFriends'] = perToonFavorites
        messenger.send('favorite-friends-updated')

    def addFavoriteFriends(self, avIds):
        favorites = self.getFavoriteFriends()
        for avId in avIds:
            if avId not in favorites:
                favorites.append(avId)
        self._setFavoriteFriends(favorites)

    def removeFavoriteFriends(self, avIds):
        removeSet = set(avIds)
        self._setFavoriteFriends([avId for avId in self.getFavoriteFriends()
                                  if avId not in removeSet])

    def isFavorite(self, avId):
        return avId in self.getFavoriteFriends()
