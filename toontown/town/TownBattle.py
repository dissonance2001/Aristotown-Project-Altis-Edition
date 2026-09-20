from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.fsm import StateData
from direct.gui.DirectGui import DGG
from direct.showbase import PythonUtil
from direct.interval.IntervalGlobal import *
from direct.showbase.MessengerGlobal import messenger

from toontown.clashbattle.battle import BattleBase
from toontown.clashbattle.battle import BattleGUI, BattleGUIGlobals
from toontown.clashbattle.battle import FireCogPanel
from toontown.clashbattle.battle import SueCogPanel
from toontown.clashbattle.battle.BattleAvatar import BattleAvatar
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.statuses import StatusEffects
from toontown.clashbattle.battle.statuses.StatusEffectEnums import *
from toontown.clashbattle.battle.statuses.StatusEffects import ObscureInformationStatusEffect, ZapCanJump, ZapDealsBoostedDamage, \
    LureStatusEffect, TrappedStatusEffect, FrozenStatusEffect, UntouchableStatusEffect
from toontown.toonbase import ToontownTimer
from toontown.clashbattle.battle.BattleGlobals import *
from toontown.gui import TTDialog
from toontown.gui.ScaledFrame import ScaledFrame
from toontown.town import TownBattleAttackPanel
from toontown.town import TownBattleChooseAvatarPanel
from toontown.town import TownBattleCogPanel
from toontown.town import TownBattleToonPanel
from toontown.town import TownBattleWaitPanel
from toontown.town.TownBattleSOSPanel import TownBattleSOSPanel
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class TownBattle(StateData.StateData):
    def __init__(self, doneEvent):
        StateData.StateData.__init__(self, doneEvent)

        self.battle = None
        self.numCogs = 1
        self.cogs = []
        self.creditLevel = None
        self.luredIndices = []
        self.trappedIndices = []
        self.suedIndices = []
        self.untouchableToonIndices = []
        self.untouchableSuitIndices = []
        self.untouchableByTrapSuitIndices = []
        self.numToons = 1
        self.toons = []
        self.localNum = 0
        self.time = 0
        self.isStreet = 0
        self.clockTick = None
        self.track = -1
        self.level = -1
        self.lockIn = 0
        self.target = 0
        self.surrendered = False
        self.surrenderedToons = []
        self.toonAttacks = [(-1, 0, 0)] * 4
        self.fsm = ClassicFSM.ClassicFSM('TownBattle', [State.State('Off', self.enterOff, self.exitOff, ['Attack']),
         State.State('Attack', self.enterAttack, self.exitAttack, ['ChooseCog', 'ChooseToon', 'AttackWait', 'Run',
                                                                   'Afk', 'Fire', 'Sue', 'SOS', 'Counterfeit', 'Surrender']),
         State.State('ChooseCog', self.enterChooseCog, self.exitChooseCog, ['AttackWait', 'Attack']),
         State.State('AttackWait', self.enterAttackWait, self.exitAttackWait, ['ChooseCog', 'ChooseToon', 'Attack']),
         State.State('ChooseToon', self.enterChooseToon, self.exitChooseToon, ['AttackWait', 'Attack']),
         State.State('Run', self.enterRun, self.exitRun, ['Attack']),
         State.State('Afk', self.enterAfk, self.exitAfk, ['Attack']),
         State.State('SOS', self.enterSOS, self.exitSOS, ['Attack', 'AttackWait', 'ChooseToon']),
         State.State('Fire', self.enterFire, self.exitFire, ['Attack', 'AttackWait']),
         State.State('Sue', self.enterSue, self.exitSue, ['Attack', 'AttackWait']),
         State.State('Counterfeit', self.enterCounterfeit, self.exitCounterfeit, ['Attack', 'AttackWait', 'Run', 'SOS', 'Fire',
                                                                                  'Sue', 'Surrender']),
         State.State('Surrender', self.enterSurrender, self.exitSurrender, ['Attack'])], 'Off', 'Off')
        self.runPanel = TTDialog.TTDialog(dialogName='TownBattleRunPanel',
                                          text=TTLocalizer.TownBattleRun,
                                          style=TTDialog.TwoChoice,
                                          command=self.__handleRunPanelDone)
        self.runPanel.hide()
        self.surrenderPanel = TTDialog.TTDialog(dialogName='TownBattleSurrenderPanel',
                                                text=TTLocalizer.TownBattleSurrenderVote.format(votecase=TTLocalizer.TownBattleSurrenderVoteUnanimously),
                                                style=TTDialog.TwoChoice,
                                                command=self.__handleSurrenderPanelDone)
        self.surrenderPanel.hide()
        self.attackPanelDoneEvent = 'attack-panel-done'
        self.attackPanel = TownBattleAttackPanel.TownBattleAttackPanel(self.attackPanelDoneEvent)
        self.waitPanelDoneEvent = 'wait-panel-done'
        self.lockInEvent = 'lock-in-request'
        self.gagChangeEvent = 'gag-change-event'
        self.waitPanel = TownBattleWaitPanel.TownBattleWaitPanel(self.waitPanelDoneEvent, self.lockInEvent, self.gagChangeEvent, townBattle=self)
        self.chooseCogPanelDoneEvent = 'choose-cog-panel-done'
        self.chooseCogPanel = TownBattleChooseAvatarPanel.TownBattleChooseAvatarPanel(self.chooseCogPanelDoneEvent, 0, self.gagChangeEvent, townBattle=self)
        self.chooseToonPanelDoneEvent = 'choose-toon-panel-done'
        self.chooseToonPanel = TownBattleChooseAvatarPanel.TownBattleChooseAvatarPanel(self.chooseToonPanelDoneEvent, 1, self.gagChangeEvent, townBattle=self)
        self.SOSPanelDoneEvent = 'SOS-panel-done'
        self.SOSPanel = TownBattleSOSPanel(self.SOSPanelDoneEvent)
        self.fireCogPanelDoneEvent = 'fire-cog-panel-done'
        self.FireCogPanel = FireCogPanel.FireCogPanel(self.fireCogPanelDoneEvent, townBattle=self)
        self.sueCogPanelDoneEvent = 'sue-cog-panel-done'
        self.SueCogPanel = SueCogPanel.SueCogPanel(self.sueCogPanelDoneEvent, townBattle=self)
        self.counterfeitDoneEvent = 'counterfeit-done'
        self.resizeEvent = 'aspectRatioChanged'
        self.cogFireCosts = [1] * MaxBattleAvatars
        self.cogSueCosts = [1] * MaxBattleAvatars
        self.afkToons = []
        self.afkPanel = None

        # These are not Statedatas, so they have no doneEvents
        self.toonPanels = list((TownBattleToonPanel.TownBattleToonPanel(self) for _ in range(4)))
        self.cogPanels = list((TownBattleCogPanel.TownBattleCogPanel(self) for _ in range(MaxBattleAvatars)))
        self.informationPanel = BattleGUI.MasterInformationPanel()

        self.timer = ToontownTimer.ToontownTimer()
        self.timer.reparentTo(base.a2dBottomRight)
        self.timer.setPos(*BattleGUIGlobals.BattleTimerPos)
        self.timer.setScale(BattleGUIGlobals.BattleTimerScale)
        self.timer.bind(DGG.WITHIN, self.__handleWithinTimer)
        self.timer.bind(DGG.WITHOUT, self.__handleWithoutTimer)
        self.timer['state'] = DGG.NORMAL
        self.timer.hide()
        self.timeRunningOutSfx = loader.loadSfx('phase_3.5/audio/sfx/round_running_out.ogg')
        self.timeRunningOutTrack = None

        self.roundCount = ScaledFrame(parent=base.a2dBottomRight, relief=None, pos=(-0.163, 0, 0.31), scale=0.35,
                                      frameSize=(-1.05, 1.05, -0.15, 0.15), text='Round 1', text_scale=0.14,
                                      text_pos=(0, -0.05), wantClipElements=False,
                                      text_fg=(1, 1, 1, 1), text_font=getMinnieFont(), borderScale=0.03,
                                      scaledTexture='phase_3/maps/gui/ttcc_gui_scaledFrame_shadow.png')
        self.roundCount.hide()
        self.roundCountSeq = None

    def cleanup(self):
        self.ignoreAll()
        self.unload()
        self.surrenderedToons = []
        del self.fsm
        self.runPanel.cleanup()
        del self.runPanel
        if self.afkPanel:
            self.afkPanel.cleanup()
            del self.afkPanel
        del self.attackPanel
        del self.waitPanel
        del self.chooseCogPanel
        del self.chooseToonPanel
        del self.SOSPanel
        del self.FireCogPanel
        del self.SueCogPanel
        self.informationPanel.cleanup()
        del self.informationPanel
        for toonPanel in self.toonPanels:
            toonPanel.cleanup()

        del self.toonPanels
        for cogPanel in self.cogPanels:
            cogPanel.cleanup()

        del self.cogPanels
        self.timer.destroy()
        del self.timer
        del self.cogs
        del self.toons
        del self.battle
        if self.timeRunningOutTrack:
            self.timeRunningOutTrack.finish()
        del self.timeRunningOutTrack
        del self.timeRunningOutSfx

        if self.roundCountSeq:
            self.roundCountSeq.finish()
        self.roundCountSeq = None
        if self.roundCount:
            self.roundCount.destroy()
        self.roundCount = None

    def enter(self, event, parentFSMState, isStreet = False, creditMultiplier = 1, tutorialFlag = 0):
        self.parentFSMState = parentFSMState
        if not self.isLoaded:
            self.load()
        self.notify.debug(f'Battle Event: {event} parentFSMState: {parentFSMState} isStreet {isStreet} credMult: {creditMultiplier} tutorialFlag: {tutorialFlag}')
        self.battleEvent = event
        self.fsm.enterInitialState()
        base.localAvatar.laffMeter.start()
        self.numToons = 1
        self.numCogs = 1
        self.toons = [base.localAvatar]
        self.toonPanels[0].setLaffMeter(base.localAvatar)
        self.isStreet = isStreet
        if isStreet:
            textStr = TTLocalizer.TownBattleAfk
            buttonTextList = TTLocalizer.TownBattleAfkChoices
            style = TTDialog.TwoChoice
        else:
            textStr = TTLocalizer.TownBattleAfkNoRun
            buttonTextList = [TTLocalizer.TownBattleAfkChoices[0]]
            style = TTDialog.Acknowledge
        self.afkPanel = TTDialog.TTDialog(dialogName='TownBattleAfkPanel',
                                          text=textStr,
                                          buttonTextList=buttonTextList,
                                          style=style,
                                          command=self.__handleAfkPanelDone)
        self.afkPanel.hide()
        self.creditLevel = None
        self.creditMultiplier = creditMultiplier
        self.tutorialFlag = tutorialFlag
        base.localAvatar.inventory.setActivateMode('battle', heal=0, isStreet=isStreet, tutorialFlag=tutorialFlag)
        base.localAvatar.inventory.fixRewardButtonPos()

    def exit(self):
        if hasattr(self, 'toonPanels'):
            for toonPanel in self.toonPanels:
                toonPanel.cleanupLaffMeterAndNametag()
                toonPanel.setLockIn(False)
                toonPanel.updateSurrenderState(False, instant=True)
        if hasattr(self, 'base') or True:
            base.localAvatar.laffMeter.stop()
        if hasattr(self, 'informationPanel'):
            self.informationPanel.clearPanel()
        if hasattr(self, 'parentFSMState'):
            del self.parentFSMState
        if self.isStreet:
            base.localAvatar.inventory.countInvasions = True
        base.localAvatar.inventory.setActivateMode('book', isStreet=self.isStreet)
        base.localAvatar.inventory.setLiveCreditMult()

    def load(self):
        if self.isLoaded:
            return
        self.attackPanel.load()
        self.waitPanel.load()
        self.chooseCogPanel.load()
        self.chooseToonPanel.load()
        self.isLoaded = 1

    def unload(self):
        if not self.isLoaded:
            return
        self.attackPanel.unload()
        self.waitPanel.unload()
        self.chooseCogPanel.unload()
        self.chooseToonPanel.unload()
        self.FireCogPanel.unload()
        self.SOSPanel.unload()
        self.SueCogPanel.unload()
        self.isLoaded = 0

    def setState(self, state):
        # The distributed battle does some set states after the
        # localtoon has left the battle and this fsm has been deleted
        if hasattr(self, 'fsm'):
            self.fsm.request(state)

    def updateTimer(self, timescale, time, runoutTime):
        self.time = time
        if timescale < (runoutTime / 10):
            if time == round(10 * timescale):
                if not (self.timeRunningOutTrack and self.timeRunningOutTrack.isPlaying()):
                    self.timeRunningOutSfx.setPlayRate(1.0)
                    self.startTimeRunningOutTrack()
                    self.timeRunningOutSfx.play()
        else:
            if not (self.timeRunningOutTrack and self.timeRunningOutTrack.isPlaying()):
                self.timeRunningOutSfx.setPlayRate(timescale / (runoutTime / 10))
                self.startTimeRunningOutTrack()
                self.timeRunningOutSfx.play()
        self.timer.setTime(time)

    def startTimeRunningOutTrack(self):
        if self.timeRunningOutTrack:
            self.timeRunningOutTrack.finish()

        shakeInterval = Sequence()
        for _ in range(10):
            shakeInterval.append(LerpHprInterval(self.timer, 0.025, 15))
            shakeInterval.append(LerpHprInterval(self.timer, 0.025, 0))
            shakeInterval.append(LerpHprInterval(self.timer, 0.025, -15))
            shakeInterval.append(LerpHprInterval(self.timer, 0.025, 0))

        self.timeRunningOutTrack = Parallel(
            SoundInterval(self.timeRunningOutSfx),
            shakeInterval)
        self.timeRunningOutTrack.start()

    def stopTimerSound(self):
        if hasattr(self, 'timeRunningOutPulseTrack') and self.timeRunningOutPulseTrack:
            self.timeRunningOutPulseTrack.finish()
        if self.timeRunningOutTrack:
            self.timeRunningOutTrack.finish()
        if self.clockTick is not None:
            self.clockTick.pause()
            self.clockTick = None

    def __cogPanels(self, num):
        for panel in self.cogPanels:
            panel.hide(hidByBattle=True)
            panel.setPos(0, 0, BattleGUIGlobals.SuitPanelHeight)

        for i in range(num):
            self.cogPanels[i].setScale(1)
            self.cogPanels[i].show()

    def __enterPanels(self, num, localNum):
        self.notify.debug('enterPanels() num: %d localNum: %d' % (num, localNum))
        # Hide all the toon panels, and position them low on the screen
        for toonPanel in self.toonPanels:
            toonPanel.hide(hidByBattle=True)
            toonPanel.setPos(0, 0, BattleGUIGlobals.ToonPanelHeight)

        for i in range(num):
            self.toonPanels[i].setScale(1)
            self.toonPanels[i].show()
            self.toonPanels[i].set3dNametagVisiblity(False)

        # Ensure all of our hidden panels have their values cleared.
        # hidByBattle flag used to prevent crashes from pressing F3 to hide GUI.
        hiddenPanels = [panel for panel in self.toonPanels if panel.isHidden() and panel.hidByBattle]
        for panel in hiddenPanels:
            panel.cleanupLaffMeterAndNametag()
            panel.setValues(self.toonPanels.index(panel), AttackEnum.TOON_UN_ATTACK)

    def updatePanelsForAspectRatio(self):
        # If possible, avoid touching this code. It's not the greatest.
        toonPanels = [panel for panel in self.toonPanels if not (panel.isHidden() and panel.hidByBattle)]
        cogPanels = [panel for panel in self.cogPanels if not (panel.isHidden() and panel.hidByBattle)]
        numToonPanels = len(toonPanels)
        numCogPanels = len(cogPanels)
        maxScale = (16. / 9.)
        userScale = base.getAspectRatio() / maxScale
        # Effectively 1.0, but easier to understand the aspect ratio this way
        minScale = (3. / 3.)
        minScaleFactor = minScale / maxScale
        maxScaleFactor = 1.0
        scaleFactor = max(min(userScale, maxScaleFactor), minScaleFactor)

        # Calculate how far our user's aspect ratio is within our bounds of 3:3 and 16:9.
        maxDiff = maxScaleFactor - minScaleFactor
        userDiff = maxScaleFactor - scaleFactor
        diffRatio = min(userDiff / maxDiff, 1.0)

        # Slightly move the panel downwards to keep it at the correct place in reference to the bottom of the screen.
        minDownZ = 0
        maxDownZ = 0.05
        subtractAmount = lerp(minDownZ, maxDownZ, diffRatio)

        # Create a custom separation amount based on our scale factor
        xSeparationToon = BattleGUIGlobals.ToonPanelXSpacing * scaleFactor
        xSeparationSuit = BattleGUIGlobals.SuitPanelXSpacing * scaleFactor
        startingXToon = (0.5 * (numToonPanels - 1)) * xSeparationToon
        startingXSuit = (0.5 * (numCogPanels - 1)) * xSeparationSuit

        # Put the toon and cog panels each in the right places with the values we just calculated.
        for toonPanel in toonPanels:
            toonPanel.setX(startingXToon - (toonPanels.index(toonPanel) * xSeparationToon))
            toonPanel.setZ(BattleGUIGlobals.ToonPanelHeight - subtractAmount)
            toonPanel.setScale(scaleFactor)
        for cogPanel in cogPanels:
            cogPanel.setX(startingXSuit - (cogPanels.index(cogPanel) * xSeparationSuit))
            cogPanel.setZ(BattleGUIGlobals.SuitPanelHeight)
            cogPanel.setScale(scaleFactor)

        # Make sure the inventory fits within the bounds of the screen on terrible aspect ratios.
        minInvScale = 0.85
        maxInvScale = 1.0
        # Make our own scale factor here, with 4:3 as the minimum instead of 3:3, or 1.0.
        minInvScaleFactor = (4. / 3.) / maxScale
        invMaxDiff = maxScaleFactor - minInvScaleFactor
        invDiffRatio = min(userDiff / invMaxDiff, 1.0)
        invScale = lerp(maxInvScale, minInvScale, invDiffRatio)
        base.localAvatar.inventory.setScale(invScale)
        # Set the scale factors for each of these so that the selection arrows are in the correct places.
        self.chooseCogPanel.spacingModifier = scaleFactor
        self.chooseCogPanel.adjustCogs(self.numCogs, self.luredIndices, self.trappedIndices, self.track,
                                       self.untouchableSuitIndices)
        self.chooseToonPanel.spacingModifier = scaleFactor
        self.chooseToonPanel.adjustToons(self.numToons, self.toons, self.localNum, self.untouchableToonIndices)

    def updateChosenAttacks(self, battleIndices, tracks, levels, targets):
        """
        toonIndices: The battle indices for these parallel arrays
        tracks: An array of four tracks, one for each player
        levels: An array of four levels, one for each player
        targets: An array for four indices, either toon or suit, depending
        """
        self.notify.debug('updateChosenAttacks bi=%s tracks=%s levels=%s targets=%s' % (
            battleIndices,
            tracks,
            levels,
            targets,
        ))

        # Build unique strings for Zap ordering.
        if self.battle:
            soakedSuits = self._getSoakedSuits(tracks, levels, targets)
            zapTargetDict = self._getZapTargetDict(battleIndices, tracks, levels, targets, soakedSuits)
            splashedSuits = self._getSplashTargetDict(battleIndices, tracks, levels, targets)
            luredSuits = self._getLuredSuits(tracks, levels, targets, zapTargetDict)
            markedSuits = self._getMarkedSuits(tracks, targets)
        else:
            soakedSuits = []
            zapTargetDict = {}
            splashedSuits = {}
            luredSuits = {}
            markedSuits = []

        # Update each toon's panels.
        for i in range(4):
            # Determine the number of possible targets for this attack,
            # and whether it is a group attack
            cogSoaked = False
            if battleIndices[i] == -1:
                pass
            else:
                if tracks[i] == AttackEnum.TOON_NO_ATTACK:
                    numTargets = 0
                    target = -2
                elif tracks[i] == AttackEnum.TOON_PASS:
                    numTargets = 0
                    target = -2
                elif tracks[i] == AttackEnum.TOON_NPC:
                    numTargets = self.numToons
                    target = targets[i]
                    if target == -1:
                        numTargets = None
                elif tracks[i] == AttackEnum.TOON_HEAL:
                    # A heal
                    numTargets = self.numToons
                    if self.__isGroupHeal(levels[i]):
                        # -2 means group heal
                        target = -2
                    else:
                        target = targets[i]
                elif tracks[i] == AttackEnum.TOON_SQUIRT:
                    numTargets = self.numCogs
                    if i in splashedSuits:
                        target = splashedSuits[i]
                    else:
                        target = [targets[i]]
                elif tracks[i] == AttackEnum.TOON_ZAP:
                    numTargets = self.numCogs
                    if i in zapTargetDict.keys():
                        target = zapTargetDict[i]
                        if soakedSuits[target[0]]:
                            cogSoaked = True
                    else:
                        target = [targets[i]]
                else:
                    # An attack
                    numTargets = self.numCogs
                    if self.__isGroupAttack(tracks[i], levels[i]):
                        # -1 means group attack
                        target = -1
                    else:
                        target = targets[i]
                        if target == -1:
                            # We haven't chosen a target yet.
                            numTargets = None
                self.toonPanels[battleIndices[i]].setValues(
                    battleIndices[i], tracks[i], levels[i], numTargets, target,
                    self.localNum, soaked=cogSoaked,
                    luredSuits=luredSuits, markedSuits=markedSuits, soakedSuits=soakedSuits,
                    untouchableIndices=self.untouchableSuitIndices,
                    untouchableByTrapIndices=self.untouchableByTrapSuitIndices, townBattle=self)

    def _checkSuitsForStatusEffects(self, statusEffectClass) -> list:
        """
        Given a statusEffectId, it will return a list of all
        of the suits that have that given status effect.

        :param statusEffectId: A status effect ID.
        :return: List of the form [False, True, ... ]. True if that suit index has the effect, False otherwise.
        """
        retList = []
        for i in range(len(self.battle.suits)):
            if self.cogPanels[i].cog and \
                self.cogPanels[i].cog.getStatusEffectOfType(statusEffectClass):
                retList.append(True)
            else:
                retList.append(False)
        return retList

    def _checkToonsForStatusEffects(self, statusEffectClass) -> list:
        """
        Given a statusEffectId, it will return a list of all
        of the suits that have that given status effect.

        :param statusEffectId: A status effect ID.
        :return: List of the form [False, True, ... ]. True if that suit index has the effect, False otherwise.
        """
        retList = []
        for i in range(len(self.battle.toons)):
            if self.toonPanels[i].avatar and \
                self.toonPanels[i].avatar.getStatusEffectOfType(statusEffectClass):
                retList.append(True)
            else:
                retList.append(False)
        return retList

    def _getSoakedSuits(self, tracks, levels, targets):
        # Gets a list of soaked suits.
        soakedSuits = self._checkSuitsForStatusEffects(ZapDealsBoostedDamage)
        realSoakedSuits = [all([soakedSuits[n], (n not in self.untouchableSuitIndices)]) for n in
                           range(len(soakedSuits))]
        # Consider gags toons have picked.
        for i, track in enumerate(tracks):
            if track == AttackEnum.TOON_SQUIRT and targets[i] != -1:
                target = targets[i]
                realSoakedSuits[target] = True
                if i >= len(self.battle.toons):
                    continue
                if target != 0:
                    realSoakedSuits[target - 1] = True
                if target < len(self.battle.suits) - 1:
                    realSoakedSuits[target + 1] = True
        return realSoakedSuits

    def _getMarkedSuits(self, tracks, targets):
        # Gets a list of marked suits.
        markedSuits = []
        for i, track in enumerate(tracks):
            if track == AttackEnum.TOON_THROW and targets[i] != -1:
                markedSuits.append(targets[i])
        return markedSuits

    def _getLuredSuits(self, tracks, levels, targets, zapTargetDict):
        # Gets a list of lured suits.
        luredSuits = {}  # Each key will be a suit's doId to minimize confusion later
        for i in range(len(self.battle.suits)):
            suit = self.cogPanels[i].cog
            if not suit:
                continue
            # Get our Lure SE
            lure = suit.getStatusEffectOfType(LureStatusEffect)
            kbDmg = int(lure.knockback) if lure else 0
            luredSuits[suit.doId] = {
                'knockback': kbDmg,  # This will be 0 if the suit isn't lured, or the knockback damage
                'unluredBy': 0,
                # Similarly, this will remain 0 if we determine the suit will remain lured through the round
                'unluredByTrack': None  # This will be the track that unlures the suit, if any
            }
        # NOW, we will consider the various gag tracks toons have picked.
        # Check for all lure uses first.
        for i, track in enumerate(tracks):
            if i >= len(self.battle.toons) or track in [AttackEnum.TOON_HEAL, AttackEnum.TOON_DROP]:
                continue
            # For no particular reason, let's do lure first.
            if track == AttackEnum.TOON_LURE:
                # First we'll want to grab the knockback damage
                toon = self.battle.toons[i]
                kbDamage = getAvPropDamage(
                    track, levels[i], toon.getExperience()[track],
                    toon.getTrackBonusLevel(track) >= 1
                )

                def handleLureBoost(kbDamage):
                    if self.toonPanels:
                        kbDamage = self.toonPanels[0].getGeneralDamageModifiers(
                            attackTrack=AttackEnum.TOON_LURE,
                            suitIndex=targets[i],
                            damage=kbDamage,
                            markedSuits=None,
                        )
                    for boost in toon.getStatusEffectsOfType(StatusEffects.LureKnockbackModifierStatusEffect):
                        kbDamage = boost.handleLureKb(kbDamage)
                    return int(math.ceil(round(kbDamage, 4)))

                trapIndex = self.battle.getGagOrder().index(AttackEnum.TOON_TRAP)

                # Then we can calculate if it's a single lure
                if AvPropTargetCat[0][levels[i]] == ATK_SINGLE_TARGET:
                    if targets[i] == -1:
                        continue
                    # We'll check for a Trap SE here to see if the suit is already trapped
                    suit = self.cogPanels[targets[i]].cog
                    if not suit:
                        continue
                    if suit.doId not in luredSuits:
                        continue
                    # Here we'll check if the suit getting lured is trapped already, and set its unluredBy to Trap if so
                    if luredSuits[suit.doId]['unluredBy'] != trapIndex and suit.getStatusEffectOfType(
                        TrappedStatusEffect):
                        luredSuits[suit.doId]['unluredBy'] = trapIndex
                        luredSuits[suit.doId]['unluredByTrack'] = AttackEnum.TOON_TRAP

                    # Make sure we're not overwriting a bigger lure in doing this
                    if kbDamage > luredSuits[suit.doId]['knockback']:
                        luredSuits[suit.doId]['knockback'] = handleLureBoost(kbDamage)
                # Or a group lure
                else:
                    for target in luredSuits:
                        suit = base.cr.doId2do.get(target)  # Weird way to do this here but whatever
                        if not suit:
                            continue
                        # Do not consider suits which are already lured.
                        if suit.getStatusEffectOfType(LureStatusEffect):
                            continue
                        # We'll do the same check here but for every suit
                        if luredSuits[target]['unluredBy'] != trapIndex and suit.getStatusEffectOfType(
                            TrappedStatusEffect):
                            luredSuits[target]['unluredBy'] = trapIndex
                            luredSuits[target]['unluredByTrack'] = AttackEnum.TOON_TRAP
                        if kbDamage > luredSuits[target]['knockback']:
                            luredSuits[target]['knockback'] = handleLureBoost(kbDamage)

        # Then do a second pass for all other non-Lure gags.
        for i, track in enumerate(tracks):
            if i >= len(self.battle.toons) or track in [AttackEnum.TOON_HEAL, AttackEnum.TOON_DROP]:
                continue
            # Use the index of the track in the gag track order when possible.
            if track in self.battle.getGagOrder():
                trackIndex = self.battle.getGagOrder().index(track)
            else:
                trackIndex = track
            # Now that that's out of the way, let's go back and do trap
            if track == AttackEnum.TOON_TRAP:
                if targets[i] == -1:
                    continue
                # Ugly check to prevent crashes
                suit = self.cogPanels[targets[i]].cog
                if not suit:
                    continue
                suitId = suit.doId
                if suitId not in luredSuits:
                    continue
                if luredSuits[suitId]['knockback']:
                    luredSuits[suitId]['unluredBy'] = trackIndex  # We'll mark it as unlured by trap
                    luredSuits[suitId]['unluredByTrack'] = track
            # Sound seems to be next on my list
            elif track == AttackEnum.TOON_SOUND:
                # Sound will unlure all the cogs :( sad
                for target in luredSuits:
                    if luredSuits[target]['unluredBy'] > trackIndex or not luredSuits[target]['unluredBy']:
                        luredSuits[target]['unluredBy'] = trackIndex
                        luredSuits[target]['unluredByTrack'] = track
            # Continuing the pattern of skipping every other track, let's do zap next
            elif track == AttackEnum.TOON_ZAP:
                if i in zapTargetDict:
                    targetList = zapTargetDict[i]  # We'll get our targets from the zap dict
                    for target in targetList:
                        # Ugly check to prevent crashes
                        suit = self.cogPanels[target].cog
                        if not suit:
                            continue
                        suitId = suit.doId
                        if suitId not in luredSuits:
                            continue
                        if luredSuits[suitId]['unluredBy'] > trackIndex or not luredSuits[suitId]['unluredBy']:
                            luredSuits[suitId]['unluredBy'] = trackIndex
                            luredSuits[suitId]['unluredByTrack'] = track
            # Now let's do drop-- hehe, just kidding of course :) we'll finish by doing throw and squirt
            elif track in (AttackEnum.TOON_SQUIRT, AttackEnum.TOON_THROW):
                if targets[i] == -1:
                    continue
                # Ugly check to prevent crashes
                suit = self.cogPanels[targets[i]].cog
                if not suit:
                    continue
                suitId = suit.doId
                if suitId not in luredSuits:
                    continue
                if luredSuits[suitId]['unluredBy'] > trackIndex or not luredSuits[suitId]['unluredBy']:
                    luredSuits[suitId]['unluredBy'] = trackIndex
                    luredSuits[suitId]['unluredByTrack'] = track
        return luredSuits

    @staticmethod
    def _getGagOrderedList(battleIndices, tracks, levels, targets, track_find):
        """
        Get a list of battle indices checking some gag levels.
        If player 1 is using gag level 3, and players 0 and 2 are using gag level 7,
        and player 3 is not using track_find, then build the list [1, 0, 2].
        Used especially for calculating Zap gag order.
        """
        levelsUsed = set()
        retList = []
        # Add each gag level used into the levelsUsed set
        for i, usedTrack in enumerate(tracks):
            if usedTrack == track_find:
                levelsUsed.add(levels[i])
        # No levels were detected, return an empty list
        if not levelsUsed:
            return []
        levelsUsed = list(levelsUsed)  # convert from set to list
        levelsUsed.sort()  # Lowest to highest
        for level in levelsUsed:
            for i, indice in enumerate(battleIndices):
                if indice != -1:  # Existing player check
                    if tracks[i] == track_find and levels[i] == level and targets[i] != -1:
                        retList.append(indice)
        return retList

    def _getCogHP(self):
        # Returns list of current cog HPs
        return [suit.hp for suit in self.battle.suits]

    def _getZapTargetDict(self, battleIndices, tracks, levels, targets, soakedSuits):
        retDict = {}
        zapOrderedList = self._getGagOrderedList(battleIndices, tracks, levels, targets, AttackEnum.TOON_ZAP)
        if not zapOrderedList:
            return retDict

        # consts
        LEFT = 1
        RIGHT = -1

        for toonIndex in zapOrderedList:
            # Make sure this toonIndex exists.
            if toonIndex >= len(self.battle.toons):
                continue
            # Make sure that we have actually targeted a cog.
            if targets[toonIndex] == -1:
                continue
            targetIndex = targets[toonIndex]
            retList = [targetIndex]

            # Ensure that zaps can actually jump from this cog.
            if 0 <= targetIndex < len(self.cogPanels):
                if (
                    self.cogPanels[targetIndex].cog
                    and self.cogPanels[targetIndex].cog.getStatusEffectOfType(FrozenStatusEffect)
                ):
                    # Set the targets hit on this toon index.
                    retDict[toonIndex] = retList
                    continue

            # The following code is lifted, and adjusted, from BattleCalculatorAI.

            # First, we need to determine the direction we need to go.
            # Firstly, assume that we're going LEFT.
            direction = LEFT

            # However, if there's no suit to the left of us,
            # then obviously we'll need to go right.
            if targetIndex >= len(self.battle.activeSuits) - 1:
                direction = RIGHT

            # Suppose there is a suit to the left of us.
            # Well, what if it's not soaked? Then we'll go right.
            elif not soakedSuits[targetIndex + LEFT]:
                direction = RIGHT

            # Now, we're going to go over a set amount of suits.
            for _ in range(ZapTargetsWanted):
                # If this cog is not soaked, then there's no more suits to check.
                if not soakedSuits[targetIndex]:
                    break

                # Now that we know that the cog is soaked,
                # we're safe to apply the damage to it.
                if targetIndex not in retList:
                    retList.append(targetIndex)

                # Now, we'll go ahead and move our targetIndex
                # by the expected direction. And if it's OOB,
                # then we're safe to break from the loop.
                targetIndex += direction
                if not (0 <= targetIndex < len(self.battle.suits)):
                    break

            # Set the targets hit on this toon index.
            retDict[toonIndex] = retList

        # Return the full dictionary of toon indices -> targets hit.
        return retDict

    def _getSplashTargetDict(self, battleIndices, tracks, levels, targets):
        retDict = {}
        squirtOrderedList = self._getGagOrderedList(battleIndices, tracks, levels, targets, AttackEnum.TOON_SQUIRT)
        if not squirtOrderedList:
            return retDict

        untouchableSuits = self._checkSuitsForStatusEffects(UntouchableStatusEffect)
        for toonIndex in squirtOrderedList:
            # Make sure this toonIndex exists.
            if toonIndex >= len(self.battle.toons):
                continue
            # Make sure that we have actually targeted a cog.
            if targets[toonIndex] == -1:
                continue
            targetIndex = targets[toonIndex]
            retList = [targetIndex]

            # The following code is lifted, and adjusted, from BattleCalculatorAI.

            # Soak the nearby suits.
            # First, attempt to soak the target to the right.
            if targetIndex > 0:
                if not untouchableSuits[targetIndex - 1]:
                    retList.append(targetIndex - 1)

            # Then attempt to soak the target to the left.
            if targetIndex < len(self.battle.activeSuits) - 1:
                if not untouchableSuits[targetIndex + 1]:
                    retList.append(targetIndex + 1)

            # Set the targets hit on this toon index.
            retDict[toonIndex] = retList

        # Return the full dictionary of toon indices -> targets hit.
        return retDict

    def updateLockIns(self, battleIndices, lockIns):
        for i in range(4):
            if battleIndices[i] != -1:
                self.toonPanels[battleIndices[i]].setLockIn(lockIns[i])
                if battleIndices[i] == self.localNum:
                    self.waitPanel.setLockIn(lockIns[i])

    def chooseDefaultTarget(self):
        if self.track > -1:
            response = {}
            response['mode'] = 'Attack'
            response['track'] = self.track
            response['level'] = self.level
            response['target'] = self.target
            messenger.send(self.battleEvent, [response])
            return 1
        return 0

    def updateLaffMeter(self, toonNum, hp):
        self.toonPanels[toonNum].updateLaffMeter(hp)

    # Each state will have an enter function, an exit function,
    # and a datagram handler, which will be set during each enter function.

    # Specific State functions

    ##### Off state #####

    def enterOff(self):
        if self.isLoaded:
            # Hide the toon panels
            for toonPanel in self.toonPanels:
                toonPanel.hide()
                toonPanel.set3dNametagVisiblity(True)

            for cogPanel in self.cogPanels:
                cogPanel.hide()

            self.informationPanel.clearPanel()

        self.toonAttacks = [(-1, 0, 0), (-1, 0, 0), (-1, 0, 0), (-1, 0, 0)]
        self.target = 0
        # Hide the timer
        if hasattr(self, 'timer'):
            self.timer.hide()
        if self.roundCount:
            self.roundCount.hide()

    def exitOff(self):
        if self.isLoaded:
            self.__enterPanels(self.numToons, self.localNum)
            self.__cogPanels(self.numCogs)
        # No timer in tutorial
        if not self.tutorialFlag:
            self.timer.show()
        # Clear the attack values
        self.track = -1
        self.level = -1
        self.target = 0

    ##### Attack state #####

    def enterAttack(self):
        messenger.send('reopen-dice-select')
        self.attackPanel.enter()
        self.accept(self.attackPanelDoneEvent, self.__handleAttackPanelDone)

    def exitAttack(self):
        messenger.send('close-dice-select')
        self.ignore(self.attackPanelDoneEvent)
        self.attackPanel.exit()

    def __handleAttackPanelDone(self, doneStatus):
        self.notify.debug('doneStatus: %s' % doneStatus)
        mode = doneStatus['mode']
        self.lockIn = doneStatus.get('lockIn', False)
        if mode == 'Inventory':
            self.track = doneStatus['track']
            self.level = doneStatus['level']

            # Update your own toon panel
            self.toonPanels[self.localNum].setValues(self.localNum, self.track, self.level, townBattle=self)
            # Update the targeting GUI
            self.chooseCogPanel.setValues(self.track, self.level)
            self.chooseToonPanel.setValues(self.track, self.level)
            self.waitPanel.setValues(self.track, self.level)

            response = {'track': self.track, 'level': self.level}
            if self.track == AttackEnum.TOON_HEAL:
                if self.__isGroupHeal(self.level):
                    # For group heals, no choice needs to be made, and no
                    # target is required.
                    response['mode'] = 'Attack'
                    response['target'] = self.target
                    response['lockIn'] = self.lockIn
                    messenger.send(self.battleEvent, [response])
                    self.fsm.request('AttackWait')
                # For single heals, we may ask the user for a choice.
                elif self.numToons == 3 or self.numToons == 4:
                    # If there are 3 or 4 toons, a choice must be made.
                    self.fsm.request('ChooseToon')
                elif self.numToons == 2:
                    # If there are only two toons, then the other toon
                    # is the default target
                    response['mode'] = 'Attack'
                    response['lockIn'] = self.lockIn
                    # Figure out the index of the other guy
                    if self.localNum == 0:
                        response['target'] = 1
                    elif self.localNum == 1:
                        response['target'] = 0
                    else:
                        self.notify.error('Bad localNum value: %s' % self.localNum)
                    messenger.send(self.battleEvent, [response])
                    self.fsm.request('AttackWait')
                else:
                    # You can't heal yourself, so only 2, 3, and 4 are valid
                    # values.
                    self.notify.error('Heal was chosen when number of toons is %s' % self.numToons)
            # If it isn't heal, then it is an attack.
            elif self.__isCogChoiceNecessary():
                self.notify.debug('choice needed')
                self.fsm.request('ChooseCog')

                # Now we send an Attack message anyway, so other
                # toons in the battle are notified of our choice
                # of track, even before we choose a target.  The
                # AI will know this doesn't count as a full choice
                # yet.
                response['mode'] = 'Attack'
                response['target'] = -1
                messenger.send(self.battleEvent, [response])
            else:
                self.notify.debug('no choice needed')
                self.fsm.request('AttackWait')
                response['mode'] = 'Attack'
                # If there is only one cog, then the target is cog 0
                response['target'] = 0
                response['lockIn'] = self.lockIn
                messenger.send(self.battleEvent, [response])
        elif mode == 'Run':
            self.fsm.request('Run')
        elif mode == 'Surrender':
            self.fsm.request('Surrender')
        elif mode == 'SOS':
            self.fsm.request('SOS')
        elif mode == 'Fire':
            # Update the targeting GUI
            self.waitPanel.setValues(AttackEnum.TOON_FIRE, None)
            self.fsm.request('Fire')
        elif mode == 'Sue':
            # Update the targeting GUI
            self.waitPanel.setValues(AttackEnum.TOON_SUE, None)
            self.fsm.request('Sue')
        elif mode == 'Counterfeit':
            self.fsm.request('Counterfeit')
        elif mode == 'Pass':
            # Update the targeting GUI
            self.waitPanel.setValues(AttackEnum.TOON_PASS, None)
            response = {}
            response['mode'] = 'Pass'
            response['id'] = -1
            response['lockIn'] = self.lockIn
            messenger.send(self.battleEvent, [response])
            self.fsm.request('AttackWait')
        else:
            self.notify.warning('unknown mode: %s' % mode)

    ##### ChooseCog state #####

    def checkHealTrapLureSue(self, groupTrapCheck=False):
        # Assume you can do all of these, then check each case
        self.notify.debug(f'''***numToons: {self.numToons}, numCogs: {self.numCogs}, lured: {self.luredIndices},
        trapped: {self.trappedIndices}, sued: {self.suedIndices}''')

        # If everybody is trapped or lured, you cannot trap
        canTrap = 0 if len(PythonUtil.union(self.trappedIndices, self.luredIndices)) == self.numCogs else 1

        # If all cogs are lured or untouchable, no lure
        canLure = 0 if len(PythonUtil.union(self.luredIndices, self.untouchableSuitIndices)) == self.numCogs else 1

        # check if any single Cog is trapped if we want to use a group trap (currently only all trap SOS NPCs)
        if groupTrapCheck:
            canTrap = 1 if canTrap and len(self.trappedIndices) == 0 else 0

        # If there is only one toon in battle or all other toons are untouchable, they cannot heal
        canHeal = 0 if len(self.untouchableToonIndices) >= self.numToons - 1 else 1

        # If all cogs in battle are sued or untouchable, then the toon cannot sue.
        canSue = 0 if len(PythonUtil.union(self.suedIndices, self.untouchableSuitIndices)) == self.numCogs else 1

        return canHeal, canTrap, canLure, canSue

    def adjustCogsAndToons(self, cogs, luredIndices, trappedIndices, suedIndices, toons,
                           afkToons, battle, untouchableToonIndices, untouchableSuitIndices,
                           untouchableByTrapSuitIndices, forceUpdate=False):
        self.notify.debug(f'adjustCogsAndToons() cogs: {cogs} self.cogs: {self.cogs}')
        self.notify.debug(f'adjustCogsAndToons() luredIndices: {luredIndices} self.luredIndices: {self.luredIndices}')
        self.notify.debug(f'adjustCogsAndToons() trappedIndices: {trappedIndices} self.trappedIndices: {self.trappedIndices}')
        self.notify.debug(f'adjustCogsAndToons() suedIndices: {suedIndices} self.suedIndices: {self.suedIndices}')
        self.notify.debug(f'adjustCogsAndToons() toons: {toons} self.toons: {self.toons}')
        self.notify.debug(f'adjustCogsAndToons() afkToons: {afkToons} self.afkToons: {self.afkToons}')
        # Determine the maximum level attack item we'll get credit
        # for, based on the suits in the battle.  This is the same as
        # the highest level suit we're currently facing.
        maxSuitLevel = 0
        zoneId = base.cr.playGame.getPlace().getZoneId()
        for cog in cogs:
            if cog.isVirtual and 12500 <= zoneId <= 12899:  # Is a laser cog in the lawfice?
                maxSuitLevel = 0
                break
            maxSuitLevel = max(maxSuitLevel, cog.getActualLevel())
        creditLevel = maxSuitLevel
        # If nothing changed, we do not need to reactivate the gui
        if cogs == self.cogs and creditLevel == self.creditLevel and luredIndices == self.luredIndices and \
                trappedIndices == self.trappedIndices and suedIndices == self.suedIndices and toons == self.toons \
                and afkToons == self.afkToons:
            resetActivateMode = 0
        else:
            resetActivateMode = 1
        self.notify.debug('adjustCogsAndToons() resetActivateMode: %s' % resetActivateMode)
        self.cogs = cogs

        self.numCogs = len(cogs)
        self.creditLevel = creditLevel
        self.luredIndices = luredIndices
        self.trappedIndices = trappedIndices
        self.suedIndices = suedIndices

        self.untouchableToonIndices = untouchableToonIndices
        self.untouchableSuitIndices = untouchableSuitIndices
        self.untouchableByTrapSuitIndices = untouchableByTrapSuitIndices

        self.toons = toons
        self.afkToons = afkToons
        self.numToons = len(toons)
        self.localNum = toons.index(base.localAvatar)
        self.battle = battle
        currStateName = self.fsm.getCurrentState().getName()

        for cog in self.cogs:
            messenger.send(f"suitHpChanged-{cog.doId}")

        if resetActivateMode or forceUpdate:
            self.__enterPanels(self.numToons, self.localNum)
            self.__cogPanels(self.numCogs)
            # New toons means an adjustment to the laff meters.
            for i, toon in enumerate(self.toons):
                self.toonPanels[i].setLaffMeter(toon)
                self.toonPanels[i].setCogs(cogs)
                if toon.doId in self.afkToons:
                    self.toonPanels[i].showAfkLabel()

            for i, cog in enumerate(self.cogs):
                self.cogPanels[i].setCogInformation(cog)

            if currStateName == 'ChooseCog':
                self.chooseCogPanel.adjustCogs(self.numCogs, self.luredIndices, self.trappedIndices, self.track, self.untouchableSuitIndices)
            elif currStateName == 'ChooseToon':
                self.chooseToonPanel.adjustToons(self.numToons, self.toons, self.localNum, self.untouchableToonIndices)
            canHeal, canTrap, canLure, canSue = self.checkHealTrapLureSue()
            allSuitsUntouchable = len(untouchableSuitIndices) == self.numCogs
            battleState = 'counterfeit' if currStateName == 'Counterfeit' else 'battle'
            base.localAvatar.inventory.setActivateMode(battleState, heal=canHeal, trap=canTrap, lure=canLure, sue=canSue,
                                                       isStreet=self.isStreet,
                                                       creditLevel=self.creditLevel, tutorialFlag=self.tutorialFlag,
                                                       allSuitsUntouchable=allSuitsUntouchable)
            self.updatePanelsForAspectRatio()

        if currStateName != 'Afk' and base.localAvatar.doId in self.afkToons:
            self.fsm.request('Afk')

    @property
    def localToonPanel(self):
        return self.toonPanels[self.localNum]

    def getToonBannedGags(self, toon):
        toonNum = self.toons.index(toon)
        self.toonPanels[toonNum].checkAvatarBannedGags()
        return self.toonPanels[toonNum].bannedGags

    def adjustCogsAndToons(self, cogs, luredIndices, trappedIndices, toons, battle):
        self.battle = battle
        cogIds = map(lambda cog: cog.doId, cogs)
        # self.notify.debug('adjustCogsAndToons() cogIds: %s self.cogs: %s' % (cogIds, self.cogs))
        # self.notify.debug('adjustCogsAndToons() luredIndices: %s self.luredIndices: %s' % (luredIndices, self.luredIndices))
        # self.notify.debug('adjustCogsAndToons() trappedIndices: %s self.trappedIndices: %s' % (trappedIndices, self.trappedIndices))
        toonIds = map(lambda toon: toon.doId, toons)
        # self.notify.debug('adjustCogsAndToons() toonIds: %s self.toons: %s' % (toonIds, self.toons))
        maxSuitLevel = 0
        cogFireCostIndex = 0
        for cog in cogs:
            maxSuitLevel = max(maxSuitLevel, cog.getActualLevel())
            self.cogFireCosts[cogFireCostIndex] = 1
            cogFireCostIndex += 1

        creditLevel = maxSuitLevel
        resetActivateMode = not (
                    cogIds == self.cogs and creditLevel == self.creditLevel and luredIndices == self.luredIndices and trappedIndices == self.trappedIndices and toonIds == self.toons)
        # self.notify.debug('adjustCogsAndToons() resetActivateMode: %s' % resetActivateMode)
        self.cogs = cogIds
        self.numCogs = len(cogs)
        self.creditLevel = creditLevel
        self.luredIndices = luredIndices
        self.trappedIndices = trappedIndices
        self.toons = toonIds
        self.toonAvatars = list(toons)
        self.numToons = len(toons)
        self.localNum = toons.index(base.localAvatar)
        currStateName = self.fsm.getCurrentState().getName()
        # for i in range(len(toons)):
        #     self.toonPanels[i].setLaffMeter(toons[i])
        if resetActivateMode:
            self.__enterPanels(self.numToons, self.localNum)
            self.__cogPanels(self.numCogs)
            for i in range(len(toons)):
                self.toonPanels[i].setLaffMeter(toons[i])

            self.setSurrenderedToons(self.surrenderedToons)

            for i in range(len(cogs)):
                self.cogPanels[i].setCogInformation(cogs[i])

            if currStateName == 'ChooseCog':
                self.chooseCogPanel.adjustCogs(self.numCogs, self.luredIndices, self.trappedIndices, self.track,
                                               self.level)
            elif currStateName == 'ChooseToon':
                self.chooseToonPanel.adjustToons(self.numToons, self.localNum, self.track, self.level, self.toonAvatars)
            canHeal, canTrap, canLure = self.checkHealTrapLure()
            base.localAvatar.inventory.setBattleCreditMultiplier(self.creditMultiplier)
            base.localAvatar.inventory.setActivateMode('battle', heal=canHeal, trap=canTrap, lure=canLure,
                                                       bldg=self.bldg, creditLevel=self.creditLevel,
                                                       tutorialFlag=self.tutorialFlag)

    def enterChooseCog(self):
        self.cog = 0
        self.chooseCogPanel.enter(
            self.numCogs, self.toons, luredIndices=self.luredIndices, trappedIndices=self.trappedIndices,
            track=self.track, untouchableIndices=self.untouchableSuitIndices,
            untouchableByTrapIndices=self.untouchableByTrapSuitIndices)
        self.accept(self.chooseCogPanelDoneEvent, self.__handleChooseCogPanelDone)
        self.accept(self.gagChangeEvent, self.__handleGagChange)

    def exitChooseCog(self):
        self.ignore(self.chooseCogPanelDoneEvent)
        self.ignore(self.gagChangeEvent)
        self.chooseCogPanel.exit()

    def __handleChooseCogPanelDone(self, doneStatus):
        mode = doneStatus['mode']
        if mode == 'Back':
            self.fsm.request('Attack')
            response = {}
            response['mode'] = 'UnAttack'
            messenger.send(self.battleEvent, [response])
        elif mode == 'Avatar':
            self.cog = doneStatus['avatar']
            self.target = self.cog
            self.fsm.request('AttackWait')
            self.waitPanel.setValues(self.track, self.level)
            response = {}
            response['mode'] = 'Attack'
            response['track'] = self.track
            response['level'] = self.level
            response['target'] = self.cog
            response['lockIn'] = self.lockIn
            messenger.send(self.battleEvent, [response])
        else:
            self.notify.warning('unknown mode: %s' % mode)

    ##### AttackWait state #####

    def enterAttackWait(self):
        self.accept(self.waitPanelDoneEvent, self.__handleAttackWaitBack)
        self.accept(self.lockInEvent, self.__handleLockIn)
        self.accept(self.gagChangeEvent, self.__handleGagChange)
        self.waitPanel.enter()

    def exitAttackWait(self):
        self.ignore(self.waitPanelDoneEvent)
        self.ignore(self.lockInEvent)
        self.ignore(self.gagChangeEvent)
        self.waitPanel.exit()

    def __handleAttackWaitBack(self, doneStatus):
        mode = doneStatus['mode']
        if mode == 'Back':
            if self.track == AttackEnum.TOON_HEAL:
                # If a heal was chosen, go back to choose toon if there are
                # more than 2 toons, otherwise go to the attack panel.
                # Nope! That doesn't happen anymore. Now, if you have chosen
                # a heal, it always makes you go back to the attack panel. This
                # is the cowardly way of handling the situation where the selected
                # healee flees the battle.
                self.fsm.request('Attack')
            elif self.track == AttackEnum.TOON_NO_ATTACK:
                # Must have come back from passing, show them the attack panel again
                self.fsm.request('Attack')
            # An attack was chosen. Go back to choose a cog or to choose
            # an attack, appropriately.
            elif self.__isCogChoiceNecessary():
                self.fsm.request('ChooseCog')
            else:
                self.fsm.request('Attack')
            # Clear out whatever attack choice was sent to the server
            response = {}
            response['mode'] = 'UnAttack'
            messenger.send(self.battleEvent, [response])
        else:
            self.notify.error('unknown mode: %s' % mode)

    def __handleLockIn(self, lockInInfo):
        mode = lockInInfo['mode']
        if mode == 'LockIn':
            response = {}
            response['mode'] = 'LockIn'
            response['lockIn'] = lockInInfo['lockIn']
            messenger.send(self.battleEvent, [response])
        else:
            self.notify.error('unknown mode: %s' % mode)

    def __handleGagChange(self, gagChangeInfo):
        # This is a special case where we're changing a single target toon-up gag during toon select.
        if 'softChange' in gagChangeInfo and gagChangeInfo['softChange']:
            self.toonPanels[self.localNum].setValues(self.localNum, self.track, self.level, townBattle=self)
            self.waitPanel.setValues(self.track, self.level)
        else:
            messenger.send(self.battleEvent, [gagChangeInfo])

    ##### ChooseToon state #####

    def enterChooseToon(self, level: int = 0, allowPickLocal: bool = False):
        self.toon = 0
        self.chooseToonPanel.enter(
            self.numToons, self.toons, localNum=self.localNum,
            untouchableIndices=self.untouchableToonIndices, npcId=level,
            allowPickLocal=allowPickLocal
        )
        self.accept(self.chooseToonPanelDoneEvent, self.__handleChooseToonPanelDone)
        self.accept(self.gagChangeEvent, self.__handleGagChange)

    def exitChooseToon(self):
        self.ignore(self.chooseToonPanelDoneEvent)
        self.ignore(self.gagChangeEvent)
        self.chooseToonPanel.exit()

    def __handleChooseToonPanelDone(self, doneStatus):
        mode = doneStatus['mode']
        if mode == 'Back':
            self.fsm.request('Attack')
            response = {'mode': 'UnAttack'}
            messenger.send(self.battleEvent, [response])
        elif mode == 'Avatar':
            self.toon = doneStatus['avatar']
            self.target = self.toon
            self.fsm.request('AttackWait')
            response = {'mode': doneStatus['attackType'], 'track': self.track, 'level': self.level, 'target': self.toon,
                        'lockIn': self.lockIn}
            messenger.send(self.battleEvent, [response])
        else:
            self.notify.warning('unknown mode: %s' % mode)

    ##### Run state #####

    def enterRun(self):
        if self.isStreet:
            self.runPanel.show()

    def exitRun(self):
        self.runPanel.hide()

    def __handleRunPanelDone(self, doneStatus):
        if doneStatus == DGG.DIALOG_OK:
            response = {}
            response['mode'] = 'Run'
            messenger.send(self.battleEvent, [response])
        else:
            self.fsm.request('Attack')

    ##### AFK State #####

    def enterAfk(self):
        base.transitions.fadeScreen(0.5)
        self.afkPanel.show()

    def exitAfk(self):
        base.transitions.noFade()
        self.afkPanel.hide()

    def __handleAfkPanelDone(self, doneStatus):
        # Can't run if not on a street...
        if doneStatus == DGG.DIALOG_CANCEL and self.isStreet:
            response = {}
            response['mode'] = 'Run'
            messenger.send(self.battleEvent, [response])
        else:
            response = {}
            response['mode'] = 'Attack'
            response['track'] = AttackEnum.TOON_UN_ATTACK
            response['level'] = 0
            response['target'] = 0
            messenger.send(self.battleEvent, [response])
            self.fsm.request('Attack')

    ##### Surrender State #####

    def enterSurrender(self):
        if self.isStreet:
            return

        if self.surrendered:
            text = TTLocalizer.TownBattleSurrenderUnvote
        else:
            if self.numToons <= 4:
                voteMessage = TTLocalizer.TownBattleSurrenderVoteUnanimously
            else:
                voteMessage = TTLocalizer.TownBattleSurrenderVoteNumber.format(number=TTLocalizer.numberToWord(self.numToons - 1))
            text = TTLocalizer.TownBattleSurrenderVote.format(votecase=voteMessage)

        self.surrenderPanel.setMessage(text)
        self.surrenderPanel.show()

    def exitSurrender(self):
        self.surrenderPanel.hide()

    def __handleSurrenderPanelDone(self, doneStatus):
        if doneStatus == DGG.DIALOG_OK:
            response = {}
            response['mode'] = 'Surrender'
            messenger.send(self.battleEvent, [response])
            self.surrendered = not self.surrendered
            self.fsm.request('Attack')
        else:
            self.fsm.request('Attack')

    ##### Fire state #####

    def enterFire(self):
        # canHeal, canTrap, canLure = self.checkHealTrapLure()
        for i, suit in enumerate(self.cogs):
            self.cogFireCosts[i] = math.ceil(suit.getActualLevel() * FireCostPercent)
        self.FireCogPanel.enter(self.numCogs, luredIndices=self.luredIndices, trappedIndices=self.trappedIndices, track=self.track, fireCosts=self.cogFireCosts)
        self.accept(self.fireCogPanelDoneEvent, self.__handleCogFireDone)

    def exitFire(self):
        self.ignore(self.fireCogPanelDoneEvent)
        self.FireCogPanel.exit()

    def __handleCogFireDone(self, doneStatus):
        mode = doneStatus['mode']
        if mode == 'Back':
            self.fsm.request('Attack')
        elif mode == 'Avatar':
            self.cog = doneStatus['avatar']
            self.target = self.cog
            self.fsm.request('AttackWait')
            response = {}
            response['mode'] = 'Fire'
            response['target'] = self.cog
            response['lockIn'] = self.lockIn
            messenger.send(self.battleEvent, [response])
        else:
            self.notify.warning('unknown mode: %s' % mode)

    ##### Sue state #####

    def enterSue(self):
        # canSue = self.checkHealTrapLureSue()
        i = 0
        for suit in self.cogs:
            self.cogSueCosts[i] = math.ceil(suit.getActualLevel() * SueCostPercent)
            i += 1

        self.SueCogPanel.enter(self.numCogs, sueCosts=self.cogSueCosts, suedIndices = self.suedIndices)
        self.accept(self.sueCogPanelDoneEvent, self.__handleCogSueDone)

    def exitSue(self):
        self.ignore(self.sueCogPanelDoneEvent)
        self.SueCogPanel.exit()

    def __handleCogSueDone(self, doneStatus):
        mode = doneStatus['mode']
        if mode == 'Back':
            self.fsm.request('Attack')
        elif mode == 'Avatar':
            self.cog = doneStatus['avatar']
            self.target = self.cog
            self.fsm.request('AttackWait')
            response = {}
            response['mode'] = 'Sue'
            response['target'] = self.cog
            response['lockIn'] = self.lockIn
            messenger.send(self.battleEvent, [response])
        else:
            self.notify.warning('unknown mode: %s' % mode)

    ##### Counterfeit state #####

    def enterCounterfeit(self):
        self.attackPanel.enter()
        self.accept(self.attackPanelDoneEvent, self.__handleAttackPanelDone)
        self.accept(self.counterfeitDoneEvent, self.__handleCounterfeitDone)
        base.localAvatar.inventory.setActivateMode('counterfeit',
                                                   isStreet=self.isStreet,
                                                   tutorialFlag=self.tutorialFlag)

    def __handleCounterfeitDone(self, doneStatus):
        mode = doneStatus['mode']
        if mode == 'Back':
            self.fsm.request('Attack')
        elif mode == 'CopyGag':
            gagTrack, gagLevel = doneStatus['gagTrack'], doneStatus['gagLevel']
            self.fsm.request('Attack')
            response = dict(mode='Counterfeit', gagTrack=gagTrack, gagLevel=gagLevel)
            messenger.send(self.battleEvent, [response])
        else:
            self.notify.warning('unknown mode: %s' % mode)

    def exitCounterfeit(self):
        self.ignore(self.attackPanelDoneEvent)
        self.attackPanel.exit()
        self.ignore(self.counterfeitDoneEvent)
        # Go back to the old battle state now that we're done
        canHeal, canTrap, canLure, canSue = self.checkHealTrapLureSue()
        allSuitsUntouchable = len(self.untouchableSuitIndices) == self.numCogs
        base.localAvatar.inventory.setActivateMode('battle', heal=canHeal, trap=canTrap, lure=canLure, sue=canSue,
                                                   isStreet=self.isStreet,
                                                   creditLevel=self.creditLevel, tutorialFlag=self.tutorialFlag,
                                                   allSuitsUntouchable=allSuitsUntouchable)

    ##### SOS state #####

    def enterSOS(self):
        check = self.checkHealTrapLureSue(groupTrapCheck=True)
        canLure = check[2]
        canTrap = check[1]
        self.SOSPanel.enter(canLure, canTrap, self.isStreet)
        self.accept(self.SOSPanelDoneEvent, self.__handleSOSPanelDone)

    def exitSOS(self):
        self.ignore(self.SOSPanelDoneEvent)
        self.SOSPanel.exit()

    def __handleSOSPanelDone(self, doneStatus):
        mode = doneStatus['mode']
        if mode == 'NPCSOS':
            iou = doneStatus['friend']
            self.level = iou.getItemSubtype()

            # Update the targeting GUI
            self.chooseToonPanel.setValues(AttackEnum.TOON_NPC, self.level)
            self.waitPanel.setValues(AttackEnum.TOON_NPC, self.level)

            messenger.send(self.battleEvent, [{
                'mode': 'NPCSOS',
                'level': self.level,
                'lockIn': doneStatus['lockIn'],
                'target': 0 if self.numToons == 1 else -1,
            }])

            if self.numToons > 1:
                self.fsm.request('ChooseToon', enterArgList=[self.level, True])
            else:
                self.fsm.request('AttackWait')
        elif mode == 'Back':
            self.fsm.request('Attack')

    def __isCogChoiceNecessary(self):
        # If there is more than one cog, and a non-group attack
        # has been selected, a cog choice needs to be made.
        if self.numCogs > 1 and not self.__isGroupAttack(self.track, self.level):
            return 1
        else:
            return 0

    def __isGroupAttack(self, trackNum, levelNum):
        retval = BattleBase.attackAffectsGroup(trackNum, levelNum)
        return retval

    def __isGroupHeal(self, levelNum):
        retval = BattleBase.attackAffectsGroup(AttackEnum.TOON_HEAL, levelNum)
        return retval

    def playCounterfeitAnimation(self, toon, track, level):
        toonPanelList = [toonPanel for toonPanel in self.toonPanels if toonPanel.avatar is toon]
        if not len(toonPanelList):
            return

        toonPanelList[0].doCounterfeitAnimation(track, level)

    def setSurrenderedToons(self, surrenderedToons):
        self.surrenderedToons = surrenderedToons
        needChangeList = [toonPanel for toonPanel in self.toonPanels if toonPanel.avatar and (
                bool(toonPanel.avatar.doId in surrenderedToons) != toonPanel.surrenderState)]
        for panel in needChangeList:
            panel.updateSurrenderState(bool(panel.avatar.doId in surrenderedToons))

    def __handleWithinTimer(self, *args, **kwargs):
        if not self.roundCount:
            return
        if not self.battle:
            return

        currRound = self.battle.currRound + 1
        self.roundCount.setText(f'Round {currRound}')
        self.roundCount['text_scale'] = 0.12 if currRound >= 100 else 0.14

        if self.roundCountSeq:
            self.roundCountSeq.pause()
        self.roundCountSeq = Sequence(
            Func(self.roundCount.show),
            LerpColorScaleInterval(self.roundCount, 0.08, (1, 1, 1, 1))
        )
        self.roundCountSeq.start()

    def __handleWithoutTimer(self, *args, **kwargs):
        if not self.roundCount:
            return
        if not self.battle:
            return

        if self.roundCountSeq:
            self.roundCountSeq.pause()
        self.roundCountSeq = Sequence(
            LerpColorScaleInterval(self.roundCount, 0.08, (1, 1, 1, 0)),
            Func(self.roundCount.hide),
        )
        self.roundCountSeq.start()
