from direct.fsm import StateData
from toontown.clashbattle.battle import BattleGUIGlobals, BattleGUI
from direct.gui.DirectGui import *
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.statuses import StatusEffects
from toontown.chat.ui.speedchat.TTSCUniteTerminal import TTSCUniteMsgEvent
from toontown.clashbattle.battle import BattleGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class FireCogPanel(StateData.StateData):
    """
    This is the panel used for firing a Cog.
    """

    def __init__(self, doneEvent, townBattle):
        self.notify.debug('Init choose panel...')
        StateData.StateData.__init__(self, doneEvent)
        # How many avatars in the battle?
        self.numAvatars = 0
        # Which was picked?
        self.chosenAvatar = 0
        self.townBattle = townBattle
        # Is this for toons? (or suits?)
        self.toon = 0
        self.loaded = 0

    def load(self):
        self.frame = DirectFrame(relief=None)
        self.frame.hide()

        self.gui = BattleGUI.TargetingGUI(parent=self.frame, townBattle=self.townBattle)
        self.gui.setScale(BattleGUIGlobals.TargetingGuiScale)
        self.gui.activateTargetingMode()

        self.gui.backButton.configure(command=self.__handleBack)

        self.gui.applyFireText(base.localAvatar.getPinkSlips(), True)
        self.gui.emblem.setValues(AttackEnum.TOON_FIRE)
        self.gui.update()

        self.avatarButtons = []
        for i in range(BattleGlobals.MaxBattleAvatars):
            button = BattleGUI.generateTargetingArrow()
            button.reparentTo(self.frame)
            button.configure(command=self.__handleAvatar, extraArgs=[i])
            button.setScale(BattleGUIGlobals.TargetingArrowScale)
            button.setPos(0, 0, BattleGUIGlobals.TargetingArrowHeight)
            self.avatarButtons.append(button)

        self.loaded = 1

    def unload(self):
        del self.townBattle
        if self.loaded:
            self.frame.destroy()
            del self.frame
            del self.gui
            del self.avatarButtons
        self.loaded = 0
        self.ignoreAll()

    def onUniteUsed(self):
        rewardsDisabled = bool(base.localAvatar.getStatusEffectsOfType(StatusEffects.RewardCooldownStatusEffect))
        if self.loaded and rewardsDisabled:
            self.__handleBack()

    def enter(self, numAvatars, localNum = None, luredIndices = None, trappedIndices = None, track = None, fireCosts = None):
        if not self.loaded:
            self.load()
        # Show the panel
        self.frame.show()
        # Place the buttons
        # Suits that are lured should not be available to select for
        # certain attacks
        invalidTargets = []
        if not self.toon:
            if len(luredIndices) > 0:
                # You can't place a trap in front of a suit that is already lured
                if track in (AttackEnum.TOON_TRAP, AttackEnum.TOON_LURE):
                    invalidTargets += luredIndices
            if len(trappedIndices) > 0:
                # You can't place a trap in front of a suit that is already trapped
                if track == AttackEnum.TOON_TRAP:
                    invalidTargets += trappedIndices
        self.__placeButtons(numAvatars, invalidTargets, localNum, fireCosts)
        # Force chat balloons to the margins while this is up.
        # NametagGlobals.setOnscreenChatForced(1)
        self.accept(TTSCUniteMsgEvent, self.onUniteUsed)

    def exit(self):
        # Hide the panel
        self.frame.hide()
        # NametagGlobals.setOnscreenChatForced(0)

    def __handleBack(self):
        doneStatus = {'mode': 'Back'}
        messenger.send(self.doneEvent, [doneStatus])

    def __handleAvatar(self, avatar):
        doneStatus = {'mode': 'Avatar',
         'avatar': avatar}
        messenger.send(self.doneEvent, [doneStatus])

    def adjustCogs(self, numAvatars, luredIndices, trappedIndices, track):
        # Suits that are lured should not be available to select for
        # certain attacks
        invalidTargets = []
        if len(luredIndices) > 0:
            # You can't place a trap in front of a suit that is already lured
            if track in (AttackEnum.TOON_TRAP, AttackEnum.TOON_LURE):
                invalidTargets += luredIndices
        if len(trappedIndices) > 0:
            # You can't place a trap in front of a suit that is already trapped
            if track == AttackEnum.TOON_TRAP:
                invalidTargets += trappedIndices
        self.__placeButtons(numAvatars, invalidTargets, None)
        return

    def adjustToons(self, numToons, localNum):
        self.__placeButtons(numToons, [], localNum)

    def __placeButtons(self, numAvatars, invalidTargets, localNum, fireCosts):
        # Place the buttons. NOTE: Remember, from the toons point of view
        # the avatars are numbered from right to left.

        canfire = 0
        for i in range(BattleGlobals.MaxBattleAvatars):
            # Only show the button if this avatar is in the battle
            # and he is not in the invalidTargets list
            if numAvatars > i and i not in invalidTargets and i != localNum:
                self.avatarButtons[i].show()
                self.avatarButtons[i]['text'] = str(fireCosts[i])
                if fireCosts[i] <= localAvatar.getPinkSlips():
                    self.avatarButtons[i]['state'] = DGG.NORMAL
                    self.avatarButtons[i]['text_fg'] = (0, 0, 0, 1)
                    canfire = 1
                else:
                    self.avatarButtons[i]['state'] = DGG.DISABLED
                    self.avatarButtons[i]['text_fg'] = (1.0, 0, 0, 1)
            else:
                self.avatarButtons[i].hide()

        self.gui.applyFireText(base.localAvatar.getPinkSlips(), canfire)

        # Evenly positions the buttons on the bar
        xSeparation = BattleGUIGlobals.SuitPanelXSpacing
        startingX = (0.5 * (numAvatars - 1)) * xSeparation

        for i in range(numAvatars):
            self.avatarButtons[i].setX(startingX - (i * xSeparation))
