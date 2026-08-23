from direct.gui.DirectGui import *
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import StateData
from pandac.PandaModules import *
from toontown.toonbase import TTLocalizer
from toontown.toon import NPCFriendPanel
from toontown.toon import IOURegistry


class TownBattleSOSPanel(DirectFrame, StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('TownBattleSOSPanel')

    def __init__(self, doneEvent):
        DirectFrame.__init__(self, relief=None)
        self.initialiseoptions(TownBattleSOSPanel)
        StateData.StateData.__init__(self, doneEvent)
        self.chosenNPCToons = []

    def load(self):
        if self.isLoaded == 1:
            return
        self.isLoaded = 1
        sosPanelGui = loader.loadModel('phase_3.5/models/gui/battlegui/sos_panel')
        self['image'] = sosPanelGui.find('**/sos_panel_main')
        self.setScale(1.8)
        self.setPos(0, 0, 0.03)
        self.sosLabel = DirectLabel(
            parent=self,
            relief=None,
            text='IOUs',
            text_pos=(-0.135, 0.105),
            text_scale=0.028
        )
        self.NPCFriendPanel = NPCFriendPanel.NPCFriendPanel(
            parent=self,
            pos=(-0.1245, 0, -0.093),
            scale=0.3,
            doneEvent=self.doneEvent,
            battle=True
        )
        backText = getattr(TTLocalizer, 'TownBattleBack', getattr(TTLocalizer, 'TownBattleSOSBack', 'BACK'))
        self.backButton = DirectButton(
            parent=self,
            relief=None,
            image=(
                sosPanelGui.find('**/back_neutral'),
                sosPanelGui.find('**/back_press'),
                sosPanelGui.find('**/back_hover')
            ),
            text=backText,
            text_fg=(0.157, 0.153, 0.306, 1),
            text_pos=(0.12, -0.03),
            text_scale=0.18,
            pos=(0.2, 0, -0.325),
            scale=0.12,
            command=self.__close
        )
        self.backButton.component('text1').setPos(0.15, -0.054)
        sosPanelGui.removeNode()
        self.hide()

    def unload(self):
        self.ignoreAll()
        if self.isLoaded == 0:
            return None
        self.isLoaded = 0
        self.exit()
        self.NPCFriendPanel.unload()
        del self.NPCFriendPanel
        del self.sosLabel
        del self.backButton
        DirectFrame.destroy(self)

    def enter(self, canLure=1, canTrap=1, isStreet=0):
        if self.isEntered == 1:
            return None
        self.isEntered = 1
        if self.isLoaded == 0:
            self.load()
        self.canLure = canLure
        self.canTrap = canTrap
        self.isStreet = isStreet
        self.factoryToonIdList = None
        messenger.send('SOSPanelEnter', [self])
        self.accept(base.localAvatar.uniqueName('NPCFriendsChange'), self.__updateNPCFriendsPanel)
        self.__updateNPCFriendsPanel()
        self.show()

    def exit(self):
        if self.isEntered == 0:
            return None
        self.isEntered = 0
        self.hide()
        self.ignoreAll()
        messenger.send(self.doneEvent)
        messenger.send('exitNPCFriendPageBattle')

    def __close(self):
        messenger.send(self.doneEvent, [{'mode': 'Back'}])
        messenger.send('exitNPCFriendPageBattle')

    def setFactoryToonIdList(self, toonIdList):
        self.factoryToonIdList = toonIdList[:]

    def __updateNPCFriendsPanel(self):
        ious = {}
        for npcId, count in list(base.localAvatar.NPCFriendsDict.items()):
            if IOURegistry.getIOUByNPCId(npcId) is not None:
                ious[npcId] = count
        self.NPCFriendPanel.update(ious, fCallable=1)
