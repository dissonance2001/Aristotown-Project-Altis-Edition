from toontown.toonbase.ToontownBattleGlobals import *
import types
from direct.fsm import StateData
from direct.fsm import ClassicFSM, State
from direct.fsm import State
from direct.interval.IntervalGlobal import *
from toontown.battle.BattleSounds import *
from toontown.town import TownBattleAttackPanel
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownLoader
from toontown.town import TownBattleWaitPanel
from toontown.town import TownBattleChooseAvatarPanel
from toontown.town import TownBattleSOSPanel
from toontown.town import TownBattleSOSPetSearchPanel
from toontown.town import TownBattleSOSPetInfoPanel
from toontown.town import TownBattleToonPanel
from toontown.town import TownBattleCogPanel
from toontown.toontowngui import TTDialog
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import BattleBase
from toontown.toon import IOURegistry
from toontown.toonbase import ToontownTimer
from toontown.toonbase import ToonPythonUtil as PythonUtil
from toontown.toonbase import TTLocalizer
from toontown.pets import PetConstants
from direct.gui.DirectGui import DGG
from direct.gui.DirectGui import DirectFrame
from toontown.battle import FireCogPanel
from direct.interval.SoundInterval import SoundInterval
from toontown.battle import SueCogPanel

class TownBattle(StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('TownBattle')
    evenPos = (1.1, 0.85, 0.30, -0.30, -0.85, -1.1)
    oddPos = (0.55, 0, -0.55, -7, 7)

    def __init__(self, doneEvent):
        StateData.StateData.__init__(self, doneEvent)
        self.numCogs = 1
        self.cogs = []
        self.creditLevel = None
        self.clockTick = None
        self.battle = None
        self.luredIndices = []
        self.trappedIndices = []
        self.numToons = 1
        self.toons = []
        self.toonAvatars = []
        self.localNum = 0
        self.time = 0
        self.bldg = 0
        self.track = -1
        self.level = -1
        self.lastActionMode = 'Inventory'
        self.target = 0
        self.timeRunningOutTrack = None
        self.timeRunnoutOutPulseTrack = None
        self.toonAttacks = [(-1, 0, 0),
         (-1, 0, 0),
         (-1, 0, 0),
         (-1, 0, 0)]
        self.fsm = ClassicFSM.ClassicFSM('TownBattle', [State.State('Off', self.enterOff, self.exitOff, ['Attack']),
         State.State('Attack', self.enterAttack, self.exitAttack, ['ChooseCog',
          'ChooseToon',
          'AttackWait',
          'Run',
          'Surrender',
          'Fire',
          'Sue',
          'SOS']),
         State.State('ChooseCog', self.enterChooseCog, self.exitChooseCog, ['AttackWait', 'Attack']),
         State.State('AttackWait', self.enterAttackWait, self.exitAttackWait, ['ChooseCog', 'ChooseToon', 'Attack', 'SOS']),
         State.State('ChooseToon', self.enterChooseToon, self.exitChooseToon, ['AttackWait', 'Attack', 'SOS']),
         State.State('Run', self.enterRun, self.exitRun, ['Attack']),
         State.State('Surrender', self.enterSurrender, self.exitSurrender, ['Attack']),
         State.State('SOS', self.enterSOS, self.exitSOS, ['Attack',
          'AttackWait',
          'SOSPetSearch',
          'SOSPetInfo',
          'ChooseToon']),
         State.State('SOSPetSearch', self.enterSOSPetSearch, self.exitSOSPetSearch, ['SOS', 'SOSPetInfo']),
         State.State('SOSPetInfo', self.enterSOSPetInfo, self.exitSOSPetInfo, ['SOS', 'AttackWait']),
         State.State('Fire', self.enterFire, self.exitFire, ['Attack', 'AttackWait']),
         State.State('Sue', self.enterSue, self.exitSue, ['Attack', 'AttackWait'])], 'Off', 'Off')
        self.runPanel = TTDialog.TTDialog(dialogName='TownBattleRunPanel', text=TTLocalizer.TownBattleRun, style=TTDialog.TwoChoice, command=self.__handleRunPanelDone)
        self.runPanel.hide()
        self.surrenderedToons = []
        self.surrenderPanel = TTDialog.TTDialog(dialogName='TownBattleSurrenderPanel', text=TTLocalizer.TownBattleSurrenderVote, style=TTDialog.TwoChoice, command=self.__handleSurrenderPanelDone)
        self.surrenderPanel.hide()
        self.attackPanelDoneEvent = 'attack-panel-done'
        self.attackPanel = TownBattleAttackPanel.TownBattleAttackPanel(self.attackPanelDoneEvent)
        self.waitPanelDoneEvent = 'wait-panel-done'
        self.waitPanel = TownBattleWaitPanel.TownBattleWaitPanel(self.waitPanelDoneEvent)
        self.chooseCogPanelDoneEvent = 'choose-cog-panel-done'
        self.chooseCogPanel = TownBattleChooseAvatarPanel.TownBattleChooseAvatarPanel(self.chooseCogPanelDoneEvent, 0)
        self.chooseToonPanelDoneEvent = 'choose-toon-panel-done'
        self.chooseToonPanel = TownBattleChooseAvatarPanel.TownBattleChooseAvatarPanel(self.chooseToonPanelDoneEvent, 1)
        self.SOSPanelDoneEvent = 'SOS-panel-done'
        self.SOSPanel = TownBattleSOSPanel.TownBattleSOSPanel(self.SOSPanelDoneEvent)
        self.SOSPetSearchPanelDoneEvent = 'SOSPetSearch-panel-done'
        self.SOSPetSearchPanel = TownBattleSOSPetSearchPanel.TownBattleSOSPetSearchPanel(self.SOSPetSearchPanelDoneEvent)
        self.SOSPetInfoPanelDoneEvent = 'SOSPetInfo-panel-done'
        self.SOSPetInfoPanel = TownBattleSOSPetInfoPanel.TownBattleSOSPetInfoPanel(self.SOSPetInfoPanelDoneEvent)
        self.fireCogPanelDoneEvent = 'fire-cog-panel-done'
        self.FireCogPanel = FireCogPanel.FireCogPanel(self.fireCogPanelDoneEvent)
        self.sueCogPanelDoneEvent = 'sue-cog-panel-done'
        self.SueCogPanel = SueCogPanel.SueCogPanel(self.sueCogPanelDoneEvent)
        self.cogFireCosts = [None,
         None,
         None,
         None,
         None,
        None,
        None]
        self.cogSueCosts = [None,
         None,
         None,
         None,
         None,
         None,
         None]
        self.toonPanels = [TownBattleToonPanel.TownBattleToonPanel(0),
                           TownBattleToonPanel.TownBattleToonPanel(1),
                           TownBattleToonPanel.TownBattleToonPanel(2),
                           TownBattleToonPanel.TownBattleToonPanel(3),
                           TownBattleToonPanel.TownBattleToonPanel(4),
                           TownBattleToonPanel.TownBattleToonPanel(5)]
        self.cogPanels = [TownBattleCogPanel.TownBattleCogPanel(self) for i in xrange(7)]
        self.timer = ToontownTimer.ToontownTimer()
        self.timer.reparentTo(base.a2dTopRight)
        self.timer.setPos(-0.151, 0, -1.808)
        self.timer.setScale(0.4)
        self.timer.hide()
        self.timerHoverRegion = DirectFrame(
            parent=self.timer,
            relief=DGG.FLAT,
            state=DGG.NORMAL,
            frameColor=(1, 1, 1, 0),
            frameSize=(-0.9, 0.9, -0.9, 0.9),
            pos=(0, 0, 0))
        self.timerHoverRegion.setTransparency(True)
        self.timerHoverRegion.bind(DGG.WITHIN, self.__handleWithinTimer)
        self.timerHoverRegion.bind(DGG.WITHOUT, self.__handleWithoutTimer)
        self.roundCount = DirectFrame(
            parent=base.a2dTopRight,
            relief=None,
            image='phase_3/maps/gui/ttcc_gui_scaledFrame_shadow.png',
            image_scale=(0.19, 1, 0.06),
            pos=(-0.17, 0, -1.61),
            scale=1,
            text='Round 1',
            text_scale=0.046,
            text_pos=(0, -0.014),
            text_fg=(1, 1, 1, 1),
            text_font=ToontownGlobals.getMinnieFont())
        self.roundCount.setTransparency(True)
        self.roundCount.hide()
        self.roundCountSeq = None

    def cleanup(self):
        self.ignore(self.attackPanelDoneEvent)
        self.unload()
        del self.fsm
        self.runPanel.cleanup()
        del self.runPanel
        self.surrenderPanel.cleanup()
        del self.surrenderPanel
        del self.attackPanel
        del self.waitPanel
        del self.chooseCogPanel
        del self.chooseToonPanel
        del self.SOSPanel
        del self.FireCogPanel
        del self.SueCogPanel
        del self.SOSPetSearchPanel
        del self.SOSPetInfoPanel
        for toonPanel in self.toonPanels:
            toonPanel.cleanup()
        if self.roundCountSeq:
            self.roundCountSeq.finish()
        self.roundCountSeq = None
        self.timerHoverRegion.destroy()
        self.roundCount.destroy()
        del self.timerHoverRegion
        del self.roundCount
        del self.toonPanels
        for cogPanel in self.cogPanels:
            cogPanel.cleanup()

        del self.cogPanels
        self.timer.destroy()
        del self.timer
        del self.cogs
        del self.toons

    def enter(self, event, parentFSMState, bldg = 0, creditMultiplier = 1, tutorialFlag = 0):
        self.parentFSMState = parentFSMState
        self.parentFSMState.addChild(self.fsm)
        if not self.isLoaded:
            self.load()
        print 'Battle Event %s' % event
        self.battleEvent = event
        self.fsm.enterInitialState()
        base.localAvatar.laffMeter.start()
        self.numToons = 1
        self.numCogs = 1
        self.toons = [base.localAvatar.doId]
        self.surrenderedToons = []
        for toonPanel in self.toonPanels:
            toonPanel.updateSurrenderState(False, instant=True)
       # self.toonPanels[0].setLaffMeter(base.localAvatar)
        self.bldg = bldg
        self.creditLevel = None
        self.creditMultiplier = creditMultiplier
        self.tutorialFlag = tutorialFlag
        base.localAvatar.inventory.setBattleCreditMultiplier(self.creditMultiplier)
        base.localAvatar.inventory.setActivateMode('battle', heal=0, bldg=bldg, tutorialFlag=tutorialFlag)
        self.SOSPanel.bldg = bldg

    def exit(self):
        base.localAvatar.laffMeter.stop()
        self.parentFSMState.removeChild(self.fsm)
        del self.parentFSMState
        base.localAvatar.inventory.setBattleCreditMultiplier(1)
        base.localAvatar.battleConditions = {}

    def load(self):
        if self.isLoaded:
            return
        self.attackPanel.load()
        self.waitPanel.load()
        self.chooseCogPanel.load()
        self.chooseToonPanel.load()
        self.SOSPanel.load()
        if hasattr(base, 'wantPets') and base.wantPets:
            self.SOSPetSearchPanel.load()
            self.SOSPetInfoPanel.load()
        self.isLoaded = 1

    def unload(self):
        if not self.isLoaded:
            return
        self.attackPanel.unload()
        self.waitPanel.unload()
        self.chooseCogPanel.unload()
        self.chooseToonPanel.unload()
        self.FireCogPanel.unload()
        self.SueCogPanel.unload()
        self.SOSPanel.unload()
        if hasattr(base, 'wantPets') and base.wantPets:
            self.SOSPetSearchPanel.unload()
            self.SOSPetInfoPanel.unload()
        self.isLoaded = 0

    def setState(self, state):
        if hasattr(self, 'fsm'):
            self.fsm.request(state)

    def checkTimer(self):
        if self.clockTick is not None:
            return

        self.clockTick = SoundInterval(
            globalBattleSoundCache.getSound('round_running_out.ogg'),
            node=base.localAvatar,
            listenerNode=base.localAvatar
        )
        self.clockTick.start()
        self.startTimeRunningOutTrack()
        self.startTimeRunningOutPulseTrack()

    def stopTimerSound(self):
        if hasattr(self, 'timeRunningOutPulseTrack') and self.timeRunningOutPulseTrack:
            self.timeRunningOutPulseTrack.finish()
        if self.timeRunningOutTrack:
            self.timeRunningOutTrack.finish()
        if self.clockTick is not None:
            self.clockTick.pause()
            self.clockTick = None

    def startTimeRunningOutPulseTrack(self):
        if hasattr(self, 'timeRunningOutPulseTrack') and self.timeRunningOutPulseTrack:
            self.timeRunningOutPulseTrack.finish()

        pulse = Sequence()

        duration = 1.0    # Starts slow
        minDuration = 0.1  # Ends very fast
        decrease = .1

        scale = self.timer.getScale()

        for i in xrange(20):
            pulse.append(
                LerpScaleInterval(
                    self.timer,
                    duration,
                    scale * 1.15,
                    blendType='easeInOut'
                )
            )

            pulse.append(
                LerpScaleInterval(
                    self.timer,
                    duration,
                    scale,
                    blendType='easeInOut'
                )
            )

            duration = max(minDuration, duration - decrease)

        self.timeRunningOutPulseTrack = pulse
        self.timeRunningOutPulseTrack.start()

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
            shakeInterval)
        self.timeRunningOutTrack.start()

    def updateTimer(self, time):
        self.time = time
        self.timer.setTime(time)

        # if time == 10:
        #     self.checkTimer()

    def __cogPanels(self, num):
        for panel in self.cogPanels:
            panel.hide()
            panel.setPos(0, 0, 0.7)

        for i in range(num):
            self.cogPanels[i].setX(((num - 1) * 0.25) - (i * 0.5))
            self.cogPanels[i].show()

    def __enterPanels(self, num, localNum):
        self.notify.debug('enterPanels() num: %d localNum: %d' % (num, localNum))
        for toonPanel in self.toonPanels:
            toonPanel.hide()
            z = -0.7875
            toonPanel.setPos(0, 0, z)

        if num == 1:
            self.toonPanels[0].setX(self.oddPos[1])
            self.toonPanels[0].show()
        elif num == 2:
            self.toonPanels[0].setX(self.evenPos[2])
            self.toonPanels[0].show()
            self.toonPanels[1].setX(self.evenPos[3])
            self.toonPanels[1].show()
        elif num == 3:
            self.toonPanels[0].setX(self.oddPos[0])
            self.toonPanels[0].show()
            self.toonPanels[1].setX(self.oddPos[1])
            self.toonPanels[1].show()
            self.toonPanels[2].setX(self.oddPos[2])
            self.toonPanels[2].show()
        elif num == 4:
            self.toonPanels[0].setX(self.evenPos[1])
            self.toonPanels[0].show()
            self.toonPanels[1].setX(self.evenPos[2])
            self.toonPanels[1].show()
            self.toonPanels[2].setX(self.evenPos[3])
            self.toonPanels[2].show()
            self.toonPanels[3].setX(self.evenPos[4])
            self.toonPanels[3].show()
        else:
            self.notify.error('Bad number of toons: %s' % num)
            

    def updateChosenAttacks(self, battleIndices, tracks, levels, targets):
        self.notify.debug('updateChosenAttacks bi=%s tracks=%s levels=%s targets=%s' % (battleIndices, tracks, levels, targets))

        COMBO_MULTIPLIERS = {
            SQUIRT_TRACK: {
                THROW_TRACK: (1.1, 'marked'),
            },

            ZAP_TRACK: {
                THROW_TRACK: (1.1, 'marked'),
            },

            SOUND_TRACK: {
                THROW_TRACK: (1.1, 'marked'),
            },

            DROP_TRACK: {
                THROW_TRACK:  (1.1, 'marked'),
                SQUIRT_TRACK: (1.1, ('soaked', 'drenched')),
                ZAP_TRACK:    (1.1, 'zapped'),
                TRAP_TRACK:  (1.1, ('trapped', 'dazed')),
            },
        }

        for i in range(4):
            if battleIndices[i] == -1:
                pass
            else:
                if tracks[i] == BattleBase.NO_ATTACK:
                    numTargets = 0
                    target = -2

                elif tracks[i] == BattleBase.PASS_ATTACK:
                    numTargets = 0
                    target = -2

                elif tracks[i] == BattleBase.NPCSOS:
                    numTargets = self.numToons

                    if targets[i] == -1:
                        numTargets = None
                        target = -1
                    else:
                        target = [targets[i]]

                        if battleIndices[i] not in target:
                            target.append(battleIndices[i])

                elif tracks[i] == BattleBase.SOS or tracks[i] == BattleBase.PETSOS:
                    numTargets = 0
                    target = -2

                elif tracks[i] == HEAL_TRACK:
                    numTargets = self.numToons

                    if self.__isGroupHeal(levels[i]):
                        target = -2
                    else:
                        target = targets[i]

                else:
                    numTargets = self.numCogs

                    if self.__isGroupAttack(tracks[i], levels[i]):
                        target = -1
                    else:
                        target = targets[i]

                        if target == -1:
                            numTargets = None

                targetSuit = None

                if isinstance(target, int) and target >= 0 and target < len(self.battle.activeSuits):
                    targetSuit = self.battle.activeSuits[target]

                # =====================================================
                # SAME-ROUND GAG COMBO PREVIEW
                # =====================================================
                comboMultiplier = 1.0
                comboCount = 0
                dropThrowMultiplier = 1.0
                countedConditions = set()

                currentTrack = tracks[i]
                currentTarget = targets[i]

                incomingThrowTargets = set()

                for x in range(4):
                    if battleIndices[x] == -1:
                        continue

                    if tracks[x] == THROW_TRACK:
                        throwTarget = targets[x]

                        if isinstance(throwTarget, int) and throwTarget >= 0:
                            incomingThrowTargets.add(throwTarget)

                trapTargets = set()

                for x in range(4):
                    if battleIndices[x] == -1:
                        continue

                    if tracks[x] == TRAP_TRACK:
                        trapTarget = targets[x]

                        if isinstance(trapTarget, int) and trapTarget >= 0:
                            trapTargets.add(trapTarget)

                wetTargets = set()

                for x in range(4):
                    if battleIndices[x] == -1:
                        continue

                    if tracks[x] == SQUIRT_TRACK:
                        squirtTarget = targets[x]

                        if isinstance(squirtTarget, int) and squirtTarget >= 0:
                            wetTargets.add(squirtTarget)

                            leftIndex = squirtTarget - 1
                            rightIndex = squirtTarget + 1

                            if leftIndex >= 0:
                                wetTargets.add(leftIndex)

                            if rightIndex < len(self.battle.activeSuits):
                                wetTargets.add(rightIndex)

                for cogIndex, cog in enumerate(self.battle.activeSuits):
                    if cog.hasSuitStatusEffect('soaked') or cog.hasSuitStatusEffect('drenched'):
                        wetTargets.add(cogIndex)

                if currentTrack in COMBO_MULTIPLIERS:
                    requiredTracks = COMBO_MULTIPLIERS[currentTrack]

                    for x in range(4):
                        if x == i:
                            continue

                        if battleIndices[x] == -1:
                            continue

                        otherTrack = tracks[x]
                        otherTarget = targets[x]

                        if otherTarget != currentTarget:
                            continue

                        if otherTrack in requiredTracks:
                            multiplier, condition = requiredTracks[otherTrack]

                            if condition in countedConditions:
                                continue

                            if targetSuit and not targetSuit.hasSuitStatusEffect(condition):
                                if currentTrack == DROP_TRACK:
                                    if otherTrack == THROW_TRACK:
                                        dropThrowMultiplier = 1.2
                                    elif otherTrack == TRAP_TRACK:
                                        comboCount += 1
                                    else:
                                        comboCount += 1
                                else:
                                    comboMultiplier *= multiplier

                                countedConditions.add(condition)

                self.toonPanels[battleIndices[i]].setValues(battleIndices[i], tracks[i], levels[i], numTargets, target, self.localNum, targetSuit, comboMultiplier, comboCount, dropThrowMultiplier, wetTargets, self.battle.activeSuits, incomingThrowTargets, trapTargets)

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

    def enterOff(self):
        if self.isLoaded:
            for toonPanel in self.toonPanels:
                toonPanel.hide()

            for cogPanel in self.cogPanels:
                cogPanel.hide()

        self.toonAttacks = [(-1, 0, 0),
         (-1, 0, 0),
         (-1, 0, 0),
         (-1, 0, 0)]
        self.target = 0
        if hasattr(self, 'timer'):
            self.timer.hide()
        if hasattr(self, 'roundCount'):
            if self.roundCountSeq:
                self.roundCountSeq.pause()
            self.roundCount.hide()
            self.roundCount.setColorScale(1, 1, 1, 0)

    def exitOff(self):
        if self.isLoaded:
            self.__enterPanels(self.numToons, self.localNum)
            self.__cogPanels(self.numCogs)
        self.timer.show()
        self.track = -1
        self.level = -1
        self.target = 0

    def enterAttack(self):
        self.attackPanel.enter()
        self.accept(self.attackPanelDoneEvent, self.__handleAttackPanelDone)

    def exitAttack(self):
        self.ignore(self.attackPanelDoneEvent)
        self.attackPanel.exit()

    def __handleAttackPanelDone(self, doneStatus):
        self.notify.debug('doneStatus: %s' % doneStatus)
        mode = doneStatus['mode']
        if mode == 'Inventory':
            self.lastActionMode = 'Inventory'
            self.track = doneStatus['track']
            self.level = doneStatus['level']
            self.toonPanels[self.localNum].setValues(self.localNum, self.track, self.level)
            if self.track == HEAL_TRACK:
                if self.__isGroupHeal(self.level):
                    response = {}
                    response['mode'] = 'Attack'
                    response['track'] = self.track
                    response['level'] = self.level
                    response['target'] = self.target
                    messenger.send(self.battleEvent, [response])
                    self.fsm.request('AttackWait')
                elif self.numToons == 3 or self.numToons == 4:
                    self.fsm.request('ChooseToon')
                elif self.numToons == 2:
                    response = {}
                    response['mode'] = 'Attack'
                    response['track'] = self.track
                    response['level'] = self.level
                    if self.localNum == 0:
                        response['target'] = 1
                    elif self.localNum == 1:
                        response['target'] = 0
                    else:
                        self.notify.error('Bad localNum value: %s' % self.localNum)
                    messenger.send(self.battleEvent, [response])
                    self.fsm.request('AttackWait')
                else:
                    self.notify.error('Heal was chosen when number of toons is %s' % self.numToons)
            elif self.__isCogChoiceNecessary():
                self.notify.debug('choice needed')
                self.fsm.request('ChooseCog')
                response = {}
                response['mode'] = 'Attack'
                response['track'] = self.track
                response['level'] = self.level
                response['target'] = -1
                messenger.send(self.battleEvent, [response])
            else:
                self.notify.debug('no choice needed')
                self.fsm.request('AttackWait')
                response = {}
                response['mode'] = 'Attack'
                response['track'] = self.track
                response['level'] = self.level
                response['target'] = 0
                messenger.send(self.battleEvent, [response])
        elif mode == 'Run':
            self.fsm.request('Run')
        elif mode == 'Surrender':
            self.fsm.request('Surrender')
        elif mode == 'SOS':
            self.fsm.request('SOS')
            self.lastActionMode = 'SOS'
        elif mode == 'Fire':
            self.fsm.request('Fire')
            self.lastActionMode = 'Fire'
        elif mode == 'Sue':
            self.fsm.request('Sue')
            self.lastActionMode = 'Sue'
        elif mode == 'Pass':
            self.lastActionMode = 'Pass'
            response = {}
            response['mode'] = 'Pass'
            response['id'] = -1
            messenger.send(self.battleEvent, [response])
            self.fsm.request('AttackWait')
        else:
            self.notify.warning('unknown mode: %s' % mode)

    def checkHealTrapLure(self):
        self.notify.debug('numToons: %s, numCogs: %s, lured: %s, trapped: %s' % (self.numToons,
         self.numCogs,
         self.luredIndices,
         self.trappedIndices))
        if len(PythonUtil.union(self.trappedIndices, self.luredIndices)) == self.numCogs:
            canTrap = 0
        else:
            canTrap = 1
        if len(self.luredIndices) == self.numCogs:
            canLure = 0
            canTrap = 0
        else:
            canLure = 1
        if self.numToons == 1:
            canHeal = 0
        else:
            canHeal = 1
        return (canHeal, canTrap, canLure)

    def adjustStatusEffects(self, toons):
        for i in range(len(toons)):
            self.toonPanels[i].setLaffMeter(toons[i])

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
        resetActivateMode = not (cogIds == self.cogs and creditLevel == self.creditLevel and luredIndices == self.luredIndices and trappedIndices == self.trappedIndices and toonIds == self.toons)
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
                self.chooseCogPanel.adjustCogs(self.numCogs, self.luredIndices, self.trappedIndices, self.track, self.level)
            elif currStateName == 'ChooseToon':
                self.chooseToonPanel.adjustToons(self.numToons, self.localNum, self.track, self.level, self.toonAvatars)
            canHeal, canTrap, canLure = self.checkHealTrapLure()
            base.localAvatar.inventory.setBattleCreditMultiplier(self.creditMultiplier)
            base.localAvatar.inventory.setActivateMode('battle', heal=canHeal, trap=canTrap, lure=canLure, bldg=self.bldg, creditLevel=self.creditLevel, tutorialFlag=self.tutorialFlag)

    def enterChooseCog(self):
        self.cog = 0
        self.chooseCogPanel.enter(self.numCogs, luredIndices=self.luredIndices, trappedIndices=self.trappedIndices, track=self.track, level=self.level)
        self.accept(self.chooseCogPanelDoneEvent, self.__handleChooseCogPanelDone)

    def exitChooseCog(self):
        self.ignore(self.chooseCogPanelDoneEvent)
        self.chooseCogPanel.exit()

    def __handleChooseCogPanelDone(self, doneStatus):
        mode = doneStatus['mode']
        if mode == 'Back':
            self.fsm.request('Attack')
        elif mode == 'Avatar':
            self.cog = doneStatus['avatar']
            self.target = self.cog
            self.fsm.request('AttackWait')
            response = {}
            response['mode'] = 'Attack'
            response['track'] = self.track
            response['level'] = self.level
            response['target'] = self.cog
            messenger.send(self.battleEvent, [response])
        else:
            self.notify.warning('unknown mode: %s' % mode)

    def enterAttackWait(self, chosenToon=-1):
        self.accept(self.waitPanelDoneEvent, self.__handleAttackWaitBack)
        self.waitPanel.enter(self.numToons, self.track, self.level, self.lastActionMode)

    def exitAttackWait(self):
        self.waitPanel.exit()
        self.ignore(self.waitPanelDoneEvent)

    def __handleAttackWaitBack(self, doneStatus):
        mode = doneStatus['mode']
        if mode == 'Back':
            if self.track == BattleBase.NPCSOS:
                self.fsm.request('ChooseToon')
            elif self.track == HEAL_TRACK:
                self.fsm.request('Attack')
            elif self.track == BattleBase.NO_ATTACK:
                self.fsm.request('Attack')
            elif self.__isCogChoiceNecessary():
                self.fsm.request('ChooseCog')
            else:
                self.fsm.request('Attack')
            response = {}
            response['mode'] = 'UnAttack'
            messenger.send(self.battleEvent, [response])
        else:
            self.notify.error('unknown mode: %s' % mode)

    def enterChooseToon(self):
        self.toon = 0
        self.chooseToonPanel.enter(
            self.numToons,
            localNum=self.localNum,
            track=self.track,
            level=self.level,
            avatars=self.toonAvatars
        )
        self.accept(self.chooseToonPanelDoneEvent, self.__handleChooseToonPanelDone)
        self.accept(self.chooseToonPanelDoneEvent + '-preview', self.__handleChooseToonPanelPreview)
        if self.track == BattleBase.NPCSOS:
            self.__handleChooseToonPanelPreview(-1)
            if self.numToons > 1:
                response = {}
                response['mode'] = 'IOUPreview'
                response['track'] = self.track
                response['level'] = self.level
                response['target'] = self.localNum
                messenger.send(self.battleEvent, [response])

    def exitChooseToon(self):
        self.ignore(self.chooseToonPanelDoneEvent)
        self.ignore(self.chooseToonPanelDoneEvent + '-preview')
        self.chooseToonPanel.exit()

    def __handleChooseToonPanelPreview(self, toonIndex):
        if self.track != BattleBase.NPCSOS:
            return
        targets = [self.localNum]
        if toonIndex >= 0 and toonIndex < self.numToons and toonIndex not in targets:
            targets.append(toonIndex)
        self.toonPanels[self.localNum].setValues(self.localNum, self.track, self.level, self.numToons, targets, self.localNum)

    def __handleChooseToonPanelDone(self, doneStatus):
        mode = doneStatus['mode']
        if mode == 'Back':
            if self.track == BattleBase.NPCSOS:
                if self.numToons > 1:
                    response = {}
                    response['mode'] = 'UnAttack'
                    messenger.send(self.battleEvent, [response])
                self.fsm.request('SOS')
            else:
                self.fsm.request('Attack')
        elif mode == 'Avatar':
            self.toon = doneStatus['avatar']
            self.target = self.toon
            self.fsm.request('AttackWait', [self.toon])
            response = {}
            response['mode'] = 'Attack'
            response['track'] = self.track
            response['level'] = self.level
            response['target'] = self.toon
            messenger.send(self.battleEvent, [response])
        else:
            self.notify.warning('unknown mode: %s' % mode)

    def setSurrenderedToons(self, surrenderedToons):
        self.surrenderedToons = list(surrenderedToons)
        for toonPanel in self.toonPanels:
            avatar = getattr(toonPanel, 'avatar', None)
            surrendered = avatar is not None and avatar.doId in self.surrenderedToons
            toonPanel.updateSurrenderState(surrendered)

    def enterSurrender(self):
        if base.localAvatar.doId in self.surrenderedToons:
            self.surrenderPanel['text'] = TTLocalizer.TownBattleSurrenderUnvote
        else:
            self.surrenderPanel['text'] = TTLocalizer.TownBattleSurrenderVote
        self.surrenderPanel.show()

    def exitSurrender(self):
        self.surrenderPanel.hide()

    def __handleSurrenderPanelDone(self, doneStatus):
        if doneStatus == DGG.DIALOG_OK:
            localToonId = base.localAvatar.doId
            localSurrenderedToons = list(self.surrenderedToons)
            if localToonId in localSurrenderedToons:
                localSurrenderedToons.remove(localToonId)
            else:
                localSurrenderedToons.append(localToonId)
            self.setSurrenderedToons(localSurrenderedToons)
            response = {'mode': 'Surrender'}
            messenger.send(self.battleEvent, [response])
        self.fsm.request('Attack')

    def enterRun(self):
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

    def enterFire(self):
        canHeal, canTrap, canLure = self.checkHealTrapLure()
        self.FireCogPanel.enter(self.numCogs, luredIndices=self.luredIndices, trappedIndices=self.trappedIndices, track=self.track, fireCosts=self.cogFireCosts)
        self.accept(self.fireCogPanelDoneEvent, self.__handleCogFireDone)

    def exitFire(self):
        self.ignore(self.fireCogPanelDoneEvent)
        self.FireCogPanel.exit()
    
    def enterSue(self):
        canHeal, canTrap, canLure = self.checkHealTrapLure()
        self.SueCogPanel.enter(self.numCogs, luredIndices=self.luredIndices, trappedIndices=self.trappedIndices, track=self.track, sueCosts=self.cogSueCosts)
        self.accept(self.sueCogPanelDoneEvent, self.__handleCogSueDone)
    
    def exitSue(self):
        self.ignore(self.sueCogPanelDoneEvent)
        self.SueCogPanel.exit()

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
            messenger.send(self.battleEvent, [response])
        else:
            self.notify.warning('unknown mode: %s' % mode)
    
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
            messenger.send(self.battleEvent, [response])
        else:
            self.notify.warning('unknown mode: %s' % mode)

    def enterSOS(self):
        canHeal, canTrap, canLure = self.checkHealTrapLure()
        self.SOSPanel.enter(canLure, canTrap)
        for panel in self.toonPanels:
            panel.stash()
        self.accept(self.SOSPanelDoneEvent, self.__handleSOSPanelDone)

    def exitSOS(self):
        self.ignore(self.SOSPanelDoneEvent)
        self.SOSPanel.exit()
        for panel in self.toonPanels:
            panel.unstash()

    def __handleSOSPanelDone(self, doneStatus):
        mode = doneStatus['mode']
        if mode == 'Friend':
            doId = doneStatus['friend']
            response = {}
            response['mode'] = 'SOS'
            response['id'] = doId
            messenger.send(self.battleEvent, [response])
            self.fsm.request('AttackWait')
        elif mode == 'Pet':
            self.petId = doneStatus['petId']
            self.petName = doneStatus['petName']
            self.fsm.request('SOSPetSearch')
        elif mode == 'NPCFriend':
            doId = doneStatus['friend']
            subtype = IOURegistry.getSubtypeByNPCId(doId)
            if subtype is None:
                self.fsm.request('SOS')
                return
            self.track = BattleBase.NPCSOS
            self.level = subtype
            self.lastActionMode = 'IOU'
            self.fsm.request('ChooseToon')
        elif mode == 'Back':
            self.fsm.request('Attack')

    def enterSOSPetSearch(self):
        response = {}
        response['mode'] = 'PETSOSINFO'
        response['id'] = self.petId
        self.SOSPetSearchPanel.enter(self.petId, self.petName)
        self.proxyGenerateMessage = 'petProxy-%d-generated' % self.petId
        self.accept(self.proxyGenerateMessage, self.__handleProxyGenerated)
        self.accept(self.SOSPetSearchPanelDoneEvent, self.__handleSOSPetSearchPanelDone)
        messenger.send(self.battleEvent, [response])

    def exitSOSPetSearch(self):
        self.ignore(self.proxyGenerateMessage)
        self.ignore(self.SOSPetSearchPanelDoneEvent)
        self.SOSPetSearchPanel.exit()

    def __handleSOSPetSearchPanelDone(self, doneStatus):
        mode = doneStatus['mode']
        if mode == 'Back':
            self.fsm.request('SOS')
        else:
            self.notify.error('invalid mode in handleSOSPetSearchPanelDone')

    def __handleProxyGenerated(self):
        self.fsm.request('SOSPetInfo')

    def enterSOSPetInfo(self):
        self.SOSPetInfoPanel.enter(self.petId)
        self.accept(self.SOSPetInfoPanelDoneEvent, self.__handleSOSPetInfoPanelDone)

    def exitSOSPetInfo(self):
        self.ignore(self.SOSPetInfoPanelDoneEvent)
        self.SOSPetInfoPanel.exit()

    def __handleSOSPetInfoPanelDone(self, doneStatus):
        mode = doneStatus['mode']
        if mode == 'OK':
            response = {}
            response['mode'] = 'PETSOS'
            response['id'] = self.petId
            response['trickId'] = doneStatus['trickId']
            messenger.send(self.battleEvent, [response])
            self.fsm.request('AttackWait')
            bboard.post(PetConstants.OurPetsMoodChangedKey, True)
        elif mode == 'Back':
            self.fsm.request('SOS')

    def __isCogChoiceNecessary(self):
        return self.numCogs > 1 and not self.__isGroupAttack(self.track, self.level)

    def __isGroupAttack(self, trackNum, levelNum):
        retval = BattleBase.attackAffectsGroup(trackNum, levelNum)
        return retval

    def __isGroupHeal(self, levelNum):
        retval = BattleBase.attackAffectsGroup(HEAL_TRACK, levelNum)
        return retval
    
    def __handleWithinTimer(self, *args, **kwargs):
        if not self.battle:
            return

        currRound = max(1, self.battle.TurnsElapsed + 1)
        self.roundCount['text'] = 'Round %d' % currRound
        self.roundCount['text_scale'] = 0.043 if currRound >= 100 else 0.05

        if self.roundCountSeq:
            self.roundCountSeq.pause()
        self.roundCount.setColorScale(1, 1, 1, 0)
        self.roundCountSeq = Sequence(
            Func(self.roundCount.show),
            LerpColorScaleInterval(self.roundCount, 0.08, (1, 1, 1, 1)))
        self.roundCountSeq.start()

    def __handleWithoutTimer(self, *args, **kwargs):
        if self.roundCountSeq:
            self.roundCountSeq.pause()
        self.roundCountSeq = Sequence(
            LerpColorScaleInterval(self.roundCount, 0.08, (1, 1, 1, 0)),
            Func(self.roundCount.hide))
        self.roundCountSeq.start()
