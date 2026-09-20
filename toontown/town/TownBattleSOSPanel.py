from direct.gui.DirectGui import *
from panda3d.core import *
from direct.fsm import StateData

from toontown.clashbattle.battle.statuses import StatusEffects
from toontown.chat.ui.speedchat.TTSCUniteTerminal import TTSCUniteStateChangedEvent
from toontown.toonbase import TTLocalizer
from toontown.toon import NPCFriendPanel
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class TownBattleSOSPanel(DirectFrame, StateData.StateData):
    def __init__(self, doneEvent):
        DirectFrame.__init__(self, relief=None)
        self.initialiseoptions(TownBattleSOSPanel)
        StateData.StateData.__init__(self, doneEvent)
        self.textRolloverColor = Vec4(1, 1, 0, 1)
        self.textDownColor = Vec4(0.5, 0.9, 1, 1)
        self.textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)
        self.chosenNPCToons = []

    def load(self):
        if self.isLoaded == 1:
            return
        self.isLoaded = 1
        sosPanelGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/sos_panel')
        self['image'] = sosPanelGui.find('**/sos_panel_main')
        self.setScale(1.8)
        self.setPos(0, 0, 0.03)

        # Sos Card Title
        self.sosLabel = DirectLabel(
            parent=self,
            relief=None,
            text='IOUs',
            text_pos=(-0.135, 0.105),
            text_scale=0.028
        )

        # Sos Card List
        self.NPCFriendPanel = NPCFriendPanel.NPCFriendPanel(
            parent=self,
            pos=(-0.1245, 0, -0.093),
            scale=0.3,
            doneEvent=self.doneEvent,
            battle=True
        )

        # Back Button
        self.backButton = DirectButton(
            parent=self,
            relief=None,
            image=(
                sosPanelGui.find('**/back_neutral'),
                sosPanelGui.find('**/back_press'),
                sosPanelGui.find('**/back_hover')
            ),
            text=TTLocalizer.TownBattleBack,
            text_fg=(0.157, 0.153, 0.306, 1),
            text_pos=(0.12, -0.03),
            text_scale=0.18,
            pos=(0.2, 0, -0.325),
            scale=0.12,
            command=self.__close
        )
        # Position pressed text
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
        DirectFrame.destroy(self)
        del self.sosLabel
        del self.backButton

    def onUniteUsed(self):
        rewardsDisabled = bool(base.localAvatar.getStatusEffectsOfType(StatusEffects.RewardCooldownStatusEffect))
        if self.isLoaded and rewardsDisabled:
            self.__close()

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
        self.__updateNPCFriendsPanel()
        self.show()
        self.accept('LocalInventorySet', self.__updateNPCFriendsPanel)
        self.accept(TTSCUniteStateChangedEvent, self.onUniteUsed)

    def exit(self):
        if self.isEntered == 0:
            return None
        self.isEntered = 0
        self.hide()
        self.ignoreAll()
        messenger.send(self.doneEvent)
        messenger.send('exitNPCFriendPageBattle')  # Tell the battle sos dialog box to clean itself up

    def __close(self):
        doneStatus = {}
        doneStatus['mode'] = 'Back'
        messenger.send(self.doneEvent, [doneStatus])
        messenger.send('exitNPCFriendPageBattle')  # Tell the battle sos dialog box to clean itself up

    def setFactoryToonIdList(self, toonIdList):
        self.factoryToonIdList = toonIdList[:]

    def __updateNPCFriendsPanel(self):
        # We don't need to do any special checks here anymore, since we only have power up cards
        self.NPCFriendPanel.update(base.localAvatar.getIOUs(), fCallable=1)
