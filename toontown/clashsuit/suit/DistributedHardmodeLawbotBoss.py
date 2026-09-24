from toontown.gui.game.condition import ConditionGlobals
from toontown.clashsuit.suit import BossCogGlobals
from toontown.clashsuit.suit.ClashLawbotBoss import *
from toontown.clashsuit.suit import ClashLawbotBossSuit
from toontown.clashbattle.battle import MovieUtil
from toontown.clashbattle.battle import SuitBattleGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.nametag import NametagGroup
from toontown.nametag import NametagGlobals
from toontown.chat.constants.ChatGlobals import *

@DirectNotifyCategory()
class DistributedHardmodeLawbotBoss(ClashLawbotBoss):
    def __init__(self, cr):
        ClashLawbotBoss.__init__(self, cr)
        FSM.FSM.__init__(self, 'DistributedHardmodeLawbotBoss')
        self.nextLocalDoId = -50
        self.introductionSpotlights = [None, None, None, None, None, None]
        self.introductionVirtuals = [None, None, None, None, None, None]
        self.litigationOrder = ['stenog', 'sgoat', 'lgator', 'caseman']
        self.litigationTeam = []
        self.litigationMembersUpdated = {0: [], 1: []}
        self.areaAttackSeq = None

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        ClashLawbotBoss.announceGenerate(self)
        self.bossLandSfx = self.boomSfx

   # def addSpeedchatMenu(self):
    #    base.localAvatar.chatContainer.speedChatMenu.addHardModeCLOMenu()

   # def removeSpeedchatMenu(self):
    #    base.localAvatar.chatContainer.speedChatMenu.removeHardModeCLOMenu()

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        ClashLawbotBoss.disable(self)
        self.cleanupIntroductionSpotlights()
        self.cleanupIntroductionVirtuals()
        self.cleanupLitigationTeam()

        if self.areaAttackSeq is not None:
            self.areaAttackSeq.finish()
            self.areaAttackSeq = None

        # Remove any lingering tasks
        taskMgr.remove(self.uniqueName('RetryDefenseSpecialistSpawn'))

    def loadEnvironment(self):
        ClashBossCog.ClashBossCog.loadEnvironment(self)
        self.geom = loader.loadModel('phase_11/models/lawbotHQ/LawbotBossRoom')
        self.geom.setPos(0, 0, -71.601)
        self.geom.setScale(1)
        self.elevatorEntrance = self.geom.find('**/elevator_origin')
        self.elevatorEntrance.getChildren().detach()
        self.elevatorEntrance.setScale(1)
        self.elevA = self.geom.find('**/elevator_L_origin')
        self.elevA.getChildren().detach()
        self.elevA.setScale(1)
        self.elevB = self.geom.find('**/elevator_R_origin')
        self.elevB.getChildren().detach()
        self.elevB.setScale(1)
        elevatorModel = loader.loadModel('phase_11/models/lawbotHQ/LB_Elevator')
        elevatorModel.reparentTo(self.elevatorEntrance)
        self.setupElevator(elevatorModel)
        self.elevAModel = loader.loadModel('phase_11/models/lawbotHQ/LB_Elevator')
        self.elevAModel.reparentTo(self.elevA)
        self.setupLeftElevator(self.elevAModel)
        self.elevBModel = loader.loadModel('phase_11/models/lawbotHQ/LB_Elevator')
        self.elevBModel.reparentTo(self.elevB)
        self.setupRightElevator(self.elevBModel)
        self.elevatorMusic = 'clo_hard_elevator'
        self.promotionMusic = 'clo_hard_intro_cutscene'
        self.stingMusic = 'clo_hard_battle_two_cutscene'
        self.battleOneMusic = 'clo_hard_battle_one'
        self.cannonCtscMusic = 'clo_hard_cannon_cutscene'
        self.battleThreeMusic = 'clo_hard_battle_three'
        self.betweenBattleMusic = 'clo_hard_megaphone_cutscene'
        self.battleFourMusic = 'clo_hard_battle_four'
        self.battleFourDizzyMusic = 'clo_hard_battle_four_stunned'
        self.killMusic = 'clo_hard_battle_stinger'
        self.victoryMusic = 'clo_hard_victory'
        self.epilogueMusic = 'clo_hard_epilogue'

        # Litigation Team Music Files
        prefix = 'clo_hard_litigation_'
        self.litigationBase = base.musicMgr.loadMusic(f'{prefix}base')
        self.casemgrMusic = base.musicMgr.loadMusic(f'{prefix}casemgr')
        self.litigatorMusic = base.musicMgr.loadMusic(f'{prefix}litigator')
        self.scapegoatMusic = base.musicMgr.loadMusic(f'{prefix}scapegoat')
        self.stenographMusic = base.musicMgr.loadMusic(f'{prefix}stenograph')
        self.litigationMusic = {'caseman': self.casemgrMusic,
                                'lgator': self.litigatorMusic,
                                'sgoat': self.scapegoatMusic,
                                'stenog': self.stenographMusic}
        self.litigationMusicPlaying = []
        # Store the litigation suits that we have
        self.litigationSuits = []
        self.musicSeq = None
        self.preloadFinalBattleMusic()

        plane = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, -50)))
        planeNode = CollisionNode('dropPlane')
        planeNode.addSolid(plane)
        planeNode.setCollideMask(ToontownGlobals.PieBitmask)
        self.geom.attachNewNode(planeNode)
        self.geom.reparentTo(render)
        self.loadEvidenceBox()
        self.evidenceBox.hide()
        self.trapdoorMid = self.geom.find('**/trapdoor_mid')
        self.trapdoorRotateNode = render.attachNewNode('rotateNode')
        self.trapdoorRotateNode.setPos(self.trapdoorMid, 1, 0, -0.75)
        self.trapdoorMid.wrtReparentTo(self.trapdoorRotateNode)
        self.gavel_zero = self.geom.find("**/gavel_0")
        self.gavelZeroRotateNode = render.attachNewNode('gavelZeroRotateNode')
        self.gavelZeroRotateNode.setPos(self.gavel_zero, 0, 0, -1)
        self.gavel_one = self.geom.find("**/gavel_1")
        self.gavelOneRotateNode = render.attachNewNode('gavelOneRotateNode')
        self.gavelOneRotateNode.setPos(self.gavel_one, 0, 0, -1)

    def setLitigationTeamMusic(self, suits):
        # We are using base.playMusic as opposed to through the music manager for these for sake of speed.
        # We loaded these through the music manager earlier, however we need these to be as synced up as possible.

        suitNames = []
        for suit in suits:
            suitNames.append(suit.dna.name)
            if suit.dna.name in self.litigationMusic:
                music = self.litigationMusic[suit.dna.name]
                # Only start the music again if it is not playing currently.
                if music not in self.litigationMusicPlaying:
                    self.litigationMusicPlaying.append(music)

        # For each suit that is a litigator but isn't in our battle, stop their music if it is playing.
        for suitName in list(self.litigationMusic.keys()):
            if suitName not in suitNames:
                music = self.litigationMusic[suitName]
                if music in self.litigationMusicPlaying:
                    music.setVolume(0)
                    self.litigationMusicPlaying.remove(music)

        if self.litigationBase.status() != self.litigationBase.PLAYING:
            base.playMusic(self.litigationBase, looping=1, volume=1.1, interrupt=0)
            # all layers are "playing" always but the inactive ones are silent
            base.playMusic(self.stenographMusic, looping=1, volume=0, interrupt=0, time=self.litigationBase.getTime())
            base.playMusic(self.scapegoatMusic, looping=1, volume=0, interrupt=0, time=self.litigationBase.getTime())
            base.playMusic(self.casemgrMusic, looping=1, volume=0, interrupt=0, time=self.litigationBase.getTime())
            base.playMusic(self.litigatorMusic, looping=1, volume=0, interrupt=0, time=self.litigationBase.getTime())

        for music in self.litigationMusicPlaying:
            music.setVolume(1.1)

    def handleToonoMusicIn(self, gameMusic):
        if gameMusic is not None:
            base.musicMgr.playMusic(gameMusic, looping = 1, interrupt = False, volume = 0)

            muteSeq = Parallel()
            for music in self.litigationMusicPlaying:
                if music is not None:
                    muteSeq.append(LerpFunctionInterval(music.setVolume, fromData = music.getVolume(), toData = 0,
                                                        duration = 1.5))

            self.musicSeq = Parallel(
                muteSeq,
                LerpFunctionInterval(gameMusic.setVolume, fromData = gameMusic.getVolume(), toData = 1,
                                     duration = 1.5),
            )
            self.musicSeq.start()

    def handleToonoMusicOut(self, gameMusic):
        if gameMusic is not None:
            self.finishMusicSeq()

            unmuteSeq = Parallel()
            for music in self.litigationMusicPlaying:
                if music is not None:
                    unmuteSeq.append(LerpFunctionInterval(music.setVolume, fromData=music.getVolume(), toData=1,
                                                          duration=1.5))

            self.musicSeq = Sequence(
                Parallel(
                    unmuteSeq,
                    LerpFunctionInterval(gameMusic.setVolume, fromData=gameMusic.getVolume(),
                                         toData=0, duration=1.5),
                ),
                Func(base.musicMgr.stopMusic, gameMusic)
            )
            self.musicSeq.start()

    def finishMusicSeq(self) -> None:
        if self.musicSeq is not None:
            self.musicSeq.finish()
            self.musicSeq = None

    def unloadEnvironment(self):
        ClashBossCog.ClashBossCog.unloadEnvironment(self)
        self.geom.removeNode()
        del self.geom
        self.trapdoorMid.removeNode()
        del self.trapdoorMid
        self.trapdoorRotateNode.removeNode()
        del self.trapdoorRotateNode
        self.gavel_zero.removeNode()
        del self.gavel_zero
        self.gavelZeroRotateNode.removeNode()
        del self.gavelZeroRotateNode
        self.gavel_one.removeNode()
        del self.gavel_one
        self.gavelOneRotateNode.removeNode()
        del self.gavelOneRotateNode

    def enterElevator(self):
        base.discord.applyPreset('boss-ol-1')
        ClashBossCog.ClashBossCog.enterElevator(self)
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleOnePosHpr)
        self.reparentTo(render)
        self.happy = 1
        self.raised = 1
        self.forward = 1
        self.doAnimate()
        self.showWitnessToon()
        self.showLawyerToon()
        self.witnessToon.setDisplayName(TTLocalizer.WitnessToonName)
        self.lawyerToon.setDisplayName(TTLocalizer.LawyerToonName)
        base.camera.reparentTo(self.elevatorModel)
        base.camera.setPosHpr(0, 30, 8, 180, 0, 0)
        base.camLens.setMinFov(ToontownGlobals.CJElevatorFov / (4. / 3.))

    def enterIntroduction(self):
        self.reparentTo(render)
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleTablePosHpr)
        self.stopAnimate()
        base.camera.setPosHpr(0, 30, 8, 180, 0, 0)
        base.camera.reparentTo(self.elevatorModel)
        base.camLens.setMinFov(ToontownGlobals.CJElevatorFov / (4. / 3.))
        self.makeCogRoundSpotlights()
        self.makeIntroductionSpotlights()
        self.makeIntroductionVirtuals()
        ClashBossCog.ClashBossCog.enterIntroduction(self)
        self.battleANode.setPosHpr(*BossCogGlobals.HardmodeLawyerVirtualBattleAPosHpr)
        self.battleBNode.setPosHpr(*BossCogGlobals.HardmodeLawyerVirtualBattleBPosHpr)
        base.musicMgr.playMusic(self.promotionMusic, looping=1, volume=0.9)
        self.acceptOnce('skipCutscene', self.__beginBattleOne)

    def __beginBattleOne(self):
        intervalName = 'IntroductionMovie'
        self.clearInterval(intervalName)
        self.doneBarrier('Introduction')

    def exitIntroduction(self):
        self.ignore('skipCutscene')
        ClashBossCog.ClashBossCog.exitIntroduction(self)
        self.closeEntryDoors(animated=0)
        self.hideWitnessToon()
        self.hideLawyerToon()
        self.cleanupIntroductionSpotlights()
        self.cleanupIntroductionVirtuals()

    def enterBattleOne(self):
        ClashBossCog.ClashBossCog.enterBattleOne(self)
        base.musicMgr.playMusic(self.battleOneMusic, looping=1, volume=1.2)
        self.reparentTo(render)
        if self.battleA:
            self.showCogRoundSpotlight(0)
        if self.battleB:
            self.showCogRoundSpotlight(1)
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleTablePosHpr)

        self.clearChat()
        self.loop('Ff_neutral')
        base.discord.applyPreset('boss-ol-2')

    # Networked Order for the minibosses, update should be received before makePrepareBattleTwoMovie() is called.
    def setLitigationOrder(self, litigationOrder):
        self.litigationOrder = litigationOrder

    # After a battle side dies, move the "fake" suits to the given battle side's position.
    def updateLitigationMemberPosition(self, name, battleSide):
        # Shouldn't happen, but just in case...
        if name not in self.litigationOrder:
            return

        suit = self.litigationTeam[self.litigationOrder.index(name)]
        poshpr = [BossCogGlobals.LawyerBattleAPosHpr, BossCogGlobals.LawyerBattleBPosHpr][battleSide]
        # If there were other adjusted members, do some position stuff to make sure they don't clip into each other.
        yBonus = 0
        if len(self.litigationMembersUpdated[battleSide]) > 0:
            for member in self.litigationMembersUpdated[battleSide]:
                otherSuit = self.litigationTeam[self.litigationOrder.index(member)]
                otherSuit.setY(otherSuit.getY() - 2.5)
                yBonus += 2.5

        suit.setPos(self, poshpr[0], poshpr[1] + yBonus + 14.5, poshpr[2])
        suit.loop('neutral')
        # Reset the nametag since it was tampered with earlier to look better while sitting in a chair.
        suit.nametag3d.setPos(0, 0, suit.height + 1.0)
        suit.headsUp(base.localAvatar)
        suit.show()
        # Make fun of the toon since they died.
        # suit.setChatAbsolute(TTLocalizer.LawbotLitigationToonsDied[name], CFSpeech | CFTimeout)
        # replaced with gameover dialogue
        self.litigationMembersUpdated[battleSide].append(name)

    def enterPrepareBattleTwo(self):
        self.cleanupIntervals()
        self.controlToons()
        self.setToonsToNeutral(self.involvedToons)
        self.toonsLineUpBattleTwo()
        self.battleANode.setPosHpr(*BossCogGlobals.HMLawyerBattleAPosHpr)
        self.battleBNode.setPosHpr(*BossCogGlobals.HMLawyerBattleBPosHpr)
        self.showWitnessToon()
        self.witnessToon.setPosHpr(30, 50, 0, 90, 0, 0)
        self.showLawyerToon()
        self.lawyerToon.setPosHpr(-30, 50, 0, -90, 0, 0)
        intervalName = 'PrepareBattleTwoMovie'
        delayDeletes = []
        seq = Sequence(self.__makePrepareBattleTwoMovie(delayDeletes), Func(self.__onToBattleTwo), name=intervalName)
        seq.delayDeletes = delayDeletes
        seq.start()
        self.storeInterval(seq, intervalName)
        base.musicMgr.playMusic(self.stingMusic, looping=0, volume=1.0)
        self.acceptOnce('skipCutscene', self.__onToBattleTwo)

    def exitPrepareBattleTwo(self):
        self.ignore('skipCutscene')
        self.clearInterval('PrepareBattleTwoMovie')
        self.closeEntryDoors(animated=0)
        self.hideWitnessToon()
        self.hideLawyerToon()

    def __onToBattleTwo(self, elapsedTime = 0):
        self.doneBarrier("PrepareBattleTwo")

    def enterBattleTwo(self):
        self.cleanupIntervals()
        self.reparentTo(render)
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleTablePosHpr)
        self.clearChat()
        self.setToonsToNeutral(self.involvedToons)
        base.musicMgr.stopMusic()
        # mult = BattleGlobals.getBossBattleCreditMultiplier(2)
        # localAvatar.inventory.setBattleCreditMult(mult)
        self.setBattleCreditMult(2)
        self.toonsToBattlePosition(self.toonsA, self.battleANode)
        self.toonsToBattlePosition(self.toonsB, self.battleBNode)
        self.releaseToons()
        base.discord.applyPreset('boss-ol-3')
        self.deleteCogRoundSpotlights()
        self.accept("playPicnicMusic", self.handleToonoMusicIn)
        self.accept("stopPicnicMusic", self.handleToonoMusicOut)

    def exitBattleTwo(self):
        self.cleanupBattles()
        self.cleanupLitigationTeam()
        base.musicMgr.stopMusic(self.litigationBase)
        for music in list(self.litigationMusic.values()):
            base.musicMgr.stopMusic(music)
        # localAvatar.inventory.setBattleCreditMult(1)

    def enterPrepareBattleThree(self):
        self.cleanupIntervals()
        self.controlToons()
        self.closeEntryDoors(animated=0)
        self.setToonsToNeutral(self.involvedToons)
        self.clearChat()
        self.reparentTo(render)
        base.camera.setPosHpr(self.elevatorModel, 0, -265, 18, 180, 7, 0)
        self.showLawyerToon()
        self.lawyerToon.setPosHpr(-6, 85, 0, -20, 0, 0)
        self.showWitnessToon()
        self.witnessToon.setPosHpr(6, 85, 0, 20, 0, 0)
        self.cleanupLitigationTeam()
        intervalName = 'PrepareBattleThreeMovie'
        [gav.nodePath.setScale(.01) for gav in list(self.gavels.values())]
        seq = Sequence(self.__makePrepareBattleThreeMovie(), Func(self.__onToBattleThree), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        base.musicMgr.playMusic(self.cannonCtscMusic, looping=0, volume=1.0)
        self.acceptOnce('skipCutscene', self.__onToBattleThree)

    def __onToBattleThree(self, elapsedTime = 0):
        self.doneBarrier('PrepareBattleThree')

    def exitPrepareBattleThree(self):
        self.ignore('skipCutscene')
        self.clearInterval('PrepareBattleThreeMovie')
        self.show()
        [gav.nodePath.setScale(gav.scale) for gav in list(self.gavels.values())]

    def enterBattleThree(self):
        self.stashFurniture()
        self.cleanupIntervals()
        self.reparentTo(render)
        self.addPaperParticles()
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleTwoPosHpr)
        self.clearChat()
        self.witnessToon.clearChat()
        self.releaseToons(finalBattle=1)
        self.showWitnessToon()
        base.localAvatar.cameraFSM.request("Orbit")
        self.evidenceRoundTimer = ToontownTimer.ToontownTimer()
        self.evidenceRoundTimer.posInTopRightCorner()
        self.evidenceRoundTimer.countdown(BossCogGlobals.LawbotBossEvidenceRoundTime)
        base.musicMgr.playMusic(self.battleThreeMusic, looping=1, volume=0.9)
        for index in range(len(self.cannons)):
            cannon = self.cannons[index]
            cannon.cannonNode.show()
        for i in range(10):
            self.openPainting(i, finalBattle=1)
        self.evidenceBox.show()
        self.evidenceBox.loop("idle")
        base.cr.gameGui.expBar.hide()
        self.departmentExpBar = DepartmentExperienceBar.DepartmentExperienceBar(base.localAvatar.departmentExp[ToontownGlobals.DEPARTMENT_LAWBOT], base.localAvatar.departmentLevels[ToontownGlobals.DEPARTMENT_LAWBOT], ToontownGlobals.DEPARTMENT_LAWBOT, base.localAvatar.style)
        self.departmentExpBar.setAvatar(base.localAvatar)
        self.departmentExpBar.setScale(0.075)
        self.departmentExpBar.reparentTo(base.a2dBottomLeft)
        self.departmentExpBar.start()
        self.evidenceGUI = EvidenceGUI.EvidenceGUI(hardmode=True)
        self.evidenceGUI.reparentTo(base.a2dBottomRight)
        self.setPickable(1)
        base.discord.applyPreset('boss-ol-4')

    def exitBattleThree(self):
        self.cleanupBattles()
        self.removePaperParticles()
        for i in range(10):
            self.closePainting(i, finalBattle=1)
        if self.evidenceRoundTimer:
            self.evidenceRoundTimer.destroy()
            self.evidenceRoundTimer = None
        if self.departmentExpBar:
            self.departmentExpBar.hide()
            self.departmentExpBar.stop()
            self.departmentExpBar.destroy()
        if self.evidenceGUI:
            self.evidenceGUI.hide()
            self.evidenceGUI.destroy()
        base.cr.gameGui.expBar.show()

    def enterPrepareBattleFour(self):
        self.stashFurniture()
        self.evidenceBox.show()
        self.evidenceBox.loop("idle")
        self.cleanupIntervals()
        self.releaseToons(finalBattle=1)
        self.controlToons()
        self.setToonsToNeutral(self.involvedToons)
        self.toonsLineUpBattleFour()
        self.clearChat()
        self.reparentTo(render)
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleTwoPosHpr)
        base.musicMgr.playMusic(self.betweenBattleMusic, looping=1, volume=0.9)
        self.showLawyerToon()
        self.lawyerToon.setPosHpr(-6, 85, 0, -20, 0, 0)
        self.showWitnessToon()
        self.witnessToon.setPosHpr(6, 85, 0, 20, 0, 0)
        self.cleanupLitigationTeam()
        prepareBattleFourMovie = self.__makePrepareBattleFourMovie()
        intervalName = 'prepareBattleFour'
        seq = Sequence(prepareBattleFourMovie, Func(self.__onToBattleFour), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        self.acceptOnce('skipCutscene', self.__onToBattleFour)

    def __onToBattleFour(self):
        self.doneBarrier('PrepareBattleFour')

    def exitPrepareBattleFour(self):
        self.ignore('skipCutscene')
        self.show()
        taskMgr.remove(self.uniqueName('WaitingMessage'))
        intervalName = 'PrepareBattleFour'
        self.clearInterval(intervalName)
        self.clearOnscreenMessage()

    def enterBattleFour(self):
        ClashBossCog.ClashBossCog.enterBattleFour(self)
        # self.find('**/NearBoss').show() # DEBUG
        base.localAvatar.cameraFSM.request("Orbit")
        self.clearChat()
        self.hideWitnessToon()
        self.hideLawyerToon()
        self.witnessToon.clearChat()
        self.reparentTo(render)
        self.happy = 1
        self.raised = 1
        self.forward = 1
        self.doAnimate()
        self.accept(self.enterEvidenceBoxEvent, self.withdrawEvidence)
        self.accept('soundSplash', self.soundHit)
        self.accept('localSoundSplash', self.localSoundHit)
        self.accept('outOfSound', self.outOfSound)
        self.accept('begin-sound', self.foundSoundButton)
        localAvatar.setCameraFov(ToontownGlobals.BossBattleCameraFov)
        taskMgr.doMethodLater(30, self.howToGetSound, self.uniqueName('SoundAdvice'))
        self.stickBossToFloor()
        self.releaseToons(finalBattle=1)
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleTwoPosHpr)
        self.generateHealthBar()
        self.updateHealthBar()
        self.healthGui.createBossCogHead()
        self.healthGui.moveInInitial()
        base.musicMgr.playMusic(self.battleFourMusic, looping=1, volume=0.9)
        base.cr.gameGui.expBar.hide()
        self.departmentExpBar = DepartmentExperienceBar.DepartmentExperienceBar(base.localAvatar.departmentExp[ToontownGlobals.DEPARTMENT_LAWBOT], base.localAvatar.departmentLevels[ToontownGlobals.DEPARTMENT_LAWBOT], ToontownGlobals.DEPARTMENT_LAWBOT, base.localAvatar.style)
        self.departmentExpBar.setAvatar(base.localAvatar)
        self.departmentExpBar.setScale(0.075)
        self.departmentExpBar.reparentTo(base.a2dBottomLeft)
        self.departmentExpBar.start()
        base.discord.applyPreset('boss-ol-5')

        # Tell condition manager to pull up dept bars/sound gags
        stateArgs = ConditionGlobals.ConditionStateArgs()
        stateArgs[ConditionGlobals.ConditionStateArg.BOSS] = self
        messenger.send(ConditionGlobals.SetStateMsg, [ConditionGlobals.ConditionState.BOSS_CLO, stateArgs])

    def exitBattleFour(self):
        ClashBossCog.ClashBossCog.exitBattleFour(self)
        bossDoneEventName = self.uniqueName('DestroyedBoss')
        self.ignore(bossDoneEventName)
        taskMgr.remove(self.uniqueName('StandUp'))
        self.ignore(self.enterEvidenceBoxEvent)
        self.ignore('soundHit')
        self.ignore('localSoundHit')
        self.ignore('outOfSound')
        self.ignore('begin-sound')
        self.clearOnscreenMessage()
        taskMgr.remove(self.uniqueName('SoundAdvice'))
        taskMgr.remove(self.uniqueName('RetryDefenseSpecialistSpawn'))
        localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        self.unstickBoss()
        self.setDizzy(0)
        self.battleFourMusicTime = base.musicMgr.getMusicTime(self.battleFourMusic)
        self.interruptBossDamageMovie()
        if self.departmentExpBar:
            self.departmentExpBar.hide()
            self.departmentExpBar.stop()
            self.departmentExpBar.destroy()

    def enterVictory(self):
        base.localAvatar.cleanupSoundModel()
        base.localAvatar.cleanupMegaphone()
        self.cleanupIntervals()
        self.reparentTo(render)
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleThreePosHpr)
        self.loop('neutral')
        localAvatar.setCameraFov(ToontownGlobals.BossBattleCameraFov)
        self.clearChat()
        self.witnessToon.clearChat()
        self.controlToons()
        base.localAvatar.setFriendsListButtonActive(0)
        self.setToonsToNeutral(self.involvedToons)
        self.toonsLineUpVictory()
        self.happy = 1
        self.raised = 1
        self.forward = 1
        intervalName = 'VictoryMovie'
        self.victorySequence = Sequence(self.makeVictoryMovie(), Func(self.__continueVictory), name=intervalName)
        self.victorySequence.start()
        self.storeInterval(self.victorySequence, intervalName)
        base.musicMgr.playMusic(self.battleFourMusic, looping=1, volume=0.9, time=self.battleFourMusicTime)
        if self.departmentExpBar:
            self.departmentExpBar.hide()
            self.departmentExpBar.stop()
            self.departmentExpBar.destroy()
        base.cr.gameGui.expBar.show()

    def __continueVictory(self):
        self.stopAnimate()
        if self.healthGui:
            self.healthGui.moveOutEnd()
        self.doneBarrier('Victory')

    def exitVictory(self):
        self.stopAnimate()
        self.unstash()
        localAvatar.setCameraFov(settings['fieldofview'] + 8)
        self.battleFourMusicTime = base.musicMgr.getMusicTime(self.battleFourMusic)
        self.birdsSfx.stop()

    def enterReward(self):
        self.cleanupIntervals()
        self.clearChat()
        self.showWitnessToon()
        self.witnessToon.clearChat()
        self.stash()
        self.stopAnimate()
        self.controlToons()
        panelName = self.uniqueName('reward')
        self.rewardPanel = RewardPanel.RewardPanel(panelName)
        victory, camVictory, skipper = MovieToonVictory.doToonVictory(
            1, self.involvedToons, self.toonRewardIds, self.toonRewardDicts,
            self.rewardPanel, 0, self.updatedQuests, noSkip=True
        )
        ival = Sequence(Parallel(victory, camVictory), Func(self.__doneReward))
        intervalName = 'RewardMovie'
        delayDeletes = []
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'HardmodeLawbotBoss.enterReward'))

        ival.delayDeletes = delayDeletes
        ival.start()
        self.storeInterval(ival, intervalName)
        if base.musicMgr.getMusicFilepath(self.victoryMusic) != base.musicMgr.getMusicFilepath(self.battleFourMusic):  # We have a custom victory theme loaded
            base.musicMgr.playMusic(self.victoryMusic, looping=1, volume=0.9)
        else:
            base.musicMgr.playMusic(self.battleFourMusic, looping=1, volume=0.9, time=self.battleFourMusicTime)

        # Have condition manager go back to normal
        messenger.send(ConditionGlobals.SetStateMsg, [ConditionGlobals.ConditionState.GLOBAL])

    def __doneReward(self):
        self.doneBarrier('Reward')
        self.toWalkMode()

    def exitReward(self):
        intervalName = 'RewardMovie'
        self.clearInterval(intervalName)
        self.unstash()
        self.rewardPanel.destroy()
        del self.rewardPanel
        self.battleFourMusicTime = 0
        base.musicMgr.stopMusic()

    def enterEpilogue(self):
        self.cleanupIntervals()
        self.clearChat()
        self.witnessToon.clearChat()
        self.stash()
        self.stopAnimate()
        self.controlToons()
        self.hideToonsMeters()
        self.showWitnessToon()
        self.witnessToon.reparentTo(render)
        self.witnessToon.setPosHpr(*BossCogGlobals.LawbotBossWitnessEpiloguePosHpr)
        self.witnessToon.takeOffSuit()
        self.arrangeToonsAroundWitnessToon()
        base.camera.reparentTo(render)
        base.camera.setPos(self.witnessToon, -9, 12, 6)
        base.camera.lookAt(self.witnessToon, 0, 0, 3)
        intervalName = 'EpilogueMovie'
        seq = Sequence(self.makeEpilogueMovie(), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        self.accept('nextChatPage', self.__epilogueChatNext)
        self.accept('doneChatPage', self.__doneEpilogue)
        base.musicMgr.playMusic(self.epilogueMusic, looping=1, volume=0.9)

    def __epilogueChatNext(self, pageNumber, elapsed):
        if pageNumber == self.localUniteEffectPageNumber:
            self.handleLocalUniteEffect()

    def __doneEpilogue(self, elapsedTime = 0):
        intervalName = 'EpilogueMovieToonAnim'
        self.ignore('nextChatPage')
        self.ignore('doneChatPage')
        self.clearInterval(intervalName)
        track = Parallel(Sequence(Wait(0.5), Func(self.localToonToSafeZone)))
        self.storeInterval(track, intervalName)
        track.start()

    def exitEpilogue(self):
        self.clearInterval('EpilogueMovieToonAnim')
        self.unstash()
        self.ignore('doneChatPage')
        base.musicMgr.stopMusic(self.epilogueMusic)

    def createBossTrapMovie(self, trapIndex, defenseSpecialistsMade, doForcedAreaAttack):
        def startForcedAreaAttack():
            if self.areaAttackSeq is not None:
                self.areaAttackSeq.pause()
                self.areaAttackSeq = None

            self.areaAttackSeq = Sequence(Func(self.announceForcedAreaAttack),
                                          Wait(.1),
                                          Func(self.announceForcedAreaAttack),
                                          Wait(.1),
                                          Func(self.announceForcedAreaAttack),
                                          Wait(.1),
                                          Func(self.announceForcedAreaAttack),
                                          Wait(.1),
                                          Func(self.announceForcedAreaAttack),
                                          Func(self.resetJumpFullTime))
            self.areaAttackSeq.start()

        self.interruptBossDamageMovie()
        trap = self.traps[trapIndex]
        trapLevel = trap.getTrapLevel()
        bossTrack = Sequence()
        if trapLevel == 5:
            sfx = BattleSounds.globalBattleSoundCache.getSound('TL_trap_door.ogg')
            bossTrack.append(
                Parallel(
                    Sequence(Wait(2), LerpPosInterval(self, 1.0, Point3(self.getX(), self.getY(), -150))),
                    Sequence(Wait(1), SoundInterval(sfx, node=trap.trap, volume=0.65, duration=2.0))
                )
            )
        else:
            sfx = BattleSounds.globalBattleSoundCache.getSound('TL_quicksand.ogg')
            bossTrack.append(
                Parallel(
                    LerpPosInterval(self, 3.0, Point3(self.getX(), self.getY(), -100)),
                    Sequence(Wait(1.0), SoundInterval(sfx, node=trap.trap, volume=0.65, duration=2.0))
                )
            )

        x, y, h = self.randomFallPos

        bossTrack.append(Func(self.hide))
        bossTrack.append(Func(self.setPos, x, y, -25))
        bossTrack.append(Func(self.setHpr, h, 0, 0))
        if defenseSpecialistsMade:
            bossTrack.append(Func(self.handleDefenseSpecialistSpawn))
        bossTrack.append(Func(self.show))
        bossTrack.append(Parallel(LerpPosInterval(self, 0.5, Point3(x, y, -71.606)),
                                  Func(self.doAnimate, 'Ff_trapfall', now=1, raised=1),
                                  Func(self.specialHead.play, 'Ff_trapfall'),
                                  ))
        if doForcedAreaAttack:
            bossTrack.append(Func(startForcedAreaAttack))
        bossTrack.append(SoundInterval(self.bossLandSfx, duration=1.9))

        if doForcedAreaAttack:
            bossTrack = Parallel(Sequence(Wait(2.29),
                                          Func(base.localAvatar.doBossJumpIndicator),
                                          Func(base.playSfx, self.warningSfx)),
                                 bossTrack)

        target = loader.loadModel('phase_11/models/lawbotHQ/clo_hm_attack_indicator')
        target.reparentTo(render)
        target.setPos(x, y, -71.575)
        target.setHpr(h, -90, 0)
        target.setScale(35)
        target.hide()

        targetTrack = Sequence(
            Wait(1.5),
            Func(target.show),
            Parallel(
                LerpScaleInterval(target, 0.3, 40, startScale=35, blendType='easeOut'),
                LerpColorScaleInterval(target, 0.3, (1, 1, 0, 0.3), startColorScale=(1, 1, 0, 1), blendType='easeOut'),
            ),
            Parallel(
                LerpScaleInterval(target, 0.3, 40, startScale=35, blendType='easeOut'),
                LerpColorScaleInterval(target, 0.5, (1, 1, 0, 0.3), startColorScale=(1, 1, 0, 1), blendType='easeOut'),
            ),
            Parallel(
                LerpScaleInterval(target, 0.3, 40, startScale=35, blendType='easeOut'),
                LerpColorScaleInterval(target, 0.5, (1, 1, 0, 0.3), startColorScale=(1, 1, 0, 1), blendType='easeOut'),
            ),
            Parallel(
                LerpScaleInterval(target, 0.3, 40, startScale=35, blendType='easeOut'),
                LerpColorScaleInterval(target, 0.5, (1, 1, 0, 0.3), startColorScale=(1, 1, 0, 1), blendType='easeOut'),
            ),
            Parallel(
                LerpScaleInterval(target, 0.3, 40, startScale=35, blendType='easeOut'),
                LerpColorScaleInterval(target, 0.5, (1, 1, 0, 0.3), startColorScale=(1, 1, 0, 1), blendType='easeOut'),
            ),
            Func(target.detachNode),
        )

        self.bossDamageMovie = Parallel(bossTrack, targetTrack)
        self.bossDamageMovie.start()

    def localSoundHit(self, pieCode, entry):
        if pieCode == ToontownGlobals.PieCodeLawyer:
            if localAvatar.soundModeInUse == ToontownGlobals.SoundMegaphoneNormal:
                self.lawyerGotHit(entry)
            elif localAvatar.soundModeInUse == ToontownGlobals.SoundMegaphoneTaunt:
                self.lawyerGotHit(entry, taunt=1)

    def makeIntroductionMovie(self, delayDeletes):
        # Set up delay deletes, so that we don't have crashes if someone disconnects.
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'HardmodeLawbotBoss.makeIntroductionMovie'))

        # Make Lists of Individual Local DO Movies.
        spotlightAppearanceMovies = []
        for i in range(6):
            spotlightAppearanceMovies.append(self.makeSpotlightAppearanceMovie(i))

        track = Track(
            (0.5, LerpPosHprInterval(base.camera, 0.5, Point3(0, -10, 5.5), Vec3(180, -5, 0), other=self.elevatorModel, blendType='easeInOut')),
            (0.5, LerpFunc(base.camLens.setMinFov, fromData=ToontownGlobals.CJElevatorFov / (4. / 3.), toData=60, blendType='easeInOut')),
            (0.5, Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossIntro0, CFSpeech | CFTimeout)),
            (4.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossIntro1, CFSpeech | CFTimeout)),
            (9.5, Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossIntro2, CFSpeech | CFTimeout)),
            (13.5, Func(self.witnessToon.clearChat)),
            (13.5, Func(self.lawyerToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossIntro3, CFSpeech | CFTimeout)),
            (18.0, Func(self.lawyerToon.clearChat)),
            (18.0, Sequence(Func(self.witnessToon.loop, 'walk'), LerpHprInterval(self.witnessToon, 1.0, Vec3(90,0,0)), Func(self.witnessToon.loop, 'neutral'))),
            (18.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossIntro4, CFSpeech | CFTimeout)),
            (20.0, Sequence(Func(self.lawyerToon.loop, 'walk'), LerpHprInterval(self.lawyerToon, 1.0, Vec3(-90,0,0)), Func(self.lawyerToon.loop, 'neutral'))),
            (22.5, Func(self.witnessToon.clearChat)),
            (22.5, self.makeToonsElevatorExitMovie()),
            (22.5, LerpPosHprInterval(base.camera, 1.5, Point3(0, -60, 20), Vec3(0, -12, 0), other=self.elevatorModel, blendType='easeInOut')),
            (23.0, Sequence(Func(self.witnessToon.loop, 'walk'), Func(self.witnessToon.setPlayRate, -1.0, 'walk'), LerpPosInterval(self.witnessToon, 3.0, Point3(10,20,0)), Func(self.witnessToon.loop, 'neutral'))),
            (23.0, Sequence(Func(self.lawyerToon.loop, 'walk'), Func(self.lawyerToon.setPlayRate, -1.0, 'walk'), LerpPosInterval(self.lawyerToon, 5.5, Point3(-15,20,0)), Func(self.lawyerToon.loop, 'neutral'))),
            (26.5, Func(base.camera.setPosHpr, self.elevatorModel, 8, -27, 3, -60, 0, 0)),
            (26.5, Func(self.lawyerToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossIntro5, CFSpeech | CFTimeout)),
            (27.5, spotlightAppearanceMovies[0]),
            (28.0, self.makeSpotlightDamageMovie(0)),
            (28.0, Func(self.lawyerToon.surpriseEyes)),
            (29.5, LerpHprInterval(base.camera, 1.0, Vec3(-65,20,0), other=self.elevatorModel, blendType='easeInOut')),
            (30.0, Func(self.lawyerToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossIntro6, CFSpeech | CFTimeout)),
            (34.0, Func(self.lawyerToon.clearChat)),
            (34.0, Func(base.camera.setPosHpr, self.elevatorModel, 0, -60, 20, 0, -12, 0)),
            (34.0, Sequence(Func(self.lawyerToon.loop, 'run'), LerpPosInterval(self.lawyerToon, 1.0, Point3(-10,20,0)), Func(self.lawyerToon.loop, 'walk'), LerpHprInterval(self.lawyerToon, 1.0, Vec3(90,0,0)), Func(self.lawyerToon.loop, 'neutral'), Func(self.lawyerToon.blinkEyes))),
            (34.5, spotlightAppearanceMovies[1]),
            (35.0, spotlightAppearanceMovies[2]),
            (35.5, spotlightAppearanceMovies[3]),
            (36.0, spotlightAppearanceMovies[4]),
            (36.5, spotlightAppearanceMovies[5]),
            (38.0, Func(base.camera.setPosHpr, self.elevatorModel, -30, -22.75, 4.5, -90, 5, 0)),
            (38.0, self.makeToonsRotateTowardsVirtualsMovie()),
            (38.0, Sequence(Func(self.witnessToon.loop, 'walk'), LerpHprInterval(self.witnessToon, 1.0, Vec3(-90,0,0)), Func(self.witnessToon.loop, 'neutral'))),
            (38.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossIntro7, CFSpeech | CFTimeout)),
            (40.0, self.loseCogSuits(self.involvedToons, self.elevatorModel, (-30, -22.75, 4.5, -90, 5, 0), arrayOfObjs = False)),
            (41.5, self.makeVirtualsMovementMovie()),
            (42.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossIntro8, CFSpeech | CFTimeout)),
            (43.0, self.makeToonsNeutralMovie()),
            (45.5, Func(base.camera.setPosHpr, self.elevatorModel, -6, -45, 10, -10, -15, 0)),
            (45.5, Sequence(Func(self.witnessToon.loop, 'walk'), LerpHprInterval(self.witnessToon, 0.5, Vec3(0,0,0)), Func(self.witnessToon.loop, 'neutral'))),
            (46.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossIntro9, CFSpeech | CFTimeout)),
            (50.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossIntro10, CFSpeech | CFTimeout)),
            (52.0, Sequence(Func(self.lawyerToon.loop, 'walk'), LerpHprInterval(self.lawyerToon, 0.5, Vec3(0,0,0)), Func(self.lawyerToon.loop, 'neutral'))),
            (53.0, Sequence(Func(self.witnessToon.loop, 'run'), LerpFunc(self.witnessToon.setY, 3.0, fromData=20, toData=50), Func(self.witnessToon.loop, 'neutral'))),
            (53.0, Sequence(Func(self.lawyerToon.loop, 'run'), LerpFunc(self.lawyerToon.setY, 3.0, fromData=20, toData=50), Func(self.lawyerToon.loop, 'neutral'))),
            (54.0, Func(self.witnessToon.clearChat)),
            (54.5, self.makeToonsChaseVirtualsMovie())
            )
        track = Sequence(track)
        if self.battleA:
            track.append(Func(self.showCogRoundSpotlight, 0))
            track.append(Func(base.playSfx, self.spotlightOnSfx))
        if self.battleB:
            track.append(Func(self.showCogRoundSpotlight, 1))
            track.append(Func(base.playSfx, self.spotlightOnSfx))
        track.append(Wait(0.5))
        return Sequence(
            Func(self.stickToonsToFloor),
            track,
            Func(self.unstickToons), name=self.uniqueName('Introduction'))

    def makeVictoryMovie(self):
        fallSeq = Sequence(Func(self.neck.setHpr, Vec3(0, 180, 0)), Parallel(ActorInterval(self, 'Fb_fall', 0, 0, 5.5, 3.0), SoundInterval(self.deathSfx)))
        firstMoveSeq = self.getBossMoveMovie(BossCogGlobals.LawbotBossBattleFallMiddlePos, Vec3(0, 0, 0), 0, 2.5, doAnimate=False)     # don't do self.doAnimate(None) here
        secondMoveSeq = self.getBossMoveMovie(BossCogGlobals.LawbotBossBattleFallFinalPos, Vec3(0, 0, 0), 0, 5.0, doAnimate=False)     # same as above
        secondMoveSeq.setT(2.5)

        trackOne = Track(
            (0.0, Sequence(
                Func(base.camLens.setMinFov, 60),
                Func(base.camera.reparentTo, render),
                Func(base.camera.setPos, 0, 175, -60),
                Func(base.camera.setHpr, 0, 0, 0),
                Func(self.setDizzy, 0),
                Func(self.stopAnimate),
                Func(self.doAnimate, None, happy=1, raised=1),
                Func(self.specialHead.play, 'Ff_trapland'),
                Func(self.clearChat),
            )),
            (0.0, Sequence(Func(self.setPosHpr, *BossCogGlobals.LawbotBossBattleFallPosHpr))),
            (3.0, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossVictory0, CFSpeech)),
            (3.0, Func(self.toonsLineUpVictory)),
            (7.0, Sequence(Func(self.stopAnimate), Func(self.interruptBossDamageMovie), Func(self.loop, 'Ff_neutral'))),
            (7.0, Func(self.clearChat)),
            (7.0, self.makeTrapdoorShakeMovie(intensity=0.2)),
            (9.0, firstMoveSeq),
            (9.0, LerpPosInterval(base.camera, blendType='easeInOut', duration=2.5, pos=(0, 138.25, -60))),
            (11.5, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossVictory1, CFSpeech)),
            (15.0, Func(self.clearChat)),
            (15.0, self.makeTrapdoorShakeMovie(intensity=0.35)),
            (17.0, Func(secondMoveSeq.resume)),
            (17.0, LerpPosInterval(base.camera, blendType='easeInOut', duration=2.5, pos=(0, 101.5, -60))),
            (19.5, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossVictory2, CFSpeech)),
            (19.5, Sequence(ActorInterval(self, 'Ff_cross_arms_into'), Func(self.loop, 'Ff_cross_arms_loop'))),
            (23.0, Func(self.clearChat)),
            (23.0, self.makeTrapdoorShakeMovie(intensity=0.5, reparentCLO=False)),
            (25.5, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossVictory3, CFSpeech)),
            (29.5, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossVictory4, CFSpeech)),
            (33.0, Func(self.clearChat)),
            (33.0, Sequence(Func(self.showLawyerToon), Func(self.lawyerToon.setPosHpr, 10, 110, 0, 15, 0, 0))),
            (33.5, LerpHprInterval(base.camera, 0.5, Vec3(-20,-22,0), blendType='easeOut')),
            (34.0, Func(self.lawyerToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossVictory5, CFSpeech)),
            (35.0, self.makeLaurenButtonMovie()),
            (37.3, Parallel(Func(base.musicMgr.playMusic, self.killMusic, volume = 0.9), Func(self.openTrapDoor))),
            (38.0, Func(self.lawyerToon.clearChat))
        )

        trackTwo = Track(
            (0.0, LerpHprInterval(base.camera, 0.5, Vec3(0,0,0), blendType='easeOut')),
            (1.0, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossVictory6, CFSpeech)),
            (1.0, Sequence(ActorInterval(self, 'Ff_cross_arms_out'), Func(self.loop, 'Ff_neutral'))),
            (4.0, Func(self.clearChat)),
            (4.0, fallSeq),
            (4.5, Func(self.setChatAbsolute, TTLocalizer.LawbotBossVictory4, CFSpeech)),
            (7.0, Func(self.closeTrapDoor)),
            (7.5, Func(self.clearChat)),
            (9.0, Func(self.hide))
        )

        movie = Sequence(trackOne, trackTwo)

        return movie

    def makeEpilogueMovie(self):
        epSpeech = TTLocalizer.WitnessToonCongratulations1
        epSpeech = self.__talkAboutPromotion(epSpeech)
        epSpeech += TTLocalizer.WitnessToonCongratulations2
        bossTrack = Sequence(Func(self.witnessToon.setLocalPageChat, epSpeech, 0))
        return bossTrack

    def __talkAboutPromotion(self, speech):
        deptIndex = CogDisguiseGlobals.dept2deptIndex(self.style.dept)
        newCogSuitLevel = localAvatar.getCogLevels()[deptIndex]
        newCogSuitReviveLevel = localAvatar.getCogReviveLevels()[deptIndex]
        # TODO: Add new strings for hardmode specific stuff.
        # execSuitNames = ToontownGlobals.SuitIndexPerDepartment[deptIndex][SuitDNA.suitsPerDept:]

        if self.prevCogSuitReviveLevel == -1 and newCogSuitReviveLevel > -1:
            speech += TTLocalizer.WitnessToonHardmodeExecutiveSuit

        numSuesEarned = self.numSuesEarned.get(localAvatar.doId)
        if not numSuesEarned:
            numSuesEarned = TTLocalizer.CeaseDesistsNotFoundVal
        speech += TTLocalizer.WitnessToonCeaseDesistReward % numSuesEarned
        speech = self.handleUniteSpeech(speech)

        return speech

    def __makePrepareBattleTwoMovie(self, delayDeletes):
        # Set up delay deletes, so that we don't have crashes if someone disconnects.
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'HardmodeLawbotBoss.makeIntroductionMovie'))

        self.setPosHpr(*BossCogGlobals.LawbotBossBattleTablePosHpr)

        self.makeLitigationTeam()

        trackOne = Track(
            (0.0, Sequence(Func(base.camera.wrtReparentTo, render), Func(base.camera.setPosHpr, self.elevatorModel, 0, -31, 12, 180, -20, 0))),
            (0.0, Func(base.camLens.setMinFov, 60)),
            (0.0, Func(self.toonsLineUpBattleTwo)),
            (0.0, Sequence(Func(self.witnessToon.loop, 'run'), LerpPosInterval(self.witnessToon, 3.0, Vec3(6,50,0)))),
            (0.0, Sequence(Func(self.lawyerToon.loop, 'run'), LerpPosInterval(self.lawyerToon, 3.0, Vec3(-6,50,0)))),
            (0.5, Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareTwo0, CFSpeech | CFTimeout)),
            (3.0, Sequence(Func(self.witnessToon.loop, 'walk'), LerpHprInterval(self.witnessToon, 1.0, Vec3(160,0,0)), Func(self.witnessToon.loop, 'neutral'))),
            (3.0, Sequence(Func(self.lawyerToon.loop, 'walk'), LerpHprInterval(self.lawyerToon, 1.0, Vec3(-160,0,0)), Func(self.lawyerToon.loop, 'neutral'))),
            (4.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareTwo1, CFSpeech | CFTimeout)),
            (8.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareTwo2, CFSpeech | CFTimeout)),
            (12.0, Func(self.witnessToon.clearChat)),
            (12.0, Func(base.camera.setPosHpr, self.elevatorModel, 0, -150, 8, 0, 0, 0)),
            (12.0, Func(self.openEntryDoors)),
            (12.0, self.makeToonsEnterRoomMovie()),
            (16.0, Func(self.closeEntryDoors)),
            (18.5, Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareTwo3, CFSpeech | CFTimeout)),
            (22.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareTwo4, CFSpeech | CFTimeout)),
            (26.0, Func(self.witnessToon.clearChat)),
            (26.0, Func(self.lawyerToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareTwo5, CFSpeech | CFTimeout)),
            (29.0, Func(self.lawyerToon.clearChat)),
            (29.0, Func(base.camera.setPosHpr, self.elevatorModel, 0, -265, 18, 180, 7, 0)),
            (29.0, Func(self.loop, 'Ff_cross_arms_loop')),
            (29.0, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareTwo6, CFSpeech | CFTimeout)),
            (33.0, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareTwo7, CFSpeech | CFTimeout)),
            (37.0, LerpPosInterval(base.camera, 2.0, pos=Vec3(0,-202,22), other=self.elevatorModel, blendType='easeInOut')),
            (37.0, LerpFunc(base.camera.setP, 3.0, fromData=7, toData=-20, blendType='easeInOut')),
            (37.5, Sequence(ActorInterval(self, 'Ff_cross_arms_out'), Func(self.loop, 'Ff_neutral'))),
            (37.5, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareTwo8, CFSpeech | CFTimeout)),
            (42.0, Func(self.clearChat)),
            (42.0, self.makeLitigationDialogueMovie())
        )

        trackTwo = Track(
            (0.0, Func(base.camera.setPosHpr, self.elevatorModel, 0, -265, 18, 180, 7, 0)),
            (0.0, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareTwo9, CFSpeech | CFTimeout)),
            (4.0, Func(self.loop, 'Ff_speech')),
            (4.0, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareTwo10, CFSpeech | CFTimeout)),
            (8.0, Func(self.clearChat)),
            (8.0, Func(self.loop, 'Ff_neutral'))
        )

        movie = Sequence(trackOne, trackTwo)

        return movie

    def __makePrepareBattleThreeMovie(self):
        lerpGavelScales = Parallel()
        for g in list(self.gavels.values()):
            lerpGavelScales.append(LerpScaleInterval(g.nodePath, 2, g.scale))

        slamGavels = Parallel()
        for g in list(self.gavels.values()):
            slamGavels.append(g.doSingleSlam())

        def freakoutCamSeq():
            seq = Sequence(
                LerpPosInterval(base.camera, .1, Vec3(base.camera.getX(), base.camera.getY(), base.camera.getZ() + 1)),
                LerpPosInterval(base.camera, .1, Vec3(base.camera.getX(), base.camera.getY(), base.camera.getZ() - 2)),
                LerpPosInterval(base.camera, .1, Vec3(base.camera.getX(), base.camera.getY(), base.camera.getZ() - 1)),
            )
            seq.start()

        def hideFurniture():
            podiums = self.geom.find('**/g_cogpodiums')
            table = self.geom.find('**/g_meetingtable')
            seq = Sequence(
                Parallel(
                    LerpScaleInterval(podiums, 2, Point3(1, 1, 0.1), blendType="easeIn"),
                    LerpScaleInterval(table, 2, Point3(1, 1, 0.1), blendType="easeIn"),
                ),
                Func(self.stashFurniture)
            )
            seq.start()

        tableGavelsSlam = self.makeGavelSlamMovie()
        showCannonsAppearing = self.showCannonsAppearing()
        movie = Track(
            (0.0, Func(base.camLens.setMinFov, 60)),
            (0.0, Func(self.evidenceBox.hide)),
            (0.0, Func(self.witnessToon.loop, 'neutral')),
            (0.0, Parallel(Sequence(ActorInterval(self, 'Ff_cross_arms_into'), Func(self.loop, 'Ff_cross_arms_loop')), Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareThree0, CFSpeech))),
            (4.0, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareThree1, CFSpeech)),
            (8.0, Parallel(Sequence(ActorInterval(self, 'Ff_cross_arms_out'), Func(self.loop, 'Ff_neutral')), Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareThree2, CFSpeech))),
            (12.0, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareThree3, CFSpeech)),
            (13.5, lerpGavelScales),
            (15.0, Parallel(LerpPosHprInterval(base.camera, 0.5, Vec3(0, -195, 35), Vec3(180, -20, 0), Vec3(0, -265, 18), Vec3(180, 7, 0), blendType='easeOut', other=self.elevatorModel), Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareThree4, CFSpeech))),
            (15.6, slamGavels),
            (15.7, tableGavelsSlam),
            (16.2, Func(freakoutCamSeq)),
            (19.0, LerpPosHprInterval(base.camera, 0.5, Vec3(0, -105, 5), Vec3(0, 0, 0), blendType='easeOut', other=self.elevatorModel)),
            (19.0, Func(self.evidenceBox.pose, 'open', 0.1)),
            (19.5, Func(self.clearChat)),
            (20.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareThree5, CFSpeech | CFTimeout)),
            (24.0, Func(self.witnessToon.clearChat)),
            (24.0, Func(self.lawyerToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareThree6, CFSpeech | CFTimeout)),
            (24.0, Sequence(Func(self.witnessToon.loop, 'walk'),
                            LerpHprInterval(self.witnessToon, duration=1.0, hpr=(160, 0, 0)),
                            Func(self.witnessToon.loop, 'neutral'), Func(self.evidenceBox.show),
                            self.makeEvidenceBoxAppearTrack(), Func(self.evidenceBox.loop, 'idle'),
                            Func(self.witnessToon.loop, 'walk'),
                            LerpHprInterval(self.witnessToon, duration=1.0, hpr=(20, 0, 0)),
                            Func(self.witnessToon.loop, 'neutral'))),
            (28.0, Func(self.lawyerToon.clearChat)),
            (28.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareThree7, CFSpeech | CFTimeout)),
            (32.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareThree8, CFSpeech | CFTimeout)),
            (32.0, Func(hideFurniture)),
            (36.0, Parallel(Func(self.witnessToon.clearChat), showCannonsAppearing)),
            (37.0, Wait(1))
            )
        return movie

    def __makePrepareBattleFourMovie(self):
        trackOne = Track(
            (0.0, Func(base.camLens.setMinFov, 60)),
            (0.0, Func(base.camera.setPosHpr, self.elevatorModel, 0, -179, 18, 180, 7, 0)),
            (0.0, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareFour0, CFSpeech)),
            (0.5, Func(self.toonsLineUpBattleFour)),
            (3.0, Func(self.clearChat)),
            (3.0, LerpPosHprInterval(base.camera, 0.5, Vec3(0, -105, 5), Vec3(15, 0, 0), blendType='easeOut', other=self.elevatorModel)),
            (3.5, Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareFour1, CFSpeech)),
            (6.5, Func(self.witnessToon.clearChat)),
            (6.5, LerpPosHprInterval(base.camera, 0.5, Vec3(0, -179, 18), Vec3(180, 7, 0), blendType='easeOut', other=self.elevatorModel)),
            (7.0, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareFour2, CFSpeech | CFTimeout)),
            (10.0, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareFour3, CFSpeech | CFTimeout)),
            (10.0, Sequence(ActorInterval(self, 'Ff_cross_arms_into'), Func(self.loop, 'Ff_cross_arms_loop'))),
            (13.5, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareFour4, CFSpeech | CFTimeout)),
            (17.0, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareFour5, CFSpeech | CFTimeout)),
            (21.0, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareFour6, CFSpeech | CFTimeout)),
            (25.5, Func(self.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareFour7, CFSpeech | CFTimeout)),
            (30.0, Func(self.clearChat))
        )

        trackTwo = Track(
            (0.0, LerpPosHprInterval(base.camera, 0.5, Vec3(0, -105, 5), Vec3(0, 0, 0), blendType='easeOut', other=self.elevatorModel)),
            (0.0, Func(self.lawyerToon.sadEyes)),
            (1.0, Func(self.lawyerToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareFour8, CFSpeech | CFTimeout)),
            (4.5, Func(self.lawyerToon.clearChat)),
            (4.5, Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareFour9, CFSpeech | CFTimeout)),
            (8.5, Parallel(Func(self.lawyerToon.normalEyes), Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareFour10, CFSpeech | CFTimeout))),
            (13.0, Sequence(Func(self.witnessToon.setChatAbsolute, TTLocalizer.HardmodeLawbotBossPrepareFour11, CFSpeech | CFTimeout), Func(self.loop, 'Ff_neutral'))),
            (17.0, Func(self.witnessToon.clearChat))
        )

        movie = Sequence(trackOne, trackTwo)

        return movie

    def setAttackCode(self, attackCode, avId = 0):
        self.attackCode = attackCode
        self.attackAvId = avId
        if attackCode == BossCogGlobals.BossCogDizzyNow:
            self.setDizzy(1)
            self.cleanupAttacks()
            self.specialHead.play('hit')
            self.doAnimate('hit', happy=1, now=1)
        elif attackCode == BossCogGlobals.BossCogSwatLeft:
            self.setDizzy(0)
            self.doAnimate('ltSwing', happy=1, now=1)
        elif attackCode == BossCogGlobals.BossCogSwatRight:
            self.setDizzy(0)
            self.doAnimate('rtSwing', happy=1, now=1)
        elif attackCode == BossCogGlobals.BossCogAreaAttack:
            self.setDizzy(0)
            base.playSfx(self.warningSfx)
            self.doAnimate('areaAttack', happy=1, now=1)
        elif attackCode == BossCogGlobals.BossCogFrontAttack:
            self.setDizzy(0)
            self.doAnimate('frontAttackPaper', happy=1, now=1)
        elif attackCode == BossCogGlobals.BossCogRecoverDizzyAttack:
            self.setDizzy(0)
            self.specialHead.play('Ff_trapland')
            self.doAnimate('frontAttackPaper', happy=1, now=1)
        elif attackCode == BossCogGlobals.BossCogSpreadBookDirectedAttack:
            self.setDizzy(0)
            self.doDirectedAttack(avId, attackCode)
        elif attackCode == BossCogGlobals.BossCogFourWayTornadoAreaAttack:
            self.setDizzy(0)
            base.playSfx(self.warningSfx)
            base.localAvatar.doBossTornadoIndicator()
            self.doTornadoAreaAttack()
        elif attackCode == BossCogGlobals.BossCogEightWayTornadoAreaAttack:
            self.setDizzy(0)
            base.playSfx(self.warningSfx)
            base.localAvatar.doBossTornadoIndicator()
            self.doEightWayTornadoAreaAttack()
        elif attackCode == BossCogGlobals.BossCogSpiralTornadoAreaAttack:
            self.setDizzy(0)
            base.playSfx(self.warningSfx)
            base.localAvatar.doBossTornadoIndicator()
            self.doSpiralTornadoAreaAttack()
        elif attackCode == BossCogGlobals.BossCogNoAttack:
            self.setDizzy(0)
            self.doAnimate(None, raised=1)

    def doEightWayTornadoAreaAttack(self):
        tornadoTime = 4.0
        tornado = self.getTornado()
        tornadoList = []
        indicatorList = []
        arrowGui = loader.loadModel('phase_11/models/lawbotHQ/clo_indicators')
        indicator = arrowGui.find('**/arrow_straight')
        indicator.setScale(16)
        indicator.setBin('shadow', -1)
        indicator.setDepthWrite(False)
        arrowGui.removeNode()
        indicatorPosHprs = ((0, -24, 0.035, 180, -90, 0),
                            (0, 24, 0.035, 0, -90, 0),
                            (-24, 0, 0.035, 90, -90, 0),
                            (24, 0, 0.035, -90, -90, 0),
                            (16, 16, 0.035, -45, -90, 0),
                            (-16, 16, 0.035, 45, -90, 0),
                            (16, -16, 0.035, -135, -90, 0),
                            (-16, -16, 0.035, 135, -90, 0))
        for i in range(len(list(BossCogGlobals.LawbotBossEightWayTornadoIndex2PosTravel.keys()))):
            newTornado = tornado.copyTo(self)
            tornadoList.append(newTornado)
            newIndicator = indicator.copyTo(self.geom)
            newIndicator.setColorScale(1, 1, 1, 0)
            newIndicator.setPosHpr(self, *indicatorPosHprs[i])
            indicatorList.append(newIndicator)
        tornado.removeNode()
        throwAnim = Parallel(Sequence(Func(base.localAvatar.doBossTornadoIndicator), ActorInterval(self, 'Bb2Ff_spin'), ActorInterval(self, 'Ff_neutral')), SoundInterval(self.spinSfx, node=self))
        tornadoSfx = loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cfg_whirlwind.ogg')

        def removeTornadoes(tornadoList):
            for tornado in tornadoList:
                tornado.removeNode()
            tornadoSound.finish()
            tornadoSpin.finish()
            del tornadoList

        def removeIndicators(indicatorList):
            for indicator in indicatorList:
                indicator.removeNode()
            del indicatorList

        def getTornadoFinalPosNodes(posList):
            nodeList = []
            for i in range(len(list(posList.keys()))):
                tornadoPosNode = self.attachNewNode('tornadoPosNode%s' % i)
                tornadoPosNode.setPos(posList[i])
                tornadoPosNode.wrtReparentTo(self.geom)
                nodeList.append(tornadoPosNode)
            return nodeList

        tornadoNodeList = getTornadoFinalPosNodes(BossCogGlobals.LawbotBossEightWayTornadoIndex2PosTravel)
        tornadoMove = Parallel()
        tornadoSpin = Parallel()
        tornadoSound = SoundInterval(tornadoSfx, node=base.localAvatar, seamlessLoop=1, listenerNode=base.localAvatar)
        indicatorSeq = Parallel()

        for i in range(len(indicatorList)):
            indicatorSeq.append(
                Sequence(
                    LerpColorScaleInterval(indicatorList[i], 0.25, (1, 1, 1, 1), blendType='easeIn'),
                    Wait(1.0),
                    LerpColorScaleInterval(indicatorList[i], 0.25, (1, 1, 1, 0), blendType='easeOut')
                )
            )

        for i in range(len(tornadoList)):
            mult = random.choice([1, -1])
            tornadoMove.append(
                Sequence(
                    Wait(1.3),
                    Func(tornadoList[i].show),
                    Func(tornadoList[i].wrtReparentTo, self.geom),
                    Parallel(
                        LerpScaleInterval(tornadoList[i], 1.0, startScale=0.05, scale=1.0),
                        LerpColorScaleInterval(tornadoList[i], 1.0, (1, 1, 1, 0.60)),
                        LerpPosInterval(tornadoList[i].getChild(0), duration=tornadoTime, pos=BossCogGlobals.LawbotBossTornadoWobble, blendType='easeIn'),
                        LerpPosInterval(tornadoList[i], pos=tornadoNodeList[i].getPos(), duration=tornadoTime)
                    ),
                    Parallel(
                        LerpScaleInterval(tornadoList[i], scale=0.05, duration=1.0),
                        LerpColorScaleInterval(tornadoList[i], 1.0, (1, 1, 1, 0.0))
                    )
                )
            )
            tornadoSpin.append(
                Parallel(
                    LerpHprInterval(tornadoList[i], 1.0, (0, 0, 0), (mult*360, 0, 0)), LerpHprInterval(tornadoList[i].getChild(0), 1.0, (0, 0, 0), (mult*360, 0, 0)))
            )

        def removeFinalPosNodes(nodeList):
            for node in nodeList:
                node.removeNode()
            del nodeList

        def startTornadoSeq():
            tornadoSeq = Parallel(
                Sequence(tornadoMove,
                         Func(removeTornadoes, tornadoList),
                         Func(removeFinalPosNodes, tornadoNodeList)),
                Sequence(indicatorSeq,
                         Func(removeIndicators, indicatorList)),
                Func(tornadoSpin.loop),
                Func(tornadoSound.loop))
            tornadoSeq.start()

        seq = Sequence(Func(startTornadoSeq), Wait(1), throwAnim)
        self.doAnimate(seq, raised=1, now=1)

    def doSpiralTornadoAreaAttack(self):
        tornadoTime = 4.0
        tornado = self.getTornado()
        tornadoList = []
        indicatorList = []
        arrowGui = loader.loadModel('phase_11/models/lawbotHQ/clo_indicators')
        indicator = arrowGui.find('**/arrow_curved')
        indicator.setScale(15, 16, 30)
        indicator.setBin('shadow', -1)
        indicator.setDepthWrite(False)
        arrowGui.removeNode()
        for i in range(len(list(BossCogGlobals.LawbotBossSpiralTornadoIndex2PosTravel.keys()))):
            newTornado = tornado.copyTo(self)
            tornadoList.append(newTornado)
        for i in range(3):
            indicatorNode = self.attachNewNode(f'inNode{i}')
            indicatorNode.setZ(0.035)
            indicatorNode.setHpr(((120 * (i+1)) - 30), -90, 0)
            indicatorNode.wrtReparentTo(self.geom)
            indicatorNode.setColorScale(1, 1, 1, 0)
            newIndicator = indicator.copyTo(indicatorNode)
            newIndicator.setPos(indicatorNode, -16, 0, 0)
            indicatorList.append(indicatorNode)
        tornado.removeNode()
        throwAnim = Parallel(Sequence(Func(base.localAvatar.doBossTornadoIndicator), ActorInterval(self, 'Bb2Ff_spin'), ActorInterval(self, 'Ff_neutral')), SoundInterval(self.spinSfx, node=self))
        tornadoSfx = loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cfg_whirlwind.ogg')

        def removeTornadoes(tornadoList):
            for tornado in tornadoList:
                tornado.removeNode()
            tornadoSound.finish()
            tornadoSpin.finish()
            tornadoRotateNode.removeNode()
            del tornadoList

        def removeIndicators(indicatorList):
            for indicator in indicatorList:
                indicator.removeNode()
            del indicatorList

        def getTornadoFinalPosNodes(posList, parentNode):
            nodeList = []
            for i in range(len(list(posList.keys()))):
                tornadoPosNode = self.attachNewNode('tornadoPosNode%s' % i)
                tornadoPosNode.setPos(posList[i])
                tornadoPosNode.wrtReparentTo(parentNode)
                nodeList.append(tornadoPosNode)
            return nodeList

        tornadoRotateNode = self.attachNewNode('tornadoRotateNode')
        tornadoRotateNode.setPos(0, 0, 0)
        tornadoRotateNode.wrtReparentTo(self.geom)

        tornadoNodeList = getTornadoFinalPosNodes(BossCogGlobals.LawbotBossSpiralTornadoIndex2PosTravel, tornadoRotateNode)
        tornadoMove = Parallel()
        tornadoSpin = Parallel(LerpHprInterval(tornadoRotateNode, 3.0, (0, 0, 0), (360, 0, 0)))
        tornadoSound = SoundInterval(tornadoSfx, node=base.localAvatar, seamlessLoop=1, listenerNode=base.localAvatar)
        indicatorSeq = Parallel()

        for i in range(len(indicatorList)):
            indicatorSeq.append(
                Sequence(
                    LerpColorScaleInterval(indicatorList[i], 0.25, (1, 1, 1, 1), blendType='easeIn'),
                    Wait(1.0),
                    LerpColorScaleInterval(indicatorList[i], 0.25, (1, 1, 1, 0), blendType='easeOut')
                )
            )

        for i in range(len(tornadoList)):
            tornadoMove.append(
                Sequence(
                    Wait(1.3),
                    Func(tornadoList[i].show),
                    Func(tornadoList[i].wrtReparentTo, tornadoRotateNode),
                    Parallel(
                        LerpScaleInterval(tornadoList[i], 1.0, startScale=0.05, scale=1.0),
                        LerpColorScaleInterval(tornadoList[i], 1.0, (1, 1, 1, 0.60)),
                        LerpPosInterval(tornadoList[i], pos=tornadoNodeList[i].getPos(), duration=tornadoTime)
                    ),
                    Parallel(
                        LerpScaleInterval(tornadoList[i], scale=0.05, duration=1.0),
                        LerpColorScaleInterval(tornadoList[i], 1.0, (1, 1, 1, 0.0))
                    )
                )
            )
            tornadoSpin.append(LerpHprInterval(tornadoList[i].getChild(0), 1.0, (0, 0, 0), (-360, 0, 0)))

        def removeFinalPosNodes(nodeList):
            for node in nodeList:
                node.removeNode()
            del nodeList

        def startTornadoSeq():
            tornadoSeq = Parallel(
                Sequence(tornadoMove,
                         Func(removeTornadoes, tornadoList),
                         Func(removeFinalPosNodes, tornadoNodeList)),
                Sequence(indicatorSeq,
                         Func(removeIndicators, indicatorList)),
                Func(tornadoSpin.loop),
                Func(tornadoSound.loop))
            tornadoSeq.start()

        seq = Sequence(Func(startTornadoSeq), Wait(1), throwAnim)
        self.doAnimate(seq, raised=1, now=1)

    def announceForcedAreaAttack(self):
        if not getattr(localAvatar.controlManager.currentControls, 'isAirborne', 0):
            self.zapLocalToon(BossCogGlobals.BossCogAreaAttack, origin=None, force=1)

    def zapLocalToon(self, attackCode, origin=None, force=0):
        if self.localToonIsSafe or localAvatar.ghostMode or localAvatar.isStunned:
            return
        if (self.attackCode in BossCogGlobals.BossCogDizzyStates) and (attackCode not in BossCogGlobals.NonBossCogAttacks) and not force:
            return
        messenger.send('interrupt-pie')
        messenger.send('interrupt-sound')
        place = self.cr.playGame.getPlace()
        currentState = None
        if place:
            currentState = place.getCurrentOrNextState()
        if (self.style.dept != 'l' and currentState == 'Stopped') and currentState not in ('Walk', 'FinalBattle', 'Crane'):
            return
        toon = localAvatar
        fling = 1
        shake = 0
        if attackCode == BossCogGlobals.BossCogAreaAttack:
            fling = 0
            shake = 1
        if fling:
            if origin is None:
                origin = self
            camera.wrtReparentTo(render)
            toon.headsUp(origin)
            camera.wrtReparentTo(toon)
        bossRelativePos = toon.getPos(self.getGeomNode())
        bp2d = Vec2(bossRelativePos[0], bossRelativePos[1])
        bp2d.normalize()
        pos = toon.getPos()
        hpr = toon.getHpr()
        timestamp = globalClockDelta.getFrameNetworkTime()
        if globalClock.getFrameTime() < self.lastZapLocalTime + self.attackThreshold:
            return
        else:
            self.lastZapLocalTime = globalClock.getFrameTime()
        if not localAvatar.isStunned:
            self.sendUpdate('zapToon', [pos[0],
             pos[1],
             pos[2],
             hpr[0] % 360.0,
             hpr[1],
             hpr[2],
             bp2d[0],
             bp2d[1],
             attackCode,
             timestamp])
            self.doZapToon(toon, fling=fling, shake=shake)

    '''
    Local object functions

    All of the functions below are used to initialize or manipulate local objects in the fight.

    These objects are not networked, so they should not be treated as such.
    '''

    def makeWitnessToon(self):
        self.witnessToon = NPCToons.createLocalNPC(2009)
        self.witnessToon.initializeBodyCollisions('toon')
        self.witnessToon.addActive()
        self.witnessToon.setName(TTLocalizer.WitnessToonName)
        self.witnessToon.setDisplayName(TTLocalizer.WitnessToonName)
        self.witnessToon.setPickable(0)
        self.witnessToon.setPlayerType(NametagGroup.CCNonPlayer)
        self.witnessToon.setPosHpr(*BossCogGlobals.HardmodeLawbotBossWitnessToonPosHpr)

    def makeLawyerToon(self):
        self.lawyerToon = NPCToons.createLocalNPC(12050)
        self.lawyerToon.initializeBodyCollisions('toon')
        self.lawyerToon.addActive()
        self.lawyerToon.setName(TTLocalizer.LawyerToonName)
        self.lawyerToon.setDisplayName(TTLocalizer.LawyerToonName)
        self.lawyerToon.setPickable(0)
        self.lawyerToon.setPlayerType(NametagGroup.CCNonPlayer)
        self.lawyerToon.setPosHpr(*BossCogGlobals.HardmodeLawbotBossLawyerToonPosHpr)

    def makeCogRoundSpotlights(self):
        for i in range(2):
            spotlight = DistributedLawbotBossSecurityCamera.DistributedLawbotBossSecurityCamera(base.cr, silent=True)
            spotlight.doId = self.nextLocalDoId
            self.nextLocalDoId -= 1
            spotlight.isCogRound = 1
            spotlight.generate()
            spotlight.announceGenerate()
            spotlight.setPos(BossCogGlobals.HardmodeLawyerVirtualBattleCameraPos[i][0])
            spotlight.setH(90)
            spotlight.setWideX(1.2)
            spotlight.setWideY(0.65)
            spotlight.setProjector((0, 0, 70))
            self.cogRoundSpotlights[i] = spotlight
        self.hideCogRoundSpotlights()
        self.updateCogRoundSpotlightPos(0, BossCogGlobals.HardmodeLawyerVirtualBattleSpotlightPos[0])
        self.updateCogRoundSpotlightPos(1, BossCogGlobals.HardmodeLawyerVirtualBattleSpotlightPos[1])

    def makeIntroductionSpotlights(self):
        for i in range(6):
            spotlight = DistributedLawbotBossSecurityCamera.DistributedLawbotBossSecurityCamera(base.cr)
            spotlight.doId = self.nextLocalDoId
            self.nextLocalDoId -= 1
            spotlight.isCogRound = 1
            spotlight.generate()
            spotlight.announceGenerate()
            spotlight.setPos(BossCogGlobals.HardmodeIntroductionSpotlightPos[i])
            spotlight.setWideX(0.4)
            spotlight.setWideY(0.4)
            self.introductionSpotlights[i] = spotlight
        self.hideIntroductionSpotlights()

    def hideIntroductionSpotlights(self):
        for spotlight in self.introductionSpotlights:
            spotlight.hide()

    def cleanupIntroductionSpotlights(self):
        for spotlight in self.introductionSpotlights:
            if not spotlight:
                return
            spotlight.disable()
            spotlight.delete()
            spotlight = None
        self.introductionSpotlights = []

    def makeIntroductionVirtuals(self):
        for i in range(6):
            virtual = ClashLawbotBossSuit.ClashLawbotBossSuit(base.cr)
            dna = SuitDNA.SuitDNA()
            dna.newSuitRandom(7, 'l', wantAlts=0)
            virtual.setDNA(dna)
            virtual.dna = dna
            virtual.doId = self.nextLocalDoId
            self.nextLocalDoId -= 1
            virtual.setVirtual(1)
            virtual.isForCutscene = 1
            virtual.generate()
            virtual.announceGenerate()
            virtual.reparentTo(render)
            virtual.setPos(BossCogGlobals.HardmodeIntroductionVirtualPos[i][0])
            virtual.setH(BossCogGlobals.HardmodeIntroductionVirtualPos[i][1])
            self.introductionVirtuals[i] = virtual

    def cleanupIntroductionVirtuals(self):
        for virtual in self.introductionVirtuals:
            if not virtual:
                return
            virtual.disable()
            virtual.delete()
            virtual = None
        self.introductionVirtuals = []

    # Creates client-sided Litigation Team for PrepareBattleTwo cutscene.
    def makeLitigationTeam(self):
        if len(self.litigationTeam) > 0:  # Litigation Team is already made
            return
        for i in range(4):
            suit = Suit.Suit()
            dna = SuitDNA.SuitDNA()
            dna.newSuit(self.litigationOrder[i])
            suit.setDNA(dna)
            suit.addActive()
            suit.makeExecutive()
            suit.reparentTo(render)
            suit.loop('sit')
            suit.setPosHpr(*BossCogGlobals.HardmodeLawbotBossLitigationPositions[i])
            if self.litigationOrder[i] == 'sgoat':
                suit.setZ(suit.getZ() + BossCogGlobals.HardmodeLawbotBossScapegoatZOffset)
            suit.setPickable(0)
            suit.setDisplayName(TTLocalizer.SuitBaseNameWithLevel % {'name': suit.getName(), 'dept': TTLocalizer.Lawbot, 'level': str(
                BossCogGlobals.HardmodeLawbotBossLitigationLevels[self.litigationOrder[i]]) + TTLocalizer.AvatarSuitPanelManager})
            suit.hideNametag2d()
            # Adjust nametag position because sitting animation is dumb
            suit.nametag3d.setPos(suit.nametag3d.getX() + -0.2, suit.nametag3d.getY() - 2, suit.nametag3d.getZ() - 1.5)
            self.litigationTeam.append(suit)

    def cleanupLitigationTeam(self):
        if len(self.litigationTeam) == 0:  # Litigation Team is already cleaned up
            return
        for suit in self.litigationTeam:
            suit.delete()
        self.litigationTeam = []

    @property
    def uniteResistanceToon(self):
        return self.witnessToon

    '''
    Cutscene Functions

    These functions are entirely used for creating parts of cutscenes.
    '''

    # Makes Spotlight and Virtual at the given index appear and does all the nice timing and stuff.
    def makeSpotlightAppearanceMovie(self, index):
        spotlight = self.introductionSpotlights[index]
        virtual = self.introductionVirtuals[index]
        if index != 0:
            track = Track(
                (0.0, Func(spotlight.show)),
                (0.0, SoundInterval(spotlight.onSound, node=spotlight, volume=0.8)),
                (0.5, LerpColorScaleInterval(virtual, 1, Vec4(1,1,1,1)))
            )
        else:
            track = Track(
                (0.0, Func(spotlight.show)),
                (0.5, LerpColorScaleInterval(virtual, 1, Vec4(1,1,1,1)))
            )
        return track

    # Simulates a spotlight being tripped
    def makeSpotlightDamageMovie(self, index):
        spotlight = self.introductionSpotlights[index]
        track = Track(
            (0.0, Func(self.toggleSpotlightColor, index)),
            (0.0, spotlight.attackTrack),
            (2.0, Func(self.toggleSpotlightColor, index))
        )
        return track

    # Toggles between white and red
    def toggleSpotlightColor(self, index):
        spotlight = self.introductionSpotlights[index]
        if spotlight.canDamage == 1:
            spotlight.canDamage = 0
        else:
            spotlight.canDamage = 1

    # Moves Virtuals and their spotlights off screen.
    def makeVirtualsMovementMovie(self):
        track = Parallel()
        for i in range(6):
            spotlight = self.introductionSpotlights[i]
            virtual = self.introductionVirtuals[i]
            # If H is negative, we know they are on the right side and vice versa.
            if virtual.getH() < 0:
                trackPart = Track(
                    (0.0, LerpFunc(virtual.setH, 1.0, fromData=-90, toData=90)),
                    (1.0, LerpFunc(virtual.setX, 5.0, fromData=-18, toData=-55)),
                    (1.0, LerpFunc(spotlight.setX, 5.0, fromData=-18, toData=-55))
                )
            else:
                trackPart = Track(
                    (0.0, LerpFunc(virtual.setH, 1.0, fromData=90, toData=-90)),
                    (1.0, LerpFunc(virtual.setX, 5.0, fromData=18, toData=55)),
                    (1.0, LerpFunc(spotlight.setX, 5.0, fromData=18, toData=55))
                )
            track.append(trackPart)
        return track

    # Toons walk out from elevator into the hallway
    def makeToonsElevatorExitMovie(self):
        track = Parallel()
        i = 0
        for toonId in self.toonsA:
            toon = base.cr.doId2do.get(toonId)
            if toon and toon.isDisguised:
                trackPart = Sequence(
                    Func(toon.wrtReparentTo, render),
                    Wait(1.0 * i),
                    Func(toon.headsUp, BossCogGlobals.HardmodeIntroductionToonsAPath[0]),
                    Func(toon.suit.loop, 'walk'),
                    LerpPosInterval(toon, 1.0, BossCogGlobals.HardmodeIntroductionToonsAPath[0]),
                    Func(toon.headsUp, BossCogGlobals.HardmodeIntroductionToonsAPath[3])
                )
                for j in range(3 - i):
                    trackPart.append(LerpPosInterval(toon, 1.0, BossCogGlobals.HardmodeIntroductionToonsAPath[j + 1]))
                trackPart.append(Func(toon.suit.loop, 'neutral'))
                track.append(trackPart)
                i += 1
        i = 0
        for toonId in self.toonsB:
            toon = base.cr.doId2do.get(toonId)
            if toon and toon.isDisguised:
                trackPart = Sequence(
                    Func(toon.wrtReparentTo, render),
                    Wait(1.0 * i),
                    Func(toon.headsUp, BossCogGlobals.HardmodeIntroductionToonsBPath[0]),
                    Func(toon.suit.loop, 'walk'),
                    LerpPosInterval(toon, 1.0, BossCogGlobals.HardmodeIntroductionToonsBPath[0]),
                    Func(toon.headsUp, BossCogGlobals.HardmodeIntroductionToonsBPath[3])
                )
                for j in range(3 - i):
                    trackPart.append(LerpPosInterval(toon, 1.0, BossCogGlobals.HardmodeIntroductionToonsBPath[j + 1]))
                trackPart.append(Func(toon.suit.loop, 'neutral'))
                track.append(trackPart)
                i += 1
        return track

    def makeToonsRotateTowardsVirtualsMovie(self):
        track = Parallel()
        for toonId in self.involvedToons:
            toon = base.cr.doId2do.get(toonId)
            if toon and toon.isDisguised:
                if toonId in self.toonsA:
                    track.append(Sequence(
                        Func(toon.suit.loop, 'walk'),
                        LerpHprInterval(toon, 1.0, Vec3(-90, 0, 0)),
                        Func(toon.suit.loop, 'neutral')
                    ))
                else:
                    track.append(Sequence(
                        Func(toon.suit.loop, 'walk'),
                        LerpHprInterval(toon, 1.0, Vec3(90, 0, 0)),
                        Func(toon.suit.loop, 'neutral')
                    ))
        return track

    def makeToonsChaseVirtualsMovie(self):
        track = Parallel()
        for toonId in self.involvedToons:
            toon = base.cr.doId2do.get(toonId)
            if toon:
                if toonId in self.toonsA:
                    track.append(Sequence(
                        Func(toon.loop, 'run'),
                        LerpFunc(toon.setX, 2.5, fromData=4, toData=40),
                        Func(toon.loop, 'neutral')
                    ))
                else:
                    track.append(Sequence(
                        Func(toon.loop, 'run'),
                        LerpFunc(toon.setX, 2.5, fromData=-4, toData=-40),
                        Func(toon.loop, 'neutral')
                    ))
        return track

    def makeToonsNeutralMovie(self):
        track = Parallel()
        for toonId in self.involvedToons:
            toon = base.cr.doId2do.get(toonId)
            if toon:
                track.append(Func(toon.loop, 'neutral'))
        return track

    # Moves both the NPC and Player Toons into the main room.
    def makeToonsEnterRoomMovie(self):
        """Duration: 7.0"""
        track = Parallel()
        # Add NPCs to track
        track.append(Sequence(
            Func(self.witnessToon.setPosHpr, 6, 50, 0, 0, 0, 0),
            Wait(1.5),
            Func(self.witnessToon.loop, 'run'),
            LerpPosInterval(self.witnessToon, 5.0, pos=(6, 127, 0)),
            Func(self.witnessToon.loop, 'neutral')
        ))
        track.append(Sequence(
            Func(self.lawyerToon.setPosHpr, -6, 50, 0, 0, 0, 0),
            Wait(1.5),
            Func(self.lawyerToon.loop, 'run'),
            LerpPosInterval(self.lawyerToon, 5.0, pos=(-6, 127, 0)),
            Func(self.lawyerToon.loop, 'neutral')
        ))
        # Add all players to track
        for toonId in self.involvedToons:
            toon = base.cr.doId2do.get(toonId)
            if toon:
                # If we have two battles, split the toons up. otherwise, line them up.
                if len(self.toonsB) > 0:
                    if toonId in self.toonsA:
                        toonIndex = self.toonsA.index(toonId)
                        # X Position is -3 for index 0 and 2, -9 for index 1 and 3.
                        if toonIndex % 2 == 0:
                            toonX = -3
                        else:
                            toonX = -9
                    else:
                        toonIndex = self.toonsB.index(toonId)
                        # X Position is 3 for index 0 and 2, 9 for index 1 and 3.
                        if toonIndex % 2 == 0:
                            toonX = 3
                        else:
                            toonX = 9
                    # Y position is 47 for index 0 and 1, 44 for index 2 and 3.
                    if toonIndex <= 1:
                        toonY = 47
                    else:
                        toonY = 44
                else:
                    toonIndex = self.involvedToons.index(toonId)
                    startingX = -3 * (len(self.involvedToons) - 1)
                    toonX = startingX + (6 * toonIndex)
                    toonY = 47
                track.append(Sequence(
                    Func(toon.setPosHpr, toonX, toonY, -71.5765, 0, 0, 0),
                    Wait(2),
                    Func(toon.loop, 'run'),
                    LerpPosInterval(toon, 5.0, pos=(toonX, toonY + 77, -71.5765)),
                    Func(toon.loop, 'neutral')
                ))
        return track

    # Creates dynamic dialogue for the Litigation Team
    def makeLitigationDialogueMovie(self):
        """Duration: Varies Depending on Dialogue Chosen"""
        track = Sequence()
        for i in range(2):
            firstSuit = self.litigationOrder[i*2]
            secondSuit = self.litigationOrder[(i*2)+1]
            # Pull the correct four line dialogue for this combination
            dialogue = TTLocalizer.HardmodeLawbotBossLitigationDialogue[firstSuit][secondSuit]
            track.append(Func(base.camera.setPosHpr, self.elevatorModel, 0, -241.5, 10.2, 90 * (-1 + i*2), 5, 0))
            track.append(Func(self.litigationTeam[i*2].setChatAbsolute, dialogue[0], CFSpeech | CFTimeout))
            track.append(Wait(self.determineDialogueDuration(dialogue[0])))
            if firstSuit == 'stenog' and secondSuit == 'lgator':
                if len(self.involvedToons) <= 1:
                    j = 0
                elif len(self.involvedToons) <= 4:
                    j = 1
                elif len(self.involvedToons) <= 7:
                    j = 2
                else:
                    j = 3
                formattedDialogue = dialogue[1].format(len(self.involvedToons), TTLocalizer.HardmodeLawbotBossStenogThreatAnalysis[j][0], TTLocalizer.HardmodeLawbotBossStenogThreatAnalysis[j][1])
                track.append(Func(self.litigationTeam[i*2].setChatAbsolute, formattedDialogue, CFSpeech | CFTimeout))
                track.append(Wait(self.determineDialogueDuration(formattedDialogue)))
            else:
                track.append(Func(self.litigationTeam[i*2].setChatAbsolute, dialogue[1], CFSpeech | CFTimeout))
                track.append(Wait(self.determineDialogueDuration(dialogue[1])))
            track.append(Func(self.litigationTeam[i*2].clearChat))
            track.append(Func(base.camera.setPosHpr, self.elevatorModel, 0, -219.4, 10.2, 90 * (-1 + i*2), 5, 0))
            track.append(Func(self.litigationTeam[(i*2)+1].setChatAbsolute, dialogue[2], CFSpeech | CFTimeout))
            track.append(Wait(self.determineDialogueDuration(dialogue[2])))
            track.append(Func(self.litigationTeam[(i*2)+1].setChatAbsolute, dialogue[3], CFSpeech | CFTimeout))
            track.append(Wait(self.determineDialogueDuration(dialogue[3])))
            track.append(Func(self.litigationTeam[(i*2)+1].clearChat))
        return track

    # Dynamically determine duration of dialogue based on amount of characters
    def determineDialogueDuration(self, dialogue):
        if len(dialogue) <= 20:
            return 3
        elif len(dialogue) <= 40:
            return 3.5
        elif len(dialogue) <= 80:
            return 4
        else:
            return 5

    def makeLaurenButtonMovie(self):
        """Button is Pressed at time 2.3"""
        movie = Sequence()
        button = globalPropPool.getProp('trap-button')
        buttons = [button]
        hands = self.lawyerToon.getLeftHands()
        buttonSound = BattleSounds.globalBattleSoundCache.getSound('AA_drop_trigger_box.ogg')
        soundTrack = Sequence(
            Wait(2.3),
            SoundInterval(buttonSound, duration=0.67, node=self.lawyerToon)
        )
        movie.append(
            Parallel(
                Sequence(
                    Func(MovieUtil.showProps, buttons, hands),
                    Parallel(
                        ActorInterval(button, 'trap-button'),
                        Sequence(ActorInterval(self.lawyerToon, 'pushbutton'), Func(self.lawyerToon.loop, 'neutral'))
                    ),
                    Func(MovieUtil.removeProps, buttons)
                ),
                soundTrack
            )
        )
        return movie

    '''
    Toon positioning Functions

    All of the functions below are used to position toons into predefined locations around the room.

    Used almost exclusively for cutscenes.
    '''

    def toonsLineUpBattleTwo(self):
        i = 0
        startingX = -2 * (len(self.involvedToons) - 1)
        for toonId in self.involvedToons:
            toon = base.cr.doId2do.get(toonId)
            if toon:
                toon.setPosHpr(self.elevatorModel, startingX + (i * 4), -40, 0, 180, 0, 0)
                toon.loop('neutral')
                i += 1

    '''
    Room Manipulation Functions

    All of the functions below are used to manipulate parts of the CLO boss room for
    cutscene use, battle use, or whatever else you may need.

    Any intended manipulatable part should be done through this rather than attempting
    to recreate it in the code
    '''

    # Leaving these open for hardmode boss specific cutscene funcs.
