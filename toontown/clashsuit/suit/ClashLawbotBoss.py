from direct.directutil import Mopath
from direct.distributed.ClockDelta import *
from direct.fsm import FSM
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from toontown.chat.constants.ChatGlobals import *
from otp import *
from toontown.nametag import *
from toontown.clashsuit.suit import BossCogGlobals
from toontown.clashbattle.battle import BattleBase
from toontown.clashbattle.battle import BattleParticles
from toontown.clashbattle.battle import MovieToonVictory
from toontown.clashbattle.battle import RewardPanel
from toontown.clashbattle.battle.BattleProps import *
from toontown.clashbattle.battle import BattleSounds
from toontown.building import ElevatorConstants
from toontown.building import ElevatorUtils
from toontown.coghq import CogDisguiseGlobals
from toontown.distributed import DelayDelete
from toontown.gui.game.condition import ConditionGlobals
from toontown.clashsuit.suit import ClashBossCog
from toontown.clashsuit.suit import DistributedLawbotBossSecurityCamera
from toontown.clashsuit.suit import Suit
from toontown.clashsuit.suit import SuitDNA
from toontown.clashsuit.suit import SuitHealthMeter
from toontown.gui import DepartmentExperienceBar
from toontown.toon.npc import NPCToons
from toontown.toonbase import TTLocalizer
# from toontown.toonbase import BattleGlobals
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownTimer
from toontown.coghq import EvidenceGUI
from toontown.toonbase.GlobalCacheData import GlobalCacheKey
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

OneBossCog = None


@DirectNotifyCategory()
class ClashLawbotBoss(ClashBossCog.ClashBossCog, FSM.FSM):
    def __init__(self, cr):
        ClashBossCog.ClashBossCog.__init__(self, cr)
        FSM.FSM.__init__(self, 'ClashLawbotBoss')
        self.lawyers = []
        self.lawyerRequest = None
        self.bossDamage = 0
        self.attackCode = None
        self.attackAvId = 0
        self.everUsedSound = 0
        self.battleFourMusicTime = 0
        self.insidesANodePath = None
        self.insidesBNodePath = None
        self.onscreenMessage = None
        self.bossMaxDamage = BossCogGlobals.LawbotBossMaxDamage
        self.elevatorType = ElevatorConstants.ELEVATOR_CLO
        self.cannons = {}
        self.witnessToon = None
        self.witnessToonOnstage = False
        self.lawyerToon = None
        self.lawyerToonOnstage = False
        self.evidenceHitSfx = None
        self.toonUpSfx = None
        self.mouseOverText = None
        self.warningSfx = None
        self.juryMovesSfx = None
        self.cannonIndex = -1
        self.paintingOpenTime = 3.0 # Speed is half of this atm
        self.paintingSequences = {}
        self.executiveMembers = []
        self.desperationState = -1
        self.moveTrack = None
        self.departmentExpBar = None
        self.traps = {}
        self.bossDamageMovie = None
        self.victorySequence = None
        self.numSuesEarned = {}
        self.evidence = {}
        self.enterEvidenceBoxEvent = "enterEvidenceBox"
        self.gavels = {}
        self.cogRoundSpotlights = [None, None]
        self.evidenceRoundTimer = None
        self.particle = None
        self.particleRender = None
        self.finalBattleState = 'BattleFour'
        self.randomFallPos = [0, 0, 0]
        self.defenseSpecialists = []
        self.defenseSpecialistsRotateNode = None
        self.defenseSpecialistsRotateNodeLoop = None

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        base.globalCache.swapToKey(GlobalCacheKey.LawbotBoss)

        global OneBossCog
        ClashBossCog.ClashBossCog.announceGenerate(self)
        self.setName(TTLocalizer.LawbotBossName)
        nameInfo = TTLocalizer.BossCogNameWithDept % {'name': self.getName(),
         'dept': SuitDNA.getDeptFullname(self.style.dept)}
        self.setDisplayName(nameInfo)
        self.healthGui.setBossName(TTLocalizer.LawbotBossName)
        self.evidenceRestockSfx = loader.loadSfx('phase_5/audio/sfx/LB_receive_evidence.ogg')
        self.rampSlideSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_ramp_slide.ogg')
        self.evidenceHitSfx = loader.loadSfx('phase_11/audio/sfx/LB_evidence_hit.ogg')
        self.warningSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_GOON_tractor_beam_alarmed.ogg')
        self.juryMovesSfx = loader.loadSfx('phase_11/audio/sfx/LB_jury_moves.ogg')
        self.toonUpSfx = loader.loadSfx('phase_11/audio/sfx/LB_toonup.ogg')
        self.evidenceCollectSfx = loader.loadSfx('phase_3.5/audio/sfx/tick_counter.ogg')
        self.spotlightOnSfx = loader.loadSfx('phase_11/audio/sfx/LB_laser_beam_on_2.ogg')
        self.spotlightOffSfx = loader.loadSfx('phase_11/audio/sfx/LB_capacitor_discharge_3.ogg')
        self.evidenceBoxOpenSfx = loader.loadSfx('phase_5/audio/sfx/toonbldg_settle.ogg')
        self.fallingSfx = loader.loadSfx('phase_5/audio/sfx/ENC_Lose_shrinking.ogg')
        self.tableLandSfx = loader.loadSfx('phase_5/audio/sfx/AA_drop_bigweight_miss.ogg')
        self.papersLandSfx = loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cmg_itemHitsFloor.ogg')
        self.bossLandSfx = loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')

        render.setTag('pieCode', str(ToontownGlobals.PieCodeNotBossCog))
        closeBubble = CollisionSphere(0, 0, 0, 18)
        closeBubble.setTangible(0)
        closeBubbleNode = CollisionNode('CloseBoss')
        closeBubbleNode.setIntoCollideMask(BitMask32(0))
        closeBubbleNode.setFromCollideMask(ToontownGlobals.LawyerNearbyBitmask)
        closeBubbleNode.addSolid(closeBubble)
        self.closeBubbleNode = closeBubbleNode
        self.closeHandler = CollisionHandlerEvent()
        self.closeHandler.addInPattern('closeEnter')
        self.closeHandler.addOutPattern('closeExit')
        self.closeBubbleNodePath = self.attachNewNode(closeBubbleNode)
        (base.cTrav.addCollider(self.closeBubbleNodePath, self.closeHandler),)
        self.accept('closeEnter', self.closeEnter)
        self.accept('closeExit', self.closeExit)
        insidesA = CollisionPolygon(Point3(4.0, -2.0, 5.0), Point3(-4.0, -2.0, 5.0), Point3(-4.0, -2.0, 0.5), Point3(4.0, -2.0, 0.5))
        insidesANode = CollisionNode('BossZap')
        insidesANode.addSolid(insidesA)
        insidesANode.setCollideMask(ToontownGlobals.PieBitmask | ToontownGlobals.WallBitmask)
        self.insidesANodePath = self.axle.attachNewNode(insidesANode)
        self.insidesANodePath.setTag('pieCode', str(ToontownGlobals.PieCodeBossInsides))
        self.insidesANodePath.stash()
        insidesB = CollisionPolygon(Point3(-4.0, 2.0, 5.0), Point3(4.0, 2.0, 5.0), Point3(4.0, 2.0, 0.5), Point3(-4.0, 2.0, 0.5))
        insidesBNode = CollisionNode('BossZap')
        insidesBNode.addSolid(insidesB)
        insidesBNode.setCollideMask(ToontownGlobals.PieBitmask | ToontownGlobals.WallBitmask)
        self.insidesBNodePath = self.axle.attachNewNode(insidesBNode)
        self.insidesBNodePath.setTag('pieCode', str(ToontownGlobals.PieCodeBossInsides))
        self.insidesBNodePath.stash()
        target = CollisionTube(0, -1, 4, 0, -1, 9, 3.5)
        targetNode = CollisionNode('BossZap')
        targetNode.addSolid(target)
        targetNode.setCollideMask(ToontownGlobals.PieBitmask)
        self.targetNodePath = self.pelvis.attachNewNode(targetNode)
        self.targetNodePath.setTag('pieCode', str(ToontownGlobals.PieCodeBossCog))
        shield = CollisionTube(0, 1, 4, 0, 1, 7, 3.5)
        shieldNode = CollisionNode('BossZap')
        shieldNode.addSolid(shield)
        shieldNode.setCollideMask(ToontownGlobals.PieBitmask | ToontownGlobals.CameraBitmask)
        self.pelvis.attachNewNode(shieldNode)
        disk = loader.loadModel('phase_9/models/char/bossCog-gearCollide')
        disk.find('**/+CollisionNode').setName('BossZap')
        disk.reparentTo(self.pelvis)
        disk.setZ(0.8)
        self.loadEnvironment()
        self.makeWitnessToon()
        self.makeLawyerToon()
        self.__loadMopaths()
       # self.addSpeedchatMenu()
        self.treads = self.find('**/treads')
        if OneBossCog is not None:
            self.notify.warning('Multiple BossCogs visible.')
        OneBossCog = self

   # def addSpeedchatMenu(self):
    #    base.localAvatar.chatContainer.speedChatMenu.addCLOMenu()

   # def removeSpeedchatMenu(self):
    #    base.localAvatar.chatContainer.speedChatMenu.removeCLOMenu()

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        global OneBossCog
        ClashBossCog.ClashBossCog.disable(self)
        base.cTrav.removeCollider(self.closeBubbleNodePath)
        self.request('Off')
        for sequence in list(self.paintingSequences.values()):
            if sequence.isPlaying():
                sequence.finish()
                del sequence
        del self.traps
        del self.cannons
        del self.paintingSequences
        self.unloadEnvironment()
        self.__cleanupWitnessToon()
        self.__cleanupLawyerToon()
        self.cleanupExecutiveMembers()
        self.__unloadMopaths()
        self.clearOnscreenMessage()
        self.deleteCogRoundSpotlights()
        taskMgr.remove(self.uniqueName('SoundAdvice'))
        render.clearTag('pieCode')
        if self.evidenceRoundTimer:
            self.evidenceRoundTimer.destroy()
            del self.evidenceRoundTimer
        self.targetNodePath.detachNode()
        self.cr.relatedObjectMgr.abortRequest(self.lawyerRequest)
        self.lawyerRequest = None
        base.musicMgr.stopMusic()
       # self.removeSpeedchatMenu()
        if OneBossCog == self:
            OneBossCog = None
        if self.victorySequence:
            self.victorySequence.finish()
            self.victorySequence = None
        if self.moveTrack:
            self.moveTrack.finish()
            self.moveTrack = None

        if self.defenseSpecialistsRotateNodeLoop is not None:
            self.defenseSpecialistsRotateNodeLoop.finish()
            self.defenseSpecialistsRotateNodeLoop = None

        if self.defenseSpecialistsRotateNode is not None:
            self.defenseSpecialistsRotateNode.removeNode()
            self.defenseSpecialistsRotateNode = None

    def delete(self):
        ClashBossCog.ClashBossCog.delete(self)

    def d_hitBoss(self):
        self.sendUpdate('hitBoss')

    def gotToon(self, toon):
        if self.state == 'Elevator':
            self.placeToonInElevator(toon)

    def closeEnter(self, entry):
        lawyerCol = entry.getIntoNodePath()
        if 'DocketCSphereNode' in lawyerCol.getName():
            return

        names = lawyerCol.getName().split('-')
        lawyerDoId = int(names[1])

        for lawyer in self.lawyers:
            if lawyerDoId == lawyer.doId:
                self.sendUpdate('lawyerNearEnter', [lawyer.doId])
                break

    def closeExit(self, entry):
        lawyerCol = entry.getIntoNodePath()
        names = lawyerCol.getName().split('-')
        lawyerDoId = int(names[1])

        for lawyer in self.lawyers:
            if lawyerDoId == lawyer.doId:
                self.sendUpdate('lawyerNearExit', [lawyer.doId])
                break

    def createPaintingMovie(self, painting, finalBattle=1):
        if self.paintingSequences.get(painting) and self.paintingSequences[painting].isPlaying():
            self.paintingSequences[painting].finish()
            self.paintingSequences[painting] = None
        seq = Sequence(Func(self.openPainting, painting, 1, finalBattle), Wait(8), Func(self.closePainting, painting, 1, finalBattle))
        seq.start()
        self.paintingSequences[painting] = seq

    def sendLawyerId(self, lawyerId):
        self.cr.relatedObjectMgr.abortRequest(self.lawyerRequest)
        self.lawyerRequest = self.cr.relatedObjectMgr.requestObjects([lawyerId], allCallback=self.__gotLawyer)

    def __gotLawyer(self, lawyer):
        lawyer = lawyer[0]
        self.lawyerRequest = None
        self.lawyers.append(lawyer)
        if lawyer.state == 'Off':
            lawyer.request('Neutral')
        lawyer.setBossCogId(self.doId)

    def sendDefenseSpecialistId(self, lawyerId):
        self.cr.relatedObjectMgr.abortRequest(self.lawyerRequest)
        self.lawyerRequest = self.cr.relatedObjectMgr.requestObjects([lawyerId], allCallback=self.__gotDefenseSpecialist)

    def __gotDefenseSpecialist(self, lawyer):
        lawyer = lawyer[0]
        self.lawyerRequest = None
        self.defenseSpecialists.append(lawyer)
        lawyer.setBossCogId(self.doId)

    @property
    def dizzyMusic(self):
        return self.battleFourDizzyMusic

    @property
    def unDizzyMusic(self):
        return self.battleFourMusic

    def setBossDamage(self, bossDamage, desperationState):
        delta = bossDamage - self.bossDamage
        if delta != 0:
            if delta > 0:
                self.flashRed()
            elif delta < 0:
                self.flashGreen()
            self.showHpText(-delta, scale=5)
        if self.dizzy and delta > 0:
            self.specialHead.play('hit')
            self.doAnimate('hit', now=1)
        self.bossDamage = bossDamage
        self.desperationState = desperationState
        if self.desperationState == 1:
            self.treads.setColorScale(0.25, 1, 0.25, 1)
        elif self.desperationState == 0:
            self.treads.setColorScale(0.5, 1, 0.5, 1)
        else:
            self.treads.setColorScale(1, 1, 1, 1)
        self.healthGui.updateHealth(self.bossMaxDamage - self.bossDamage)
        self.updateHealthBar()
        messenger.send(ConditionGlobals.RefreshMsg)

    def updateDamageDealt(self, avId, damageDealt):
        self.healthGui.updateDamageDealt(avId, damageDealt)

    def updateStunCount(self, avId):
        self.healthGui.updateStunCount(avId)

    def updateCogDestructionCount(self, avId, cogDestroy):
        self.healthGui.updateCogDestructionCount(avId, cogDestroy)

    def updateEvidence(self, avId, evidenceAmt):
        self.evidenceGUI.updateEvidence(avId, evidenceAmt)

    def __walkToonToPromotion(self, toonId, delay, mopath, track, delayDeletes):
        toon = base.cr.doId2do.get(toonId)
        if toon:
            destPos = toon.getPos()
            self.placeToonInElevator(toon)
            toon.wrtReparentTo(render)
            ival = Sequence(Wait(delay), Func(toon.suit.setPlayRate, 1, 'walk'), Func(toon.suit.loop, 'walk'), toon.posInterval(1, Point3(0, 90, 20)), ParallelEndTogether(MopathInterval(mopath, toon), toon.posInterval(2, destPos, blendType='noBlend')), Func(toon.suit.loop, 'neutral'))
            track.append(ival)
            delayDeletes.append(DelayDelete.DelayDelete(toon, 'LawbotBoss.__walkToonToPromotion'))

    def toNeutralMode(self):
        if self.cr:
            place = self.cr.playGame.getPlace()
            if place and hasattr(place, 'fsm'):
                place.setState('waitForBattle')

    def makeToonsWait(self):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                toon.stopLookAround()
                toon.stopSmooth()

        if self.hasLocalToon():
            self.toMovieMode()
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                toon.loop('neutral')

    def showOnscreenMessage(self, text):
        if self.onscreenMessage:
            self.onscreenMessage.destroy()
            self.onscreenMessage = None
        self.onscreenMessage = DirectLabel(text=text, text_fg=VBase4(1, 1, 1, 1), text_align=TextNode.ACenter, relief=None, pos=(0, 0, 0.35), scale=0.1)

    def clearOnscreenMessage(self):
        if self.onscreenMessage:
            self.onscreenMessage.destroy()
            self.onscreenMessage = None

    def __showWaitingMessage(self, task):
        self.showOnscreenMessage(TTLocalizer.BuildingWaitingForVictors)

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
        self.elevatorMusic = 'clo_elevator'
        self.promotionMusic = 'clo_intro_cutscene'
        self.stingMusic = 'clo_table_collapse'
        self.battleOneMusic = 'clo_battle_one'
        self.cannonCtscMusic = 'clo_cannon_cutscene'
        self.battleTwoMusic = 'clo_battle_two'
        self.battleThreeMusic = 'clo_battle_three'
        self.betweenBattleMusic = 'clo_megaphone_cutscene'
        self.battleFourMusic = 'clo_battle_four'
        self.battleFourDizzyMusic = 'clo_battle_four_stunned'
        self.killMusic = 'clo_battle_stinger'
        self.victoryMusic = 'clo_victory'
        self.epilogueMusic = 'clo_epilogue'
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

    def loadEvidenceBox(self):
        modelPath = "phase_11/models/lawbotHQ/evidencebox"
        self.evidenceBox = Actor.Actor(modelPath, {"idle": "{}-idle-loop".format(modelPath), "open": "{}-open".format(modelPath)})
        self.evidenceBox.setBlend(frameBlend = base.wantSmoothAnims)
        self.evidenceBox.reparentTo(self.geom)
        self.evidenceBox.setPosHpr(*BossCogGlobals.LawbotBossEvidenceBoxPosHpr)
        col = self.evidenceBox.find("**/box_col")
        col.setName("EvidenceBox")

    def setupLeftElevator(self, elevatorModel):
        self.leftLeftDoor = elevatorModel.find('**/left-door')
        if self.leftLeftDoor.isEmpty():
            self.leftLeftDoor = elevatorModel.find('**/left_door')
        self.leftRightDoor = elevatorModel.find('**/right-door')
        if self.leftRightDoor.isEmpty():
            self.leftRightDoor = elevatorModel.find('**/right_door')
        openSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_sliding.ogg')
        finalOpenSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_final.ogg')
        closeSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_sliding.ogg')
        finalCloseSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_final.ogg')
        self.openLeftDoors = ElevatorUtils.getOpenInterval(self, self.leftLeftDoor, self.leftRightDoor, openSfx, finalOpenSfx, self.elevatorType)
        self.closeLeftDoors = ElevatorUtils.getCloseInterval(self, self.leftLeftDoor, self.leftRightDoor, closeSfx, finalCloseSfx, self.elevatorType)
        self.closeLeftDoors.start()
        self.closeLeftDoors.finish()

    def setupRightElevator(self, elevatorModel):
        self.rightLeftDoor = elevatorModel.find('**/left-door')
        if self.rightLeftDoor.isEmpty():
            self.rightLeftDoor = elevatorModel.find('**/left_door')
        self.rightRightDoor = elevatorModel.find('**/right-door')
        if self.rightRightDoor.isEmpty():
            self.rightRightDoor = elevatorModel.find('**/right_door')
        openSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_sliding.ogg')
        finalOpenSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_final.ogg')
        closeSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_sliding.ogg')
        finalCloseSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_final.ogg')
        self.openRightDoors = ElevatorUtils.getOpenInterval(self, self.rightLeftDoor, self.rightRightDoor, openSfx, finalOpenSfx, self.elevatorType)
        self.closeRightDoors = ElevatorUtils.getCloseInterval(self, self.rightLeftDoor, self.rightRightDoor, closeSfx, finalCloseSfx, self.elevatorType)
        self.closeRightDoors.start()
        self.closeRightDoors.finish()

    def makeCogRoundSpotlights(self):
        for i in range(2):
            spotlight = DistributedLawbotBossSecurityCamera.DistributedLawbotBossSecurityCamera(base.cr)
            spotlight.doId = -50 - i
            spotlight.isCogRound = 1
            spotlight.generate()
            spotlight.announceGenerate()
            spotlight.setPos(BossCogGlobals.LawbotBossTrackingSpotlightPosList[i][0])
            spotlight.setWideX(1.2)
            spotlight.setWideY(0.65)
            spotlight.setProjector((0, 0, 115))
            self.cogRoundSpotlights[i] = spotlight
        self.hideCogRoundSpotlights()
        self.updateCogRoundSpotlightPos(0, BossCogGlobals.LawyerVirtualBattleSpotlightPos[0])
        self.updateCogRoundSpotlightPos(1, BossCogGlobals.LawyerVirtualBattleSpotlightPos[1])

    def deleteCogRoundSpotlights(self):
        for spotlight in self.cogRoundSpotlights:
            if not spotlight:
                return
            spotlight.disable()
            spotlight.delete()
            spotlight = None
        self.cogRoundSpotlights = []

    def hideCogRoundSpotlight(self, index):
        if index >= len(self.cogRoundSpotlights):
            return
        self.cogRoundSpotlights[index].hide()

    def hideCogRoundSpotlights(self):
        for spotlight in self.cogRoundSpotlights:
            spotlight.hide()

    def showCogRoundSpotlight(self, index):
        self.cogRoundSpotlights[index].show()

    def updateCogRoundSpotlightPos(self, index, pos):
        self.cogRoundSpotlights[index].newPosition(pos[0], pos[1])

    def endCogRoundSpotlight(self, index):
        if not self.cogRoundSpotlights[index]:
            return
        seq = Sequence(Func(base.playSfx, self.spotlightOffSfx), LerpColorScaleInterval(self.cogRoundSpotlights[index], 1.0, (0, 0, 0, 1), blendType='easeIn'), Func(self.hideCogRoundSpotlight, index))
        seq.start()

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

    def __loadMopaths(self):
        self.toonsEnterA = Mopath.Mopath()
        self.toonsEnterA.loadFile('phase_9/paths/bossBattle-toonsEnterA')
        self.toonsEnterA.fFaceForward = 1
        self.toonsEnterA.timeScale = 35
        self.toonsEnterB = Mopath.Mopath()
        self.toonsEnterB.loadFile('phase_9/paths/bossBattle-toonsEnterB')
        self.toonsEnterB.fFaceForward = 1
        self.toonsEnterB.timeScale = 35

    def __unloadMopaths(self):
        self.toonsEnterA.reset()
        self.toonsEnterB.reset()

    def enterOff(self):
        ClashBossCog.ClashBossCog.enterOff(self)
        if self.witnessToon:
            self.witnessToon.clearChat()

    def enterWaitForToons(self):
        ClashBossCog.ClashBossCog.enterWaitForToons(self)
        self.geom.hide()
        self.witnessToon.removeActive()

    def exitWaitForToons(self):
        ClashBossCog.ClashBossCog.exitWaitForToons(self)
        self.geom.show()
        self.witnessToon.addActive()

    def enterElevator(self):
        base.discord.applyPreset('boss-l-1')
        ClashBossCog.ClashBossCog.enterElevator(self)
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleOnePosHpr)
        self.reparentTo(render)
        self.happy = 1
        self.raised = 1
        self.forward = 1
        self.doAnimate()
        self.showWitnessToon()
        self.showLawyerToon()
        self.makeExecutiveMembers()
        self.witnessToon.putOnSuit(self.witnessToon.suitType)
        self.witnessToon.setDisplayName(TTLocalizer.WitnessToonName)
        self.lawyerToon.putOnSuit(self.lawyerToon.suitType)
        self.lawyerToon.setDisplayName(TTLocalizer.LawyerToonName)
        base.camera.reparentTo(self.elevatorModel)
        base.camera.setPosHpr(0, 30, 8, 180, 0, 0)
        base.camLens.setMinFov(ToontownGlobals.CJElevatorFov/(4./3.))

    def enterIntroduction(self):
        self.reparentTo(render)
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleOnePosHpr)
        self.stopAnimate()
        base.camera.setPosHpr(0, 30, 8, 180, 0, 0)
        base.camera.reparentTo(self.elevatorModel)
        base.camLens.setMinFov(ToontownGlobals.CJElevatorFov/(4./3.))
        ClashBossCog.ClashBossCog.enterIntroduction(self)
        self.battleANode.setPosHpr(*BossCogGlobals.LawyerBattleAPosHpr)
        self.battleBNode.setPosHpr(*BossCogGlobals.LawyerBattleBPosHpr)
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
        self.cleanupExecutiveMembers()

    def enterBattleOne(self):
        ClashBossCog.ClashBossCog.enterBattleOne(self)
        self.reparentTo(render)
        #TODO: reduntant?
        self.toonsToBattlePosition(self.toonsA, self.battleANode)
        self.toonsToBattlePosition(self.toonsB, self.battleBNode)
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleBackFromTablePosHpr)

        self.clearChat()
        self.loop('Ff_neutral')
        base.discord.applyPreset('boss-l-2')

    def exitBattleOne(self):
        ClashBossCog.ClashBossCog.exitBattleOne(self)

    def stashBoss(self):
        self.stash()

    def unstashBoss(self, task):
        self.unstash()
        self.reparentTo(render)

    def enterPrepareBattleTwo(self):
        self.cleanupIntervals()
        self.controlToons()
        self.closeEntryDoors(animated=0)
        self.setToonsToNeutral(self.involvedToons)
        self.positionToonsInFrontOfCannons()
        self.clearChat()
        self.reparentTo(render)
        base.camera.setPosHpr(self.elevatorModel, 0, -265, 18, 180, 7, 0)
        self.showWitnessToon()
        self.witnessToon.setPosHpr(0, 85, 0, 0, 0, 0)
        self.cleanupExecutiveMembers()
        intervalName = 'PrepareBattleTwoMovie'
        [gav.nodePath.setScale(.01) for gav in list(self.gavels.values())]
        seq = Sequence(self.__makePrepareBattleTwoMovie(), Func(self.__onToBattleTwo), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        base.musicMgr.playMusic(self.cannonCtscMusic, looping=0, volume=1.0)
        self.acceptOnce('skipCutscene', self.__onToBattleTwo)

    def positionToonsInFrontOfCannons(self):
        index = 0
        for toonId in self.involvedToons:
            if index in self.cannons:
                cannon = self.cannons[index]
                toon = self.cr.doId2do.get(toonId)
                if toon:
                    toon.reparentTo(cannon.parentNode)
                    toon.setPos(0, 8, 0)
                    toon.lookAt(cannon.parentNode)
                    renderPos = toon.getPos(render)
                    index += 1

    def showCannonsAppearing(self):
        camHeight = base.localAvatar.getClampedAvatarHeight() * 0.3333333333
        allCannonsAppear = Sequence(
            Func(self.positionToonsInFrontOfCannons),
            Func(base.camera.reparentTo, localAvatar),
            Func(base.camera.setPos, 5.7 * camHeight, 7.65 * camHeight, camHeight + .25),
            Func(base.camera.lookAt, localAvatar)
        )
        multiCannons = Parallel()
        index = 0
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                if index in self.cannons:
                    cannon = self.cannons[index]
                    cannonSeq = cannon.generateCannonAppearTrack(toon)
                    multiCannons.append(cannonSeq)
                    index += 1
                else:
                    self.notify.warning('No cannon %d but we have a toon =%d' % (index, toonId))

        allCannonsAppear.append(multiCannons)
        return allCannonsAppear

    def __onToBattleTwo(self, elapsedTime = 0):
        self.doneBarrier('PrepareBattleTwo')

    def exitPrepareBattleTwo(self):
        self.ignore('skipCutscene')
        self.clearInterval('PrepareBattleTwoMovie')
        self.show()
        [gav.nodePath.setScale(gav.scale) for gav in list(self.gavels.values())]

    def enterBattleTwo(self):
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
        base.musicMgr.playMusic(self.battleTwoMusic, looping=1, volume=0.9)
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
        self.evidenceGUI = EvidenceGUI.EvidenceGUI()
        self.evidenceGUI.reparentTo(base.a2dBottomRight)
        base.discord.applyPreset('boss-l-3')

    def addPaperParticles(self):
        if not self.particle:
            self.particle = BattleParticles.loadParticleFile('paperRainCLO.ptf')
            self.particle.setPos(0, 220, 150)
            self.particle.setScale(2.25, 2.1, 1.0)
            self.particleRender = self.geom.attachNewNode('particleRender')
            self.particleRender.setDepthWrite(0)
            self.particleRender.setBin('fixed', 1)
            self.particle.start(self.geom, self.particleRender)

    def removePaperParticles(self):
        if self.particle:
            self.particle.cleanup()
            self.particle = None
        if self.particleRender:
            self.particleRender.removeNode()
            self.particleRender = None

    def exitBattleTwo(self):
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

    def enterPrepareBattleThree(self):
        self.stashFurniture()
        self.makeCogRoundSpotlights()
        self.cleanupIntervals()
        self.controlToons()
        self.setToonsToNeutral(self.involvedToons)
        self.toonsLineUpBattleThree()
        self.battleANode.setPosHpr(20, -93, 0, 180, 0, 0)
        self.battleBNode.setPosHpr(-20, -93, 0, 180, 0, 0)
        self.cleanupExecutiveMembers()
        localAvatar.setCameraFov(ToontownGlobals.BossBattleCameraFov)
        intervalName = 'PrepareBattleThreeMovie'
        seq = Sequence(self.__makePrepareBattleThreeMovie(), Func(self.__onToBattleThree), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        self.acceptOnce('skipCutscene', self.__onToBattleThree)

    def exitPrepareBattleThree(self):
        self.ignore('skipCutscene')
        self.clearInterval('PrepareBattleThreeMovie')

    def __onToBattleThree(self, elapsedTime = 0):
        self.doneBarrier("PrepareBattleThree")

    def enterBattleThree(self):
        base.musicMgr.stopMusic(self.battleTwoMusic)
        self.cleanupIntervals()
        self.reparentTo(render)
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleThreePosHpr)
        self.clearChat()
        if self.battleA:
            self.showCogRoundSpotlight(0)
        if self.battleB:
            self.showCogRoundSpotlight(1)
        self.setToonsToNeutral(self.involvedToons)
        # mult = BattleGlobals.getBossBattleCreditMultiplier(2)
        # localAvatar.inventory.setBattleCreditMult(mult)
        self.setBattleCreditMult(2)
        self.toonsToBattlePosition(self.toonsA, self.battleANode)
        self.toonsToBattlePosition(self.toonsB, self.battleBNode)
        self.releaseToons()
        self.setPickable(1)
        base.discord.applyPreset('boss-l-4')

    def exitBattleThree(self):
        self.cleanupBattles()
        base.musicMgr.stopMusic(self.battleThreeMusic)
        # localAvatar.inventory.setBattleCreditMult(1)

    def enterPrepareBattleFour(self):
        self.stashFurniture()
        base.musicMgr.stopMusic(self.battleThreeMusic)
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
        base.camera.setPosHpr(self.elevatorModel, 0, -179, 18, 180, 7, 0)
        base.musicMgr.playMusic(self.betweenBattleMusic, looping=1, volume=0.9)
        self.showWitnessToon()
        self.witnessToon.takeOffSuit()
        self.witnessToon.setPosHpr(0, 85, 0, 0, 0, 0)
        self.cleanupExecutiveMembers()
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
        self.witnessToon.clearChat()
        self.reparentTo(render)
        self.happy = 1
        self.raised = 1
        self.forward = 1
        self.doAnimate()
        self.deleteCogRoundSpotlights()
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
        base.discord.applyPreset('boss-l-5')

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
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'LawbotBoss.enterReward'))

        ival.delayDeletes = delayDeletes
        ival.start()
        self.storeInterval(ival, intervalName)
        if base.musicMgr.getMusicFilepath(self.victoryMusic) != base.musicMgr.getMusicFilepath(self.battleFourMusic): # We have a custom victory theme loaded
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
        self.clearInterval(intervalName)
        track = Parallel(Sequence(Wait(0.5), Func(self.localToonToSafeZone)))
        self.storeInterval(track, intervalName)
        track.start()

    def exitEpilogue(self):
        self.clearInterval('EpilogueMovieToonAnim')
        self.unstash()
        self.ignore('nextChatPage')
        self.ignore('doneChatPage')
        base.musicMgr.stopMusic(self.epilogueMusic)

    def setNumSuesEarned(self, toonId, numSues):
        if toonId not in self.numSuesEarned:
            self.numSuesEarned[toonId] = numSues

    def enterFrolic(self):
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleOnePosHpr)
        ClashBossCog.ClashBossCog.enterFrolic(self)
        self.show()

    def __toonsToPromotionPosition(self, toonIds, battleNode):
        points = BattleBase.BattleBase.toonPoints[len(toonIds) - 1]
        for i in range(len(toonIds)):
            toon = base.cr.doId2do.get(toonIds[i])
            if toon:
                toon.reparentTo(render)
                pos, h = points[i]
                toon.setPosHpr(battleNode, pos[0], pos[1] + 10, pos[2], h, 0, 0)

    def withdrawEvidence(self, entry):
        self.sendUpdate("withdrawEvidence", [])
        self.clearOnscreenMessage()
        taskMgr.remove(self.uniqueName('SoundAdvice'))
        base.playSfx(self.evidenceRestockSfx)
        if not self.everUsedSound:
            taskMgr.doMethodLater(30, self.howToUseSound, self.uniqueName('SoundAdvice'))

    def outOfSound(self):
        self.showOnscreenMessage(TTLocalizer.LawbotBossNeedMoreEvidence)
        taskMgr.doMethodLater(20, self.howToGetSound, self.uniqueName('SoundAdvice'))

    def howToGetSound(self, task):
        self.showOnscreenMessage(TTLocalizer.LawbotBossHowToGetSound)

    def howToUseSound(self, task):
        self.showOnscreenMessage(TTLocalizer.LawbotBossHowToUseSound % base.PRIMARY_KEY.upper())

    def foundSoundButton(self):
        self.everUsedSound = 1
        self.clearOnscreenMessage()
        taskMgr.remove(self.uniqueName('SoundAdvice'))

    def createBossTrapMovie(self, trapIndex, defenseSpecialistsMade):
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

        bossTrack.append(Func(self.setPos, x, y, -25))
        bossTrack.append(Func(self.setHpr, h, 0, 0))

        if defenseSpecialistsMade:
            bossTrack.append(Func(self.handleDefenseSpecialistSpawn))

        bossTrack.append(Parallel(LerpPosInterval(self, 0.5, Point3(x, y, -71.606)),
                                  Func(self.doAnimate, 'Ff_trapfall', now=1, raised=1),
                                  Func(self.specialHead.play, 'Ff_trapfall'),
                                  ))
        bossTrack.append(SoundInterval(self.bossLandSfx, duration=1.9))

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

    def setRandomFallPosition(self, x, y, h):
        self.randomFallPos = x, y, h

    def interruptBossDamageMovie(self):
        if self.bossDamageMovie and self.bossDamageMovie.isPlaying():
            self.bossDamageMovie.finish()
        self.bossDamageMovie = None

    def soundHit(self, toon, pieCode):
        if self.victorySequence:
            return
        if localAvatar.soundModeInUse == ToontownGlobals.SoundMegaphoneNormal:
            if pieCode == ToontownGlobals.PieCodeBossCog:
                if toon == localAvatar:
                    self.d_hitBoss()

    def localSoundHit(self, pieCode, entry):
        if pieCode == ToontownGlobals.PieCodeLawyer:
            if localAvatar.soundModeInUse == ToontownGlobals.SoundMegaphoneNormal:
                self.lawyerGotHit(entry)
            elif localAvatar.soundModeInUse == ToontownGlobals.SoundMegaphoneTaunt:
                self.lawyerGotHit(entry, taunt=1)

    def lawyerGotHit(self, entry, taunt=0):
        lawyerCol = entry.getIntoNodePath()
        names = lawyerCol.getName().split('-')
        lawyerDoId = int(names[1])
        for lawyer in self.lawyers:
            if lawyerDoId == lawyer.doId:
                lawyer.d_hitSuit(taunt)
        for lawyer in self.defenseSpecialists:
            if lawyerDoId == lawyer.doId:
                lawyer.d_hitSuit(taunt)

    def makeIntroductionMovie(self, delayDeletes):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'LawbotBoss.makeIntroductionMovie'))
        endPos = (0, 291, -71.601)
        panMovie = self.makeExecutivePanMovie()
        scootBack, scootBackHpr = self.rollBossToPoint(Point3(
            BossCogGlobals.LawbotBossBattleTablePosHpr[0], BossCogGlobals.LawbotBossBattleTablePosHpr[1], BossCogGlobals.LawbotBossBattleTablePosHpr[2]), None, Point3(
            BossCogGlobals.LawbotBossBattleBackFromTablePosHpr[0], BossCogGlobals.LawbotBossBattleBackFromTablePosHpr[1], BossCogGlobals.LawbotBossBattleBackFromTablePosHpr[2]), None, 1)
        tableFall = self.makeTableFallMovie()
        lawyerLoseSuit = self.loseCogSuits([self.lawyerToon, ], self.elevatorModel, (0, -150, 8, 0, 0, 0), arrayOfObjs = True)
        toonsLoseSuit = self.loseCogSuits(self.involvedToons, self.elevatorModel, (0, -150, 8, 0, 0, 0), arrayOfObjs = False)
        bumpyLoseSuit = self.loseCogSuits([self.witnessToon, ], self.elevatorModel, (0, -150, 8, 0, 0, 0), arrayOfObjs = True)
        toonsSidestep = self.toonsDodgeLawyerToon()

        def setIntroPlayRate(playRate):
            base.musicMgr.setPlayRate(self.promotionMusic, playRate)

        track = Track(
            (0.0, LerpPosHprInterval(base.camera, 1.5, Vec3(-15, -40, 3), Vec3(150, 15, 0), other = self.elevatorModel)),
            (1.5, Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossIntro0, CFSpeech)),
            (4.5, Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossIntro1, CFSpeech)),
            (7.5, Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossIntro2, CFSpeech)),
            (10.5, Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossIntro3, CFSpeech)),
            (13.5, Parallel(LerpPosHprInterval(base.camera, 1.5, Vec3(15, -40, 3), Vec3(210, 15, 0), other = self.elevatorModel), Func(self.witnessToon.clearChat))),
            (15.0, Func(self.lawyerToon.setChatAbsolute, TTLocalizer.LawbotBossIntro4, CFSpeech)),
            (17.0, Func(self.lawyerToon.setChatAbsolute, TTLocalizer.LawbotBossIntro5, CFSpeech)),
            (21.0, Func(self.lawyerToon.setChatAbsolute, TTLocalizer.LawbotBossIntro6, CFSpeech)),
            (24.0, Func(self.lawyerToon.setChatAbsolute, TTLocalizer.LawbotBossIntro7, CFSpeech)),
            (27.0, LerpPosHprInterval(base.camera, 2.0, Vec3(0, -30, 2), Vec3(180, 10, 0), other=self.elevatorModel)),
            (30.0, Parallel(Func(self.lawyerToon.clearChat), Sequence(Wait(0.5), Func(self.openEntryDoors)), Func(self.setPos, *endPos), ActorInterval(self, 'Ff_speech', loop=1, duration = 6), LerpPosHprInterval(base.camera, 5.0, Vec3(0, -265, 18), Vec3(180, 7, 0),  Vec3(0, -30, 2), Vec3(180, 10, 0), blendType = 'easeInOut'))),
            (31.0, Func(self.setChatAbsolute, TTLocalizer.LawbotBossIntro8, CFSpeech)),
            (35.0, Func(self.setChatAbsolute, TTLocalizer.LawbotBossIntro9, CFSpeech)),
            (36.0, Sequence(ActorInterval(self, 'Ff_lookRt', duration=3), ActorInterval(self, 'Ff_lookRt', duration=4, startTime=4, endTime=0))),
            (39.0, Func(self.setChatAbsolute, TTLocalizer.LawbotBossIntro10, CFSpeech)),
            (43.0, Parallel(Sequence(ActorInterval(self, 'Ff_speech', loop=1, duration=11), Func(self.loop, 'Ff_neutral')), Func(self.setChatAbsolute, TTLocalizer.LawbotBossIntro11, CFSpeech))),
            (45.0, Parallel(Func(self.toonsToEntryDoor), Func(self.setChatAbsolute, TTLocalizer.LawbotBossIntro12, CFSpeech))),
            (48.0, Parallel(Func(self.clearChat), LerpPosHprInterval(base.camera, 2.0, Vec3(0, -150, 8), Vec3(0, 0, 0), other=self.elevatorModel))),
            (50.0, Func(self.lawyerToon.setChatAbsolute, TTLocalizer.LawbotBossIntro14, CFSpeech)),
            (53.0, Func(self.lawyerToon.setChatAbsolute, TTLocalizer.LawbotBossIntro15, CFSpeech)),
            (55.0, Parallel(Func(self.lawyerToon.clearChat), LerpPosHprInterval(base.camera, 2.0, Vec3(0, -265, 18), Vec3(180, 7, 0), other=self.elevatorModel))),
            (57.0, Sequence(ActorInterval(self, 'Ff_cross_arms_into'), Func(self.loop, 'Ff_cross_arms_loop'))),
            (57.0, Func(self.setChatAbsolute, TTLocalizer.LawbotBossIntro15_1, CFSpeech)),
            (60.5, Parallel(Func(self.clearChat), ActorInterval(self.lawyerToon.suit.specialHead, 'scared_af', loop=1, duration=1.5), Func(base.camera.setPos, Vec3(0, -150, 8)),  Func(base.camera.setHpr, Vec3(0, 0, 0)))),
            (62.0, lawyerLoseSuit),
            (65.0, Parallel(Func(self.lawyerToon.surpriseEyes), Func(self.lawyerToon.setChatAbsolute, TTLocalizer.LawbotBossIntro16, CFSpeech))),
            (67.0, Parallel(Sequence(Wait(4.0), Func(self.closeEntryDoors)), Sequence(Parallel(Func(self.lawyerToon.loop, 'walk'), LerpHprInterval(self.lawyerToon, 2.0, Vec3(180, 0, 0))), Parallel(Func(self.lawyerToon.loop, 'run'), LerpPosInterval(self.lawyerToon, 3.0, Vec3(7, -57, 0), other = self.elevatorModel), toonsSidestep)), Func(self.lawyerToon.setChatAbsolute, TTLocalizer.LawbotBossIntro17, CFSpeech))),
            (69.0, Parallel(Func(self.lawyerToon.clearChat), Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossIntro17_1, CFSpeech))),
            (73.0, Parallel(toonsLoseSuit, bumpyLoseSuit, Func(self.witnessToon.clearChat), Func(self.lawyerToon.hide))),
            (76.0, Parallel(Func(self.setChatAbsolute, TTLocalizer.LawbotBossIntro18, CFSpeech), Sequence(ActorInterval(self, 'Ff_cross_arms_out'), Func(self.loop, 'Ff_neutral')), Func(base.camera.setPos, Vec3(0, -265, 18)), Func(base.camera.setHpr, Vec3(180, 7, 0)))),
            (80.0, Parallel(Func(self.clearChat), panMovie)),
            (90.0, Sequence(LerpFunc(setIntroPlayRate, fromData = 1.0, toData = 0.0, duration = 2.0), Func(base.musicMgr.stopMusic, self.promotionMusic))),
            (92.0, Parallel(Func(self.setChatAbsolute, TTLocalizer.LawbotBossIntro19, CFSpeech), Func(base.camera.setPos, Vec3(0, -265, 18)), Func(base.camera.setHpr, Vec3(180, 7, 0)))),
            (95.0, Parallel(scootBack, Func(self.setChatAbsolute, TTLocalizer.LawbotBossIntro20, CFSpeech))),
            (98.0, Parallel(Func(self.clearChat), LerpPosHprInterval(base.camera, 0.5, Vec3(0, -280, 18), Vec3(0, -20, 0), other=self.elevatorModel))),
            (99.0, Parallel(Func(base.musicMgr.playMusic, self.stingMusic, looping = 1, volume = 0.9), tableFall)),
            (109.0, LerpPosHprInterval(base.camera, 1.0, Vec3(0, -280, 18), Vec3(180, 7, 0), other=self.elevatorModel)),
            (100.5, Sequence(Func(self.specialHead.play, 'Ff_cross_arms_into'), ActorInterval(self, 'Ff_cross_arms_into'), Func(self.specialHead.loop, 'Ff_cross_arms_loop'), Func(self.loop, 'Ff_cross_arms_loop'))),
            (111.5, Func(self.setChatAbsolute, TTLocalizer.LawbotBossIntro21, CFSpeech)),
            (114.5, Func(self.setChatAbsolute, TTLocalizer.LawbotBossIntro22, CFSpeech | CFTimeout)),
            (115.5, Sequence(Func(self.specialHead.play, 'Ff_cross_arms_out'), ActorInterval(self, 'Ff_cross_arms_out'), Func(self.specialHead.loopNeutral), Func(self.loop, 'Ff_neutral'))),
            (116.0, Wait(1)))
        return Sequence(
            Func(self.stickToonsToFloor),
            track,
            Func(self.unstickToons), name=self.uniqueName('Introduction'))

    def walkToonsToBattlePosition(self, toonIds, battleNode):
        ival = Parallel()
        points = BattleBase.BattleBase.toonPoints[len(toonIds) - 1]
        for i in range(len(toonIds)):
            toon = base.cr.doId2do.get(toonIds[i])
            if toon:
                pos, h = points[i]
                # origPos = pos
                # myCurPos = self.getPos()
                bnParent = battleNode.getParent()
                battleNode.wrtReparentTo(render)
                # bnWorldPos = battleNode.getPos()
                battleNode.wrtReparentTo(bnParent)
                pos = render.getRelativePoint(battleNode, pos)
                ival.append(Sequence(Func(toon.setPlayRate, 0.8, 'walk'), Func(toon.loop, 'walk'), toon.posInterval(3, pos), Func(toon.setPlayRate, 1, 'walk'), Func(toon.loop, 'neutral')))

        return ival

    def makeVictoryMovie(self):
        fallSeq = Sequence(Func(self.neck.setHpr, Vec3(0, 180, 0)), Parallel(ActorInterval(self, 'Fb_fall', 0, 0, 5.5, 3.0), SoundInterval(self.deathSfx)))
        firstMoveSeq = self.getBossMoveMovie(BossCogGlobals.LawbotBossBattleFallMiddlePos, Vec3(0, 0, 0), 0, 2.5, doAnimate=False)     # don't do self.doAnimate(None) here
        secondMoveSeq = self.getBossMoveMovie(BossCogGlobals.LawbotBossBattleFallFinalPos, Vec3(0, 0, 0), 0, 5.0, doAnimate=False)     # same as above
        secondMoveSeq.setT(2.5)

        bossTrack = Track(
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
            (3.0, Func(self.setChatAbsolute, TTLocalizer.LawbotBossVictory0, CFSpeech)),
            (3.0, Func(self.toonsLineUpVictory)),
            (6.5, Sequence(Func(self.stopAnimate), Func(self.interruptBossDamageMovie), Func(self.loop, 'Ff_neutral'))),
            (6.5, Func(self.clearChat)),
            (6.5, self.makeTrapdoorShakeMovie(intensity=0.2)),
            (8.5, firstMoveSeq),
            (8.5, LerpPosInterval(base.camera, blendType='easeInOut', duration=2.5, pos=(0, 138.25, -60))),
            (11.0, Func(self.setChatAbsolute, TTLocalizer.LawbotBossVictory1, CFSpeech)),
            (14.5, Func(self.clearChat)),
            (14.5, self.makeTrapdoorShakeMovie(intensity=0.35)),
            (16.5, Func(secondMoveSeq.resume)),
            (16.5, LerpPosInterval(base.camera, blendType='easeInOut', duration=2.5, pos=(0, 101.5, -60))),
            (19.0, Func(self.setChatAbsolute, TTLocalizer.LawbotBossVictory2, CFSpeech)),
            (19.0, Sequence(ActorInterval(self, 'Ff_cross_arms_into'), Func(self.loop, 'Ff_cross_arms_loop'))),
            (22.5, Func(self.clearChat)),
            (22.5, self.makeTrapdoorShakeMovie(intensity=0.5, reparentCLO=False)),
            (24.0, Parallel(Func(base.musicMgr.playMusic, self.killMusic, volume = 0.9), Func(self.openTrapDoor))),
            (25.0, Func(self.setChatAbsolute, TTLocalizer.LawbotBossVictory3, CFSpeech)),
            (25.0, Sequence(ActorInterval(self, 'Ff_cross_arms_out'), Func(self.loop, 'Ff_neutral'))),
            (27.0, Parallel(Func(self.specialHead.play, 'Ff_cross_arms_in'), ActorInterval(self, 'leftlook', duration=1.0))),
            (28.0, Func(self.clearChat)),
            (28.0, fallSeq),
            (28.5, Func(self.setChatAbsolute, TTLocalizer.LawbotBossVictory4, CFSpeech)),
            (31.0, Func(self.closeTrapDoor)),
            (31.5, Func(self.clearChat)),
            (33.0, Func(self.hide))
        )
        return bossTrack

    def makeEpilogueMovie(self):
        epSpeech = TTLocalizer.WitnessToonCongratulations1
        epSpeech = self.__talkAboutPromotion(epSpeech)
        epSpeech += TTLocalizer.WitnessToonCongratulations2
        bossTrack = Sequence(Func(self.witnessToon.setLocalPageChat, epSpeech, 0))
        return bossTrack

    def __hideToons(self):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                toon.hide()

    def __showToons(self):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                toon.show()

    def arrangeToonsAroundWitnessToon(self):
        radius = 7
        numToons = len(self.involvedToons)
        center = (numToons - 1) / 2.0
        for i in range(numToons):
            toon = self.cr.doId2do.get(self.involvedToons[i])
            if toon:
                angle = 90 - 15 * (i - center)
                radians = angle * math.pi / 180.0
                x = math.cos(radians) * radius
                y = math.sin(radians) * radius
                toon.setPos(self.witnessToon, x, y, 0)
                toon.headsUp(self.witnessToon)
                toon.loop('neutral')
                toon.show()

    def __talkAboutPromotion(self, speech):
        if (self.prevCogSuitLevel < ToontownGlobals.MaxCogSuitLevel) or (self.prevCogSuitReviveLevel > -1 and self.prevCogSuitLevel < 49):
            newCogSuitLevel = localAvatar.getCogLevels()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
            newCogSuitType = localAvatar.getCogTypes()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
            if newCogSuitLevel == ToontownGlobals.MaxCogSuitLevel:
                speech += TTLocalizer.WitnessToonLastPromotion % (ToontownGlobals.MaxCogSuitLevel + 1)
            if newCogSuitLevel in ToontownGlobals.CogSuitHPLevels and newCogSuitType != 6:
                speech += TTLocalizer.WitnessToonHPBoost
            if self.prevCogSuitType != 4 and newCogSuitType == 4:
                speech += TTLocalizer.WitnessToonTeleportAccess
        else:
            speech += TTLocalizer.WitnessToonMaxed % (ToontownGlobals.MaxCogSuitLevel + 1)
        numSuesEarned = self.numSuesEarned.get(localAvatar.doId)
        if not numSuesEarned:
            numSuesEarned = TTLocalizer.CeaseDesistsNotFoundVal
        speech += TTLocalizer.WitnessToonCeaseDesistReward % numSuesEarned
        speech = self.handleUniteSpeech(speech)
        return speech

    def stashFurniture(self):
        try:
            self.geom.find('**/g_cogpodiums').stash()
            self.geom.find('**/g_meetingtable').stash()
            self.gavel_zero.stash()
            self.gavel_one.stash()
        except:
            pass

    def __makePrepareBattleTwoMovie(self):
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
            (0.0, Parallel(Sequence(ActorInterval(self, 'Ff_cross_arms_into'), Func(self.loop, 'Ff_cross_arms_loop')), Func(self.setChatAbsolute, TTLocalizer.LawbotBossPrepareTwo0, CFSpeech))),
            (4.0, Func(self.setChatAbsolute, TTLocalizer.LawbotBossPrepareTwo1, CFSpeech)),
            (8.0, Parallel(Sequence(ActorInterval(self, 'Ff_cross_arms_out'), Func(self.loop, 'Ff_neutral')), Func(self.setChatAbsolute, TTLocalizer.LawbotBossPrepareTwo2, CFSpeech))),
            (11.0, Func(self.setChatAbsolute, TTLocalizer.LawbotBossPrepareTwo3, CFSpeech)),
            (12.5, lerpGavelScales),
            (14.0, Parallel(LerpPosHprInterval(base.camera, 0.5, Vec3(0, -175, 50), Vec3(180, -20, 0), Vec3(0, -265, 18), Vec3(180, 7, 0), blendType='easeOut', other=self.elevatorModel), Func(self.setChatAbsolute, TTLocalizer.LawbotBossPrepareTwo4, CFSpeech))),
            (14.6, slamGavels),
            (14.7, tableGavelsSlam),
            (15.2, Func(freakoutCamSeq)),
            (15.2, Func(self.positionToonsInFrontOfCannons)),
            (16.0, LerpPosHprInterval(base.camera, 0.5, Vec3(0, -105, 5), Vec3(0, 0, 0), blendType='easeOut', other=self.elevatorModel)),
            (16.0, Func(self.evidenceBox.pose, 'open', 0.1)),
            (16.5, Func(self.clearChat)),
            (17.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossPrepareTwoBumpy0, CFSpeech | CFTimeout)),
            (21.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossPrepareTwoBumpy0_1, CFSpeech | CFTimeout)),
            (24.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossPrepareTwoBumpy1, CFSpeech | CFTimeout)),
            (26.0, Sequence(Func(self.witnessToon.loop, 'walk'), LerpHprInterval(self.witnessToon, duration=1.0, hpr=(180, 0, 0)), Func(self.witnessToon.loop, 'neutral'), Func(self.evidenceBox.show), self.makeEvidenceBoxAppearTrack(), Func(self.evidenceBox.loop, 'idle'), Func(self.witnessToon.loop, 'walk'), LerpHprInterval(self.witnessToon, duration=1.0, hpr=(0, 0, 0)), Func(self.witnessToon.loop, 'neutral'))),
            (28.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossPrepareTwoBumpy2, CFSpeech | CFTimeout)),
            (32.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossPrepareTwoBumpy2_1, CFSpeech | CFTimeout)),
            (36.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossPrepareTwoBumpy3, CFSpeech | CFTimeout)),
            (36.5, Func(hideFurniture)),
            (40.0, Sequence(Func(base.camera.setPosHpr, self.elevatorModel, 0, -320, 15, 180, -10, 0), Func(self.openBackDoor), Func(self.witnessToon.loop, 'run'), LerpPosInterval(self.witnessToon, duration = 5, pos=(0, 370, 0), startPos=(0, 300, 0)), Func(self.witnessToon.loop, 'neutral'), Func(self.closeBackDoor))),
            (41.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossPrepareTwoBumpy4, CFSpeech)),
            (46.0, Parallel(Func(self.witnessToon.clearChat), showCannonsAppearing)),
            (47.0, Wait(1))
            )
        return movie

    def __makePrepareBattleThreeMovie(self):
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleTwoPosHpr)
        seqOne = Sequence(Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossPrepareThreeBumpy0, CFSpeech), Func(base.camera.setPosHpr, self.elevatorModel, 0, -320, 15, 180, -10, 0), Func(self.openBackDoor), Func(self.witnessToon.loop, 'run'), Func(self.witnessToon.setH, 180), LerpPosInterval(self.witnessToon, duration = 3, pos=(0, 330, 0), startPos=(0, 370, 0)), Func(self.closeBackDoor), Func(self.witnessToon.clearChat), Wait(2))
        seqTwo = Sequence(Func(base.camera.setPosHpr, self.elevatorModel, 10, -200, 25, 135, -10, 0), Func(self.setChatAbsolute, TTLocalizer.LawbotBossPrepareThree0, CFSpeech), LerpPosInterval(self.witnessToon, duration=6.0, pos=(30, 150, 0), startPos=(30, 270, 0)))

        trackOne = Track(
            (0.0, Func(base.camLens.setMinFov, 60)),
            (0.0, seqOne),
            (0.0, Sequence(Func(self.stopAnimate), Func(self.interruptBossDamageMovie), Func(self.loop, 'Ff_neutral'))),
            (2.0, Func(self.toonsLineUpBattleThree)),
            (5.0, seqTwo),
            (6.0, LerpPosHprInterval(base.camera, duration=8.0, other=self.elevatorModel, pos=(30, -240, 25), hpr=(25, -10, 0))),
            (6.0, Sequence(ActorInterval(self, 'leftlook', playRate=0.5), ActorInterval(self, 'Ff_cross_arms_into'), Func(self.loop, 'Ff_cross_arms'))),
            (9.0, Func(self.setChatAbsolute, TTLocalizer.LawbotBossPrepareThree1, CFSpeech)),
            (10.5, Sequence(Func(self.witnessToon.setH, 150), LerpPosInterval(self.witnessToon, duration=3.5, pos=(0, 85, 0)), Func(self.witnessToon.loop, 'walk'), LerpHprInterval(self.witnessToon, duration=1.0, hpr=(0, 0, 0)), Func(self.witnessToon.loop, 'neutral'))),
            (13.0, Func(self.clearChat)),
            (14.0, LerpPosHprInterval(base.camera, 0.5, Vec3(0, -105, 5), Vec3(0, 0, 0), blendType='easeOut', other=self.elevatorModel)),
            (14.5, Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossPrepareThreeBumpy1, CFSpeech)),
            (17.0, Func(self.witnessToon.clearChat)),
            (17.0, LerpPosHprInterval(base.camera, 0.25, Vec3(0, -175, 30), Vec3(180, -20, 0), Vec3(0, -200, 18), Vec3(180, 7, 0), blendType='easeOut', other=self.elevatorModel)),
            (17.0, Func(self.setChatAbsolute, TTLocalizer.LawbotBossPrepareThree2, CFSpeech)),
            (17.0, ActorInterval(self, 'Ff_speech', loop=1, duration=3.0)),
            (17.0, Sequence(Func(base.musicMgr.stopMusic, self.battleTwoMusic), Func(base.musicMgr.playMusic, self.battleThreeMusic, looping=1, volume=0.9))),
            (20.0, Func(self.setChatAbsolute, TTLocalizer.LawbotBossPrepareThree3, CFSpeech)),
            (20.0, Func(self.loop, 'Ff_neutral')),
            (23.0, LerpPosHprInterval(base.camera, blendType='easeOut', other=self.elevatorModel, duration=1.0, pos=(0, -200, 30), hpr=(0, 10, 0))),
            (24.0, Func(self.clearChat))
        )

        movie = Sequence(trackOne)
        if self.battleA:
            movie.append(Wait(0.5))
            movie.append(Func(self.showCogRoundSpotlight, 0))
            movie.append(Func(base.playSfx, self.spotlightOnSfx))
        if self.battleB:
            movie.append(Wait(0.5))
            movie.append(Func(self.showCogRoundSpotlight, 1))
            movie.append(Func(base.playSfx, self.spotlightOnSfx))

        return movie

    def __makePrepareBattleFourMovie(self):
        movie = Track(
            (0.0, Func(base.camLens.setMinFov, 60)),
            (0.0, Func(self.setChatAbsolute, TTLocalizer.LawbotBossPrepareFour0, CFSpeech)),
            (3.0, Func(self.setChatAbsolute, TTLocalizer.LawbotBossPrepareFour1, CFSpeech)),
            (6.0, Func(self.setChatAbsolute, TTLocalizer.LawbotBossPrepareFour2, CFSpeech | CFTimeout)),
            (6.0, Sequence(ActorInterval(self, 'Ff_cross_arms_into'), Func(self.loop, 'Ff_cross_arms_loop'))),
            (6.0, Func(self.toonsLineUpBattleFour)),
            (10.0, Func(self.clearChat)),
            (10.0, LerpPosHprInterval(base.camera, 0.5, Vec3(0, -105, 5), Vec3(0, 0, 0), blendType='easeOut', other=self.elevatorModel)),
            (11.0, Parallel(Func(self.witnessToon.sadEyes), Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossPrepareFourBumpy0, CFSpeech | CFTimeout))),
            (15.0, Parallel(Func(self.witnessToon.normalEyes), Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossPrepareFourBumpy1, CFSpeech | CFTimeout))),
            (19.0, Func(self.witnessToon.setChatAbsolute,  TTLocalizer.LawbotBossPrepareFourBumpy2, CFSpeech | CFTimeout)),
            (23.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossPrepareFourBumpy3 % base.PRIMARY_KEY.upper(), CFSpeech | CFTimeout)),
            (27.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossPrepareFourBumpy4 % base.SECONDARY_KEY.upper(), CFSpeech | CFTimeout)),
            (31.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossPrepareFourBumpy5, CFSpeech | CFTimeout)),
            (35.0, Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossPrepareFourBumpy6, CFSpeech | CFTimeout)),
            (39.0, Sequence(Func(self.witnessToon.setChatAbsolute, TTLocalizer.LawbotBossPrepareFourBumpy7, CFSpeech | CFTimeout), Func(self.loop, 'Ff_neutral'), Wait(4)))
        )
        return movie

    def toonDied(self, avId):
        ClashBossCog.ClashBossCog.toonDied(self, avId)

        # If our toon died, get rid of the dept exp bar
        if avId == base.localAvatar.doId:
            if self.departmentExpBar:
                self.departmentExpBar.hide()
                self.departmentExpBar.stop()
                self.departmentExpBar.destroy()
            base.cr.gameGui.expBar.show()

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
        elif attackCode == BossCogGlobals.BossCogBookDirectedAttack:
            self.setDizzy(0)
            self.doDirectedAttack(avId, attackCode)
        elif attackCode == BossCogGlobals.BossCogFourWayTornadoAreaAttack:
            self.setDizzy(0)
            base.playSfx(self.warningSfx)
            base.localAvatar.doBossTornadoIndicator()
            self.doTornadoAreaAttack()
        elif attackCode == BossCogGlobals.BossCogNoAttack:
            self.setDizzy(0)
            self.doAnimate(None, raised=1)

    def setMaxHp(self, hp):
        self.bossMaxDamage = hp
        self.healthGui.setMaxHp(hp)
        messenger.send(ConditionGlobals.RefreshMsg)

    def getCurTurnSpeed(self):
        result = (BossCogGlobals.BossbotTurnSpeedMax - (
                    BossCogGlobals.BossbotTurnSpeedMax - BossCogGlobals.BossbotTurnSpeedMin)) * self.getDesperationSpeedMult()
        return result

    def getCurRollSpeed(self):
        result = (BossCogGlobals.BossbotRollSpeedMax - (
                    BossCogGlobals.BossbotRollSpeedMax - BossCogGlobals.BossbotRollSpeedMin)) * self.getDesperationSpeedMult()
        return result

    def getCurTreadSpeed(self):
        result = (BossCogGlobals.BossbotTreadSpeedMax - (
                    BossCogGlobals.BossbotTreadSpeedMax - BossCogGlobals.BossbotTreadSpeedMin)) * self.getDesperationSpeedMult()
        return result

    def getDesperationSpeedMult(self):
        if self.state == 'BattleFour':
            if self.desperationState == 1:
                return 3.0
            elif self.desperationState == 0:
                return 2.4
            else:
                return 2.0
        return 1.0

    def getTornado(self):
        tornadoRoot = NodePath('tornadoRoot')
        tornado = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_cfg_whirlwind').find('**/whirlwind')
        tornado.reparentTo(tornadoRoot)
        tornado.setPos(0, 1, 0)
        tornado.setDepthWrite(0)
        tornado.setBin('transparent', 50)
        ct = CollisionTube(0, 0, 0, 0, 0, 75, 4)
        ct.setTangible(0)
        cn = CollisionNode('BossZap')
        cn.addSolid(ct)
        cn.setCollideMask(ToontownGlobals.WallBitmask)
        cnp = tornado.attachNewNode(cn)
        cnp.setTag('attackCode', str(BossCogGlobals.BossCogFourWayTornadoAreaAttack))
        tornadoRoot.setColorScale(1, 1, 1, 0)
        tornadoRoot.setPos(0, 0, BossCogGlobals.LawbotBossTornadoPosZ)
        tornadoRoot.setScale(0.6)
        tornadoRoot.hide()
        return tornadoRoot

    def doTornadoAreaAttack(self):
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
        indicatorPosHprs = ((16, 16, 0.035, -45, -90, 0),
                            (-16, 16, 0.035, 45, -90, 0),
                            (16, -16, 0.035, -135, -90, 0),
                            (-16, -16, 0.035, 135, -90, 0))
        for i in range(len(list(BossCogGlobals.LawbotBossTornadoIndex2PosTravel.keys()))):
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

        tornadoNodeList = getTornadoFinalPosNodes(BossCogGlobals.LawbotBossTornadoIndex2PosTravel)
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

    def doMoveAttack(self, toonId, turnTime, rollTime, x, y, h):
        self.attackCode = BossCogGlobals.BossCogMoveAttack
        self.attackAvId = toonId
        self.setDizzy(0)
        toon = base.cr.doId2do.get(toonId)
        if toon:
            toPos = Point3(x, y, -71.601)
            toHpr = VBase3(h, 0, 0)
            self.doAnimate(None, raised=1)
            if self.moveTrack and self.moveTrack.isPlaying():
                self.moveTrack.finish()
                self.moveTrack = None
            self.moveTrack = self.getBossMoveMovie(toPos, toHpr, turnTime, rollTime)
            self.moveTrack.start()
            self.storeInterval(self.moveTrack, "moveTrack")

    def resetBossDamageMovie(self, hits, maxHits, turnTime, rollTime, x, y, h):
        toPos = Point3(x, y, -71.601)
        toHpr = VBase3(h, 0, 0)
        self.bossDamageMovie = Sequence()
        self.bossDamageMovie.append(Func(self.loop, 'Ff_neutral'))
        track = self.getBossMoveMovie(toPos, toHpr, turnTime, rollTime, True)
        self.bossDamageMovie.append(track)
        self.bossDamageToMovie = self.bossDamageMovie.getDuration() / maxHits
        self.bossDamageMovie.setT(hits * self.bossDamageToMovie)

    def updateBossDamageMovie(self, hits, maxHits):
        if self.dizzy:
            self.specialHead.play('hit')
            self.doAnimate('hit', now=1)
        if hits >= maxHits:
            self.bossDamageMovie.resumeUntil(self.bossDamageMovie.getDuration())
        else:
            self.bossDamageMovie.resumeUntil(hits * self.bossDamageToMovie)

    def getBossMoveMovie(self, toPos, toHpr, turnTime, rollTime, reverse=False, doAnimate=True):
        fromPos = self.getPos()
        currentTreadSpeed = self.getCurTreadSpeed()

        if toHpr[0] < self.getH():
            turnRate = currentTreadSpeed
        else:
            turnRate = -currentTreadSpeed

        deltaPos = toPos - fromPos

        if reverse:
            rollTreadRate = -currentTreadSpeed
        else:
            rollTreadRate = currentTreadSpeed

        bossMoveMovie = Sequence(
            Func(self.setPos, fromPos),
            Func(self.headsUp, toPos),
            Parallel(
                self.hprInterval(turnTime, toHpr, self.getHpr()),
                self.rollLeftTreads(turnTime, turnRate),
                self.rollRightTreads(turnTime, -turnRate)
            ),
            Parallel(
                LerpFunctionInterval(self.rollBoss, duration=rollTime, extraArgs=[fromPos, deltaPos]),
                self.rollLeftTreads(rollTime, rollTreadRate),
                self.rollRightTreads(rollTime, rollTreadRate)
            )
        )
        if doAnimate:
            bossMoveMovie = Sequence(Func(self.doAnimate, None, now=1), bossMoveMovie)

        return bossMoveMovie

    def stopMoveTask(self, x, y, h, stopMove=False):
        if stopMove and (self.moveTrack and self.moveTrack.isPlaying()):
            self.moveTrack.pause()
            self.moveTrack = None
        else:
            self.setX(x)
            self.setY(y)
            self.setH(h)

    '''
    Local object functions

    All of the functions below are used to initialize or manipulate local objects in the fight.

    These objects are not networked, so they should not be treated as such.
    '''

    def makeWitnessToon(self):
        self.witnessToon = NPCToons.createLocalNPC(2009)
        state = random.getstate()
        random.seed(self.doId)
        self.witnessToon.suitType = SuitDNA.getRandomSuitByDept('l')
        self.witnessToon.initializeBodyCollisions('toon')
        self.witnessToon.addActive()
        self.witnessToon.setName(TTLocalizer.WitnessToonName)
        self.witnessToon.setDisplayName(TTLocalizer.WitnessToonName)
        self.witnessToon.setPickable(0)
        self.witnessToon.setPlayerType(NametagGroup.CCNonPlayer)
        self.witnessToon.setPosHpr(*BossCogGlobals.LawbotBossWitnessToonPosHpr)
        random.setstate(state)

    def __cleanupWitnessToon(self):
        self.hideWitnessToon()
        if self.witnessToon:
            self.witnessToon.removeActive()
            self.witnessToon.delete()
            self.witnessToon = None

    def showWitnessToon(self):
        if not self.witnessToonOnstage:
            self.witnessToon.addActive()
            self.witnessToon.reparentTo(self.geom)
            self.witnessToonOnstage = 1

    def hideWitnessToon(self):
        if self.witnessToonOnstage:
            self.witnessToon.removeActive()
            self.witnessToon.detachNode()
            self.witnessToonOnstage = 0

    def makeLawyerToon(self):
        self.lawyerToon = NPCToons.createLocalNPC(12050)
        self.lawyerToon.suitType = 'bf'
        self.lawyerToon.addActive()
        self.lawyerToon.setName(TTLocalizer.LawyerToonName)
        self.lawyerToon.setDisplayName(TTLocalizer.LawyerToonName)
        self.lawyerToon.setPickable(0)
        self.lawyerToon.setPlayerType(NametagGroup.CCNonPlayer)
        self.lawyerToon.setPosHpr(*BossCogGlobals.LawbotBossLawyerToonPosHpr)

    def __cleanupLawyerToon(self):
        self.hideWitnessToon()
        if self.lawyerToon:
            self.lawyerToon.removeActive()
            self.lawyerToon.delete()
            self.lawyerToon = None

    def showLawyerToon(self):
        if not self.lawyerToonOnstage:
            self.lawyerToon.addActive()
            self.lawyerToon.reparentTo(self.geom)
            self.lawyerToonOnstage = 1

    def hideLawyerToon(self):
        if self.lawyerToonOnstage:
            self.lawyerToon.removeActive()
            self.lawyerToon.detachNode()
            self.lawyerToonOnstage = 0

    def makeExecutiveMembers(self):
        if len(self.executiveMembers) > 0: # Exe cogs are already made
            return
        for i in range(8):
            suit = Suit.Suit()
            dna = SuitDNA.SuitDNA()
            dna.newSuit(SuitDNA.suitHeadTypes[16 + i])
            suit.setDNA(dna)
            suit.addActive()
            suit.makeExecutive()
            suit.reparentTo(render)
            suit.loop('sit')
            suit.setPosHpr(*BossCogGlobals.LawbotBossExecutivePositions[i])
            suit.setPickable(0)
            suit.setDisplayName(TTLocalizer.SuitBaseNameWithLevel % {'name': suit.getName(), 'dept': TTLocalizer.Lawbot, 'level': str(i + 5) + TTLocalizer.AvatarSuitPanelExecutive})
            self.executiveMembers.append(suit)

    def cleanupExecutiveMembers(self):
        if len(self.executiveMembers) == 0: # Exe cogs are already cleaned up
            return
        for suit in self.executiveMembers:
            suit.delete()
        self.executiveMembers = []

    '''
    Cutscene Functions

    These functions are entirely used for creating parts of cutscenes.
    '''

    def makeExecutivePanMovie(self):
        talkTrack = Sequence()
        for i in range(len(self.executiveMembers)):
            if i in [2, 4, 7]:
                suit = self.executiveMembers[len(self.executiveMembers) - (i + 1)]
                talkTrack.append(Sequence(Func(suit.setChatAbsolute, TTLocalizer.LawbotBossExecutiveSuggestions[i], CFSpeech)))
                talkTrack.append(Wait(4))
                talkTrack.append(Func(suit.clearChat))
                talkTrack.append(Wait(1))

        camTrack = Sequence(Func(base.camera.setHpr, 90, -20, 0), Func(base.camera.setPos, Vec3(0, -242, 15)), Wait(4), LerpHprInterval(base.camera, 1.0, Vec3(-90, -20, 0),  blendType='easeInOut'), Wait(4), LerpPosInterval(base.camera, 1.0, Vec3(0, -176, 15), blendType='easeInOut'))
        return Parallel(camTrack, talkTrack)

    def makeTableFallMovie(self):
        suitsReact = Parallel()
        fallDistance = 100
        i = 0
        for suit in self.executiveMembers:
            i += 1
            suitsReact.append(Sequence(Wait(1), ActorInterval(suit, 'flail', 0, 0, 2.0, 1.1, 0.7), Parallel(ActorInterval(suit, 'flail', 0, 0, 1.0, 1.0, 2.0), LerpPosInterval(suit, 1.0, Vec3(suit.getX(), suit.getY(), suit.getZ() - fallDistance), blendType = 'easeIn'))))

        table = self.geom.find("**/table")
        paper = self.geom.find("**/paper")
        tableFall = Sequence(
            Func(self.openTrapDoor),
            Wait(1),
            Func(base.playSfx, self.fallingSfx),
            LerpPosInterval(table, 1.0, Vec3(0, -220.292, -fallDistance),
            Vec3(0, -220.292, 0), blendType = 'easeIn'),
            Wait(1),
            Func(base.playSfx, self.fallingSfx),
            LerpPosInterval(paper, 1.0, Vec3(0, -220.292, -fallDistance),
            Vec3(0, -220.292, 0), blendType = 'easeIn'),
            Func(self.cleanupExecutiveMembers),
            Func(self.closeTrapDoor),
            Wait(1.5),
            LerpPosInterval(table, 1.0, Vec3(0, -220.292, 0), Vec3(0, -220.292, fallDistance), blendType = 'easeIn'),
            Func(base.playSfx, self.tableLandSfx),
            LerpPosInterval(paper, 1.0, Vec3(0, -220.292, 0), Vec3(0, -220.292, fallDistance), blendType = 'easeIn'),
            Func(base.playSfx, self.papersLandSfx)
        )
        gavelsFall = Sequence(
            Wait(1),
            Parallel(
                LerpPosInterval(self.gavel_zero, 1.0, Vec3(-27.0428, 44.9754, -fallDistance)),
                LerpPosInterval(self.gavel_one, 1.0, Vec3(27.0428, 44.9754, -fallDistance))
            ),
            Wait(3.5),
            Parallel(
                LerpPosInterval(self.gavel_zero, 1.0, Vec3(-27.0428, 44.9754, 8.96013), Vec3(-27.0428, 44.9754, fallDistance)),
                LerpPosInterval(self.gavel_one, 1.0, Vec3(27.0428, 44.9754, 8.96013), Vec3(27.0428, 44.9754, fallDistance))
            )
        )
        return Parallel(tableFall, suitsReact, gavelsFall)

    def makeGavelSlamMovie(self):
        gavelZeroTrack = Sequence(Func(self.gavel_zero.wrtReparentTo, self.gavelZeroRotateNode), LerpHprInterval(self.gavelZeroRotateNode, blendType='easeIn', duration=0.25, hpr=Vec3(0, 0, 80), startHpr=Vec3(0, 0, 0)), LerpHprInterval(self.gavelZeroRotateNode, duration=1, hpr=Vec3(0, 0, 0)), Func(self.gavel_zero.wrtReparentTo, render))
        gavelOneTrack = Sequence(Func(self.gavel_one.wrtReparentTo, self.gavelOneRotateNode), LerpHprInterval(self.gavelOneRotateNode, blendType='easeIn', duration=0.25, hpr=Vec3(0, 0, -80), startHpr=Vec3(0, 0, 0)), LerpHprInterval(self.gavelOneRotateNode, duration=1, hpr=Vec3(0, 0, 0)), Func(self.gavel_one.wrtReparentTo, render))
        return Sequence(Wait(0.25), Parallel(gavelZeroTrack, gavelOneTrack))

    def makeTrapdoorShakeMovie(self, amountOfShakes=12, duration=1.5, intensity=0.5, reparentCLO=True):
        trapdoorShakes = Sequence()
        timePerShake = duration / amountOfShakes
        trapdoorShakes.append(Func(self.trapdoorRotateNode.setHpr, Vec3(0, 0, 0)))
        if reparentCLO:
            trapdoorShakes.append(Func(self.wrtReparentTo, self.trapdoorRotateNode))
        for x in range(amountOfShakes):
            trapdoorShakes.append(LerpHprInterval(self.trapdoorRotateNode, blendType='easeOut', duration=timePerShake/4, hpr=(0, 0, intensity)))
            trapdoorShakes.append(LerpHprInterval(self.trapdoorRotateNode, blendType='easeOut', duration=timePerShake/2, hpr=(0, 0, -intensity)))
            trapdoorShakes.append(LerpHprInterval(self.trapdoorRotateNode, blendType='easeOut', duration=timePerShake/4, hpr=(0, 0, 0)))
        if reparentCLO:
            trapdoorShakes.append(Func(self.wrtReparentTo, render))
        return trapdoorShakes

    def makeEvidenceBoxAppearTrack(self):
        self.evidenceBox.setScale(0.1)
        boxTrack = Parallel(
            Sequence(
                ActorInterval(self.witnessToon, 'feedPet'),
                Func(self.witnessToon.loop, 'neutral')
            ),
            Sequence(
                Func(self.evidenceBox.reparentTo, self.witnessToon.rightHand),
                Func(self.evidenceBox.setPos, Vec3(0, 0, 0)),
                Wait(2.1),
                Func(self.evidenceBox.wrtReparentTo, self.geom),
                Func(self.evidenceBox.setShear, 0, 0, 0),
                Parallel(
                    LerpHprInterval(self.evidenceBox, hpr=(180, 0, 0), duration=1.2),
                    ProjectileInterval(self.evidenceBox, endPos=BossCogGlobals.LawbotBossEvidenceBoxPos, duration=1.2, gravityMult=0.45)
                ),
                Wait(0.2),
                Sequence(
                    Parallel(
                        ActorInterval(self.evidenceBox, 'open'),
                        Sequence(
                            Wait(0.4),
                            Func(base.playSfx, self.evidenceBoxOpenSfx, node=self.evidenceBox)
                        ),
                        Sequence(
                            LerpScaleInterval(self.evidenceBox, scale=Point3(1.35, 1.35, 0.1), duration=0.2),
                            LerpScaleInterval(self.evidenceBox, scale=Point3(1.15, 1.15, 0.1), duration=0.1),
                            LerpScaleInterval(self.evidenceBox, scale=Point3(1.25, 1.25, 0.1), duration=0.1),
                            LerpScaleInterval(self.evidenceBox, scale=Point3(1.25, 1.25, 1.35), duration=0.2),
                            LerpScaleInterval(self.evidenceBox, scale=Point3(1.25, 1.25, 1.15), duration=0.1),
                            LerpScaleInterval(self.evidenceBox, scale=Point3(1.25, 1.25, 1.25), duration=0.1)
                        )
                    )
                )
            )
        )
        return boxTrack

    '''
    Toon positioning Functions

    All of the functions below are used to position toons into predefined locations around the room.

    Used almost exclusively for cutscenes.
    '''

    def toonsToEntryDoor(self, includeNpcs = 1):
        i = 0
        startingX = -2 * (len(self.involvedToons) - 1)
        for toonId in self.involvedToons:
            toon = base.cr.doId2do.get(toonId)
            if toon:
                toon.setPosHpr(self.elevatorModel, startingX + (i * 4), -120, 0, 180, 0, 0)
                i += 1
        if includeNpcs:
            self.witnessToon.setPosHpr(self.elevatorModel, -7, -127, 0, 180, 0, 0)
            self.lawyerToon.setPosHpr(self.elevatorModel, 7, -127, 0, 180, 0, 0)

    def toonsDodgeLawyerToon(self):
        numOfToons = len(self.involvedToons)
        jumpTracks = Parallel()
        if numOfToons < 4:
            return jumpTracks
        sidestepSound = base.loader.loadSfx('phase_5/audio/sfx/ENC_cogjump_to_side.ogg')
        i = 1
        if numOfToons == 4:
            for toonId in self.involvedToons:
                toon = base.cr.doId2do.get(toonId)
                if toon and toon.isDisguised:
                    jumpTracks.append(Sequence(Parallel(SoundInterval(sidestepSound, node=toon.suit, volume=0.6), ActorInterval(toon.suit, 'sidestep-right')), Func(toon.suit.loop, 'neutral')))
                    i += 1
        elif numOfToons == 5 or numOfToons == 6:
            for toonId in self.involvedToons:
                toon = base.cr.doId2do.get(toonId)
                if toon and toon.isDisguised:
                    if i > numOfToons - 1:
                        jumpTracks.append(Sequence(Parallel(SoundInterval(sidestepSound, node=toon.suit, volume=0.6), ActorInterval(toon.suit, 'sidestep-left')), Func(toon.suit.loop, 'neutral')))
                    else:
                        jumpTracks.append(Sequence(Parallel(SoundInterval(sidestepSound, node=toon.suit, volume=0.6), ActorInterval(toon.suit, 'sidestep-right')), Func(toon.suit.loop, 'neutral')))
                    i += 1
        else:
            for toonId in self.involvedToons:
                toon = base.cr.doId2do.get(toonId)
                if toon and toon.isDisguised:
                    if i > numOfToons - 2:
                        jumpTracks.append(Sequence(Parallel(SoundInterval(sidestepSound, node=toon.suit, volume=0.6), ActorInterval(toon.suit, 'sidestep-left')), Func(toon.suit.loop, 'neutral')))
                    else:
                        jumpTracks.append(Sequence(Parallel(SoundInterval(sidestepSound, node=toon.suit, volume=0.6), ActorInterval(toon.suit, 'sidestep-right')), Func(toon.suit.loop, 'neutral')))
                    i += 1
        return jumpTracks

    def toonsLineUpBattleThree(self):
        i = 0
        startingX = -2 * (len(self.involvedToons) - 1)
        for toonId in self.involvedToons:
            toon = base.cr.doId2do.get(toonId)
            if toon:
                toon.setGeomNodeH(0)
                toon.setPosHpr(startingX + (i * 4), 200, -71.5765, 0, 0, 0)
                toon.loop('neutral')
                i += 1

    def toonsLineUpBattleFour(self):
        i = 0
        startingX = -2 * (len(self.involvedToons) - 1)
        for toonId in self.involvedToons:
            toon = base.cr.doId2do.get(toonId)
            if toon:
                toon.setGeomNodeH(0)
                toon.setPosHpr(startingX + (i * 4), 130, -71.5765, 180, 0, 0)
                toon.loop('neutral')
                i += 1

    def toonsLineUpVictory(self):
        i = 0
        startingX = -2 * (len(self.involvedToons) - 1)
        for toonId in self.involvedToons:
            toon = base.cr.doId2do.get(toonId)
            if toon:
                toon.setGeomNodeH(0)
                toon.setPosHpr(self.elevatorModel, startingX + (i * 4), -130, 0, 180, 0, 0)
                toon.loop('neutral')
                i += 1

    '''
    Room Manipulation Functions

    All of the functions below are used to manipulate parts of the CLO boss room for
    cutscene use, battle use, or whatever else you may need.

    Any intended manipulatable part should be done through this rather than attempting
    to recreate it in the code
    '''

    def openPainting(self, paintingIdx, animated = 1, finalBattle = 0):
        painting = self.geom.find("**/painting_%s" % paintingIdx)
        openPos = BossCogGlobals.LawbotBossPaintingOpenPositions[paintingIdx]
        if animated:
            # Recess painting back first, the slide up
            node = painting if finalBattle else base.localAvatar
            volume = 0.8 if finalBattle else 0.45
            paintingSfx = loader.loadSfx('phase_11/audio/sfx/LB_painting_moves.ogg')
            paintingSfxIval = SoundInterval(paintingSfx, node=node, volume=volume)
            paintingIval = Sequence(Func(paintingSfxIval.loop), LerpPosInterval(painting, self.paintingOpenTime / 1.25, Vec3(openPos[0] * 1.75, openPos[1] * 1.75, 0)), Func(paintingSfxIval.finish))
            paintingIval.start()
        else:
            painting.setPos(*openPos)

    def closePainting(self, paintingIdx, animated = 1, finalBattle = 0):
        painting = self.geom.find("**/painting_%s" % paintingIdx)
        # openPos = BossCogGlobals.LawbotBossPaintingOpenPositions[paintingIdx]
        if animated:
            # Slide painting down, then bring forward
            node = painting if finalBattle else base.localAvatar
            volume = 0.8 if finalBattle else 0.45
            paintingSfx = loader.loadSfx('phase_11/audio/sfx/LB_painting_moves.ogg')
            paintingSfxIval = SoundInterval(paintingSfx, node=node, volume=volume)
            paintingIval = Sequence(Func(paintingSfxIval.loop), LerpPosInterval(painting, self.paintingOpenTime, Vec3(0, 0, 0)), Func(paintingSfxIval.finish))
            paintingIval.start()
        else:
            painting.setPos(0, 0, 0)

    def openEntryDoors(self, animated = 1):
        doorR = self.geom.find("**/door_entry_R")
        doorL = self.geom.find("**/door_entry_L")
        if animated:
            # Doors swing to H 100 to make them appear open wider, more natural look. EaseInOut makes the doors look a little less rigid
            # Doors open in 2.0 seconds so that they actually have time to blend
            doorSfx = loader.loadSfx('phase_11/audio/sfx/LB_door_moves.ogg')
            seq = Parallel(SoundInterval(doorSfx, volume=0.6), LerpHprInterval(doorR, 2.0, Vec3(-100, 0, 0), Vec3(0, 0, 0), blendType = 'easeInOut'), LerpHprInterval(doorL, 2.0, Vec3(100, 0, 0), Vec3(0, 0, 0), blendType = 'easeInOut'))
            seq.start()
        else:
            # FBI OPEN UP
            doorR.setH(-100)
            doorL.setH(100)

    def closeEntryDoors(self, animated = 1):
        doorR = self.geom.find("**/door_entry_R")
        doorL = self.geom.find("**/door_entry_L")
        if animated:
            # Doors start from H 100, more natural look. EaseInOut makes the doors look a little less rigid
            # Doors close in 2.0 seconds so that they actually have time to blend
            doorSfx = loader.loadSfx('phase_11/audio/sfx/LB_door_moves.ogg')
            seq = Parallel(SoundInterval(doorSfx, volume=0.6), LerpHprInterval(doorR, 2.0, Vec3(0, 0, 0), Vec3(-100, 0, 0), blendType = 'easeInOut'), LerpHprInterval(doorL, 2.0, Vec3(0, 0, 0), Vec3(100, 0, 0), blendType = 'easeInOut'))
            seq.start()
        else:
            # Defaults the doors to their regular state
            doorR.setH(0)
            doorL.setH(0)

    def openBackDoor(self, animated = 1):
        backDoor = self.geom.find("**/backdoor")
        if animated:
            # Back door swings open to -110 H to make it more dramatic.
            doorSfx = loader.loadSfx('phase_11/audio/sfx/LB_door_moves.ogg')
            seq = Parallel(SoundInterval(doorSfx, volume=0.6), LerpHprInterval(backDoor, 2.0, Vec3(-110, 0, 0), Vec3(0, 0, 0), blendType = 'easeInOut'))
            seq.start()
        else:
            backDoor.setH(-110)

    def closeBackDoor(self, animated = 1):
        backDoor = self.geom.find("**/backdoor")
        if animated:
            # Back door swings from -110 H to make it more dramatic.
            doorSfx = loader.loadSfx('phase_11/audio/sfx/LB_door_moves.ogg')
            seq = Parallel(SoundInterval(doorSfx, volume=0.6), LerpHprInterval(backDoor, 2.0, Vec3(0, 0, 0), Vec3(-110, 0, 0), blendType = 'easeInOut'))
            seq.start()
        else:
            backDoor.setH(0)

    def openTrapDoor(self, animated = 1):
        if animated:
            # Mid trapdoor opens by hinge, small bounce
            trapdoorSfx = loader.loadSfx('phase_11/audio/sfx/LB_trapdoor_open.ogg')
            seq = Parallel(
                SoundInterval(trapdoorSfx),
                LerpHprInterval(self.trapdoorRotateNode, 0.45, Vec3(0, 0, 90), Vec3(0, 0, 0), blendType = 'easeIn'),
            )
            seq.start()
        else:
            self.trapdoorRotateNode.setR(90)

    def closeTrapDoor(self, animated = 1):
        if animated:
            # Mid trapdoors closes by hinge, no bounce
            trapdoorSfx = loader.loadSfx('phase_11/audio/sfx/LB_trapdoor_close.ogg')
            seq = Parallel(
                SoundInterval(trapdoorSfx),
                LerpHprInterval(self.trapdoorRotateNode, 2.0, Vec3(0, 0, 0), Vec3(0, 0, 90), blendType = 'easeInOut'),
            )
            seq.start()
        else:
            self.trapdoorRotateNode.setR(0)

    @property
    def uniteResistanceToon(self):
        return self.witnessToon

    def handleDefenseSpecialistSpawn(self, task=None):
        if self.defenseSpecialistsRotateNode is None:
            self.defenseSpecialistsRotateNode = self.attachNewNode('defenseSpecialistsRotateNode')
            self.defenseSpecialistsRotateNode.setPos(0, 0, 5)
            self.defenseSpecialistsRotateNodeLoop = LerpHprInterval(self.defenseSpecialistsRotateNode, 5.0, (0, 0, 0), (360, 0, 0))
            self.defenseSpecialistsRotateNodeLoop.loop()
        if len(self.defenseSpecialists) > 0:
            for suit in self.defenseSpecialists:
                suit.reparentTo(self.defenseSpecialistsRotateNode)
        else:
            taskName = self.uniqueName('RetryDefenseSpecialistSpawn')
            taskMgr.remove(taskName)
            taskMgr.doMethodLater(1.0, self.handleDefenseSpecialistSpawn, taskName)
