from direct.directutil import Mopath
from direct.distributed.ClockDelta import *
from direct.fsm import FSM
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.task import Task
import math

from toontown.gui.game.condition import ConditionGlobals
from toontown.clashsuit.suit import BossCogGlobals
from toontown.clashsuit.suit import DistributedBossCog
from toontown.clashsuit.suit import DistributedSuitBase
from toontown.clashsuit.suit import SuitDNA, Suit
from toontown.clashbattle.battle import BattleBase
from toontown.clashbattle.battle import MovieToonVictory
from toontown.clashbattle.battle import RewardPanel
from toontown.clashbattle.battle.BattleProps import *
from toontown.building import ElevatorConstants
from toontown.building import ElevatorUtils
from toontown.coghq import CogDisguiseGlobals
from toontown.distributed import DelayDelete
from otp import *
from toontown.nametag import NametagGlobals
from toontown.nametag.NametagConstants import CFSpeech, CFTimeout
from toontown.toon.npc import NPCToons
from toontown.toonbase import TTLocalizer
# from toontown.toonbase import BattleGlobals
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownTimer
from toontown.gui import DepartmentExperienceBar
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

OneBossCog = None


@DirectNotifyCategory()
class DistributedBoardbotBoss(DistributedBossCog.DistributedBossCog, FSM.FSM):

    debugPositions = False

    def __init__(self, cr):
        self.notify.debug('----- __init___')
        DistributedBossCog.DistributedBossCog.__init__(self, cr)
        FSM.FSM.__init__(self, 'DistributedBoardbotBoss')
        self.lawyers = []
        self.lawyerRequest = None
        self.bossDamage = 0
        self.attackCode = None
        self.attackAvId = 0
        self.recoverRate = 0
        self.recoverStartTime = 0
        self.bossDamageMovie = None
        self.everThrownPie = 0
        self.battleThreeMusicTime = 0
        self.insidesANodePath = None
        self.insidesBNodePath = None
        self.strafeInterval = None
        self.onscreenMessage = None
        self.bossMaxDamage = BossCogGlobals.LawbotBossMaxDamage
        self.elevatorType = ElevatorConstants.ELEVATOR_OTTOMAN
        self.gavels = {}
        self.chairs = {}
        self.cannons = {}
        self.useCannons = 1
        self.juryBoxIval = None
        self.juryTimer = None
        self.witnessToon = None
        self.witnessToonOnstage = False
        self.numToonJurorsSeated = 0
        self.mainDoor = None
        self.reflectedMainDoor = None
        self.panFlashInterval = None
        self.panDamage = 0
        self.evidenceHitSfx = None
        self.toonUpSfx = None
        self.bonusTimer = ToontownTimer.ToontownTimer(needDialog = 'CJStun')
        self.bonusTimer.posInTopRightCorner()
        self.bonusTimer.hide()
        self.cooldownTimer = ToontownTimer.ToontownTimer(needDialog = 'CJCooldown')
        self.cooldownTimer.posInTopRightCorner()
        self.cooldownTimer.hide()
        self.mouseOverText = None
        self.warningSfx = None
        self.juryMovesSfx = None
        self.baseColStashed = False
        self.battleDifficulty = 0
        self.bonusWeight = 0
        self.numJurorsLocalToonSeated = 0
        self.cannonIndex = -1
        self.departmentExpBar = None
        self.cookieProps = []
        return

    def announceGenerate(self):
        global OneBossCog
        self.notify.debug('----- announceGenerate')
        DistributedBossCog.DistributedBossCog.announceGenerate(self)
        self.setName(TTLocalizer.LawbotBossName)
        nameInfo = TTLocalizer.BossCogNameWithDept % {'name': self.getName(),
                                                      'dept': SuitDNA.getDeptFullname(self.style.dept)}
        self.setDisplayName(nameInfo)
        self.healthGui.setBossName(TTLocalizer.StandinShort)
        self.piesRestockSfx = loader.loadSfx('phase_5/audio/sfx/LB_receive_evidence.ogg')
        self.rampSlideSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_ramp_slide.ogg')
        self.evidenceHitSfx = loader.loadSfx('phase_11/audio/sfx/LB_evidence_hit.ogg')
        self.warningSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_GOON_tractor_beam_alarmed.ogg')
        self.juryMovesSfx = loader.loadSfx('phase_11/audio/sfx/LB_jury_moves.ogg')
        self.toonUpSfx = loader.loadSfx('phase_11/audio/sfx/LB_toonup.ogg')
        self.strafeSfx = []
        for i in range(10):
            self.strafeSfx.append(loader.loadSfx('phase_3.5/audio/sfx/SA_shred.ogg'))
        self.boomSfx = loader.loadSfx('phase_3.5/audio/sfx/clock07.ogg')

        render.setTag('pieCode', str(ToontownGlobals.PieCodeNotBossCog))
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
        self.__loadMopaths()
        ottomanSuitDNA = SuitDNA.SuitDNA()
        ottomanSuitDNA.newSuit('ottoman')
        self.ottoman = Suit.Suit()
        self.ottoman.setDNA(ottomanSuitDNA)
        self.ottoman.loop('writing')
        self.ottoman.reparentTo(render)
        self.ottoman.setPickable(0)
        self.ottoman.initializeBodyCollisions('ottoman_col')
        self.ottoman.setName(TTLocalizer.PrintCOO)
        self.ottoman.setDisplayName(TTLocalizer.SuitBaseNameWithNoLevel % {'name': TTLocalizer.COO, 'dept': TTLocalizer.Boardbot})
        self.ottoman.setPosHpr(1, 19, 0.25, 180, 0, 0)
        self.ottoman.addActive()
        dividendKingSuitDNA = SuitDNA.SuitDNA()
        dividendKingSuitDNA.newSuitRandom(dept='g')
        self.dividend_king = Suit.Suit()
        self.dividend_king.setDNA(dividendKingSuitDNA)
        self.dividend_king.loop('neutral')
        self.dividend_king.reparentTo(render)
        self.dividend_king.setPickable(0)
        self.dividend_king.initializeBodyCollisions('toon')
        self.dividend_king.setName("Dividend King")
        self.dividend_king.setDisplayName("Dividend King")
        self.dividend_king.setPosHpr(6, 7, 0, 15, 0, 0)
        self.dividend_king.hide()
        pen = loader.loadModel('phase_5/models/props/pen')
        pen.setPosHpr(0.2, 0.7, -0.1, -15, 180, 45)
        pen.setScale(1, 0.7, 1)
        pen.reparentTo(self.ottoman.leftHand)
        base.localAvatar.chatContainer.speedChatMenu.addCOOMenu()
        if OneBossCog is not None:
            self.notify.warning('Multiple BossCogs visible.')
        OneBossCog = self
        return

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        global OneBossCog
        self.notify.debug('----- disable')
        DistributedBossCog.DistributedBossCog.disable(self)
        self.request('Off')
        self.unloadEnvironment()
        self.ottoman.removeActive()
        self.ottoman.cleanup()
        self.ottoman.removeNode()
        for music in self.radioMusic:
            music.stop()
        base.localAvatar.chatContainer.speedChatMenu.removeCOOMenu()
        if OneBossCog == self:
            OneBossCog = None
        return

    def delete(self):
        self.notify.debug('----- delete')
        DistributedBossCog.DistributedBossCog.delete(self)

    def placeToonInElevator(self, toon):
        toonIndex = self.involvedToons.index(toon.doId)
        toon.reparentTo(self.elevatorModel)
        toon.setPos(*ElevatorConstants.BigElevatorPoints[toonIndex])
        toon.setHpr(180, 0, 0)

    def d_hitBoss(self, bossDamage):
        self.notify.debug('----- d_hitBoss')
        self.sendUpdate('hitBoss', [bossDamage])

    def d_healBoss(self, bossHeal):
        self.notify.debug('----- d_bossHeal')
        self.sendUpdate('healBoss', [bossHeal])

    def d_hitBossInsides(self):
        self.notify.debug('----- d_hitBossInsides')
        self.sendUpdate('hitBossInsides', [])

    def d_hitDefensePan(self):
        self.notify.debug('----- d_hitDefensePan')
        self.sendUpdate('hitDefensePan', [])

    def d_hitProsecutionPan(self):
        self.notify.debug('----- d_hitProsecutionPan')
        self.sendUpdate('hitProsecutionPan', [])

    def d_hitToon(self, toonId):
        self.notify.debug('----- d_hitToon')
        self.sendUpdate('hitToon', [toonId])

    def gotToon(self, toon):
        stateName = self.state
        if stateName == 'Elevator':
            self.placeToonInElevator(toon)

    def setLawyerIds(self, lawyerIds):
        self.lawyers = []
        self.cr.relatedObjectMgr.abortRequest(self.lawyerRequest)
        self.lawyerRequest = self.cr.relatedObjectMgr.requestObjects(lawyerIds, allCallback=self.__gotLawyers)

    def __gotLawyers(self, lawyers):
        self.lawyerRequest = None
        self.lawyers = lawyers
        for i in range(len(self.lawyers)):
            suit = self.lawyers[i]
            suit.request('Neutral')
            suit.loop('neutral')
            suit.setBossCogId(self.doId)

        return

    def setBossDamage(self, bossDamage, recoverRate, timestamp):
        recoverStartTime = globalClockDelta.networkToLocalTime(timestamp)
        self.bossDamage = bossDamage
        self.healthGui.updateHealth(self.bossMaxDamage - self.bossDamage)
        self.recoverRate = recoverRate
        self.recoverStartTime = recoverStartTime
        taskName = 'RecoverBossDamage'
        taskMgr.remove(taskName)
        if self.bossDamageMovie:
            if self.bossDamage >= self.bossMaxDamage:
                self.notify.debug('finish the movie then transition to NearVictory')
                self.bossDamageMovie.resumeUntil(self.bossDamageMovie.getDuration())
            else:
                self.bossDamageMovie.resumeUntil(self.bossDamage * self.bossDamageToMovie)
                if self.recoverRate:
                    taskMgr.add(self.__recoverBossDamage, taskName)
        self.makeScaleReflectDamage()
        messenger.send(ConditionGlobals.RefreshMsg)

    def updateDamageDealt(self, avId, damageDealt):
        self.healthGui.updateDamageDealt(avId, damageDealt)

    def updateStunCount(self, avId):
        self.healthGui.updateStunCount(avId)

    def getBossDamage(self):
        self.notify.debug('----- getBossDamage')
        now = globalClock.getFrameTime()
        elapsed = now - self.recoverStartTime
        return max(self.bossDamage - self.recoverRate * elapsed / 60.0, 0)

    def __recoverBossDamage(self, task):
        self.notify.debug('----- __recoverBossDamage')
        if self.bossDamageMovie:
            self.bossDamageMovie.setT(self.getBossDamage() * self.bossDamageToMovie)
        return Task.cont

    def __walkToonToPromotion(self, toonId, delay, mopath, track, delayDeletes):
        self.notify.debug('----- __walkToonToPromotion')
        toon = base.cr.doId2do.get(toonId)
        if toon:
            destPos = toon.getPos()
            self.placeToonInElevator(toon)
            toon.wrtReparentTo(render)
            ival = Sequence(Wait(delay), Func(toon.suit.setPlayRate, 1, 'walk'), Func(toon.suit.loop, 'walk'), toon.posInterval(1, Point3(0, 90, 20)), ParallelEndTogether(MopathInterval(mopath, toon), toon.posInterval(2, destPos, blendType='noBlend')), Func(toon.suit.loop, 'neutral'))
            track.append(ival)
            delayDeletes.append(DelayDelete.DelayDelete(toon, 'LawbotBoss.__walkToonToPromotion'))

    def __walkSuitToPoint(self, node, fromPos, toPos):
        self.notify.debug('----- __walkSuitToPoint')
        vector = Vec3(toPos - fromPos)
        distance = vector.length()
        time = distance / (ToontownGlobals.SuitWalkSpeed * 1.8)
        return Sequence(Func(node.setPos, fromPos), Func(node.headsUp, toPos), node.posInterval(time, toPos))

    def __makeRollToBattleTwoMovie(self):
        # startPos = Point3(BossCogGlobals.LawbotBossBattleOnePosHpr[0], BossCogGlobals.LawbotBossBattleOnePosHpr[1], BossCogGlobals.LawbotBossBattleOnePosHpr[2])
        # if self.arenaSide:
        #     topRampPos = Point3(*BossCogGlobals.LawbotBossTopRampPosB)
        #     topRampTurnPos = Point3(*BossCogGlobals.LawbotBossTopRampTurnPosB)
        #     p3Pos = Point3(*BossCogGlobals.LawbotBossP3PosB)
        # else:
        #     topRampPos = Point3(*BossCogGlobals.LawbotBossTopRampPosA)
        #     topRampTurnPos = Point3(*BossCogGlobals.LawbotBossTopRampTurnPosA)
        #     p3Pos = Point3(*BossCogGlobals.LawbotBossP3PosA)
        # battlePos = Point3(BossCogGlobals.LawbotBossBattleTwoPosHpr[0], BossCogGlobals.LawbotBossBattleTwoPosHpr[1], BossCogGlobals.LawbotBossBattleTwoPosHpr[2])
        # battleHpr = VBase3(BossCogGlobals.LawbotBossBattleTwoPosHpr[3], BossCogGlobals.LawbotBossBattleTwoPosHpr[4], BossCogGlobals.LawbotBossBattleTwoPosHpr[5])
        bossTrack = Sequence()
        self.notify.debug('calling setPosHpr')
        base.camera.posHprInterval(8, Point3(-22, -100, 35), Point3(-10, -13, 0), startPos=Point3(-22, -90, 35), startHpr=Point3(-10, -13, 0), blendType='easeInOut')
        chatTrack = Sequence(Func(self.ottoman.setChatAbsolute, TTLocalizer.LawbotBossTempJury1, CFSpeech), Func(base.camera.reparentTo, localAvatar), Func(base.camera.setPos, 0.0, -9.0 * base.localAvatar.getClampedAvatarHeight() * 0.3333333333, base.localAvatar.getClampedAvatarHeight()), Func(base.camera.setHpr, 0, 0, 0), Func(self.releaseToons, 1))
        bossTrack.append(Func(self.ottoman.setH, 0))
        bossTrack.append(Func(self.ottoman.loop, 'walk'))
        bossTrack.append(Parallel(Sequence(LerpPosInterval(self.ottoman, 13.5, Vec3(-2.798, 75, 0.025)), LerpPosInterval(self.ottoman, 1.5, Vec3(-2.798, 79, 2.025))), Sequence(Wait(15), Func(self.ottoman.loop, 'neutral'))))
        self.makeToonsWait()
        finalPodiumPos = Point3(self.podium.getX(), self.podium.getY(), self.podium.getZ() + BossCogGlobals.LawbotBossBattleTwoPosHpr[2])
        finalReflectedPodiumPos = Point3(self.reflectedPodium.getX(), self.reflectedPodium.getY(), self.reflectedPodium.getZ() + BossCogGlobals.LawbotBossBattleTwoPosHpr[2])
        return Sequence(chatTrack, bossTrack, Func(self.getGeomNode().setH, 0), Parallel(self.podium.posInterval(5.0, finalPodiumPos), self.reflectedPodium.posInterval(5.0, finalReflectedPodiumPos), Func(self.ottoman.setH, 180), self.ottoman.posInterval(5.0, Vec3(-2.798, 79, 21.029))), name=self.uniqueName('BattleTwoMovie'))

    def __makeRollToBattleThreeMovie(self):
        startPos = Point3(BossCogGlobals.LawbotBossBattleTwoPosHpr[0], BossCogGlobals.LawbotBossBattleTwoPosHpr[1], BossCogGlobals.LawbotBossBattleTwoPosHpr[2])
        battlePos = Point3(BossCogGlobals.LawbotBossBattleThreePosHpr[0], BossCogGlobals.LawbotBossBattleThreePosHpr[1], BossCogGlobals.LawbotBossBattleThreePosHpr[2])
        battleHpr = VBase3(BossCogGlobals.LawbotBossBattleThreePosHpr[3], BossCogGlobals.LawbotBossBattleThreePosHpr[4], BossCogGlobals.LawbotBossBattleThreePosHpr[5])
        bossTrack = Sequence()
        base.camera.posHprInterval(8, Point3(-22, -100, 35), Point3(-10, -13, 0), startPos=Point3(-22, -90, 35), startHpr=Point3(-10, -13, 0), blendType='easeInOut')
        chatTrack = Sequence(Func(self.setChatAbsolute, TTLocalizer.LawbotBossTrialChat1, CFSpeech), Func(base.camera.reparentTo, localAvatar), Func(base.camera.setPos, 0.0, -9.0 * base.localAvatar.getClampedAvatarHeight() * 0.3333333333, base.localAvatar.getClampedAvatarHeight()), Func(base.camera.setHpr, 0, 0, 0), Func(self.releaseToons, 1))
        bossTrack.append(Func(self.getGeomNode().setH, 180))
        bossTrack.append(Func(self.loop, 'Ff_neutral'))
        track, hpr = self.rollBossToPoint(startPos, None, battlePos, None, 0)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(battlePos, hpr, battlePos, battleHpr, 0)
        self.makeToonsWait()
        return Sequence(chatTrack, bossTrack, Func(self.getGeomNode().setH, 0), name=self.uniqueName('BattleTwoMovie'))

    def toNeutralMode(self):
        if self.cr:
            place = self.cr.playGame.getPlace()
            if place:
                place.setState('WaitForBattle')

    def makeToonsWait(self):
        self.notify.debug('makeToonsWait')
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

    def makeEndOfBattleMovie(self, hasLocalToon):
        name = self.uniqueName('Drop')
        seq = Sequence(name=name)
        seq += [Wait(0.0)]
        if hasLocalToon:
            seq += [Func(self.show),
             Func(base.camera.reparentTo, localAvatar),
             Func(base.camera.setPos, 0.0, -9.0 * base.localAvatar.getClampedAvatarHeight() * 0.3333333333, base.localAvatar.getClampedAvatarHeight()),
             Func(base.camera.setHpr, 0, 0, 0)]
        seq.append(Func(self.ottoman.setChatAbsolute, TTLocalizer.LawbotBossPassExam, CFSpeech))
        seq.append(Wait(5.0))
        seq.append(Func(self.clearChat))
        return seq

    def __makeBossDamageMovie(self):
        self.notify.debug('---- __makeBossDamageMovie')
        startPos = Point3(BossCogGlobals.LawbotBossBattleThreePosHpr[0], BossCogGlobals.LawbotBossBattleThreePosHpr[1], BossCogGlobals.LawbotBossBattleThreePosHpr[2])
        startHpr = Point3(*ToontownGlobals.LawbotBossBattleThreeHpr)
        bottomPos = Point3(*ToontownGlobals.LawbotBossBottomPos)
        deathPos = Point3(*BossCogGlobals.LawbotBossDeathPos)
        self.setPosHpr(startPos, startHpr)
        bossTrack = Sequence()
        bossTrack.append(Func(self.loop, 'Ff_neutral'))
        track, hpr = self.rollBossToPoint(startPos, startHpr, bottomPos, None, 1)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(bottomPos, startHpr, deathPos, None, 1)
        bossTrack.append(track)
        # duration = bossTrack.getDuration()
        return bossTrack

    def __showOnscreenMessage(self, text):
        self.notify.debug('----- __showOnscreenmessage')
        if self.onscreenMessage:
            self.onscreenMessage.destroy()
            self.onscreenMessage = None
        self.onscreenMessage = DirectLabel(text=text, text_fg=VBase4(1, 1, 1, 1), text_align=TextNode.ACenter, relief=None, pos=(0, 0, 0.35), scale=0.1)
        return

    def __clearOnscreenMessage(self):
        if self.onscreenMessage:
            self.onscreenMessage.destroy()
            self.onscreenMessage = None
        return

    def __showWaitingMessage(self, task):
        self.notify.debug('----- __showWaitingMessage')
        self.__showOnscreenMessage(TTLocalizer.BuildingWaitingForVictors)

    def loadEnvironment(self):
        self.notify.debug('----- loadEnvironment')
        DistributedBossCog.DistributedBossCog.loadEnvironment(self)
        self.geom = loader.loadModel('phase_13/models/events/apriltoons/boredbot/ottoman_office')
        self.elevatorEntrance = self.geom.find('**/elevator_origin')
        self.elevatorEntrance.getChildren().detach()
        self.elevatorEntrance.setScale(1)
        elevatorModel = loader.loadModel('phase_9/models/cogHQ/cogHQ_elevator')
        elevatorModel.reparentTo(self.elevatorEntrance)
        self.setupElevator(elevatorModel)
        self.elevatorMusic = base.musicMgr.loadMusic('bd_elevator')
        self.numOfRadioSongs = 19
        self.radioMusic = [base.loader.loadMusic(f'phase_13/audio/bgm/april_toons/coo/radio_{i + 1}.ogg')
                           for i in range(self.numOfRadioSongs + 1)]
        self.betweenBattleMusic = base.loader.loadMusic('phase_13/audio/bgm/btl/encntr_toon_winning_BTL3_WSI.ogg')
        self.battleTwoMusic = base.loader.loadMusic('phase_13/audio/bgm/btl/LB_juryBG_BTL3.ogg')

        self.battleStandIn = base.loader.loadMusic('phase_13/audio/bgm/btl/encntr_suit_winning_indoor_BTL3_WSI.ogg')
        self.battleBTLMusic = base.loader.loadMusic('phase_13/audio/bgm/btl/encntr_suit_winning_BTL3_WSI.ogg')
        self.epilogueMusicBTL = base.loader.loadMusic('phase_13/audio/bgm/btl/encntr_hall_of_fame_BTL3_WSI.ogg')

        self.geom.reparentTo(render)

    def loadJuryBox(self):
        self.juryBox = self.geom.find('**/JuryBox')
        juryBoxPos = self.juryBox.getPos()
        newPos = juryBoxPos - Point3(*ToontownGlobals.LawbotBossJuryBoxRelativeEndPos)
        if not self.debugPositions:
            self.juryBox.setPos(newPos)
        self.reflectedJuryBox = self.geom.find('**/JuryBox_Geo_Reflect')
        reflectedJuryBoxPos = self.reflectedJuryBox.getPos()
        newReflectedPos = reflectedJuryBoxPos - Point3(*ToontownGlobals.LawbotBossJuryBoxRelativeEndPos)
        if not self.debugPositions:
            self.reflectedJuryBox.setPos(newReflectedPos)
        if not self.reflectedJuryBox.isEmpty():
            if self.debugPositions:
                self.reflectedJuryBox.show()
        self.reflectedJuryBox.setZ(self.reflectedJuryBox.getZ() + ToontownGlobals.LawbotBossJuryBoxRelativeEndPos[2])

    def loadPodium(self):
        self.podium = self.geom.find('**/Podium')
        newZ = self.podium.getZ() - BossCogGlobals.LawbotBossBattleTwoPosHpr[2]
        if not self.debugPositions:
            self.podium.setZ(newZ)
        self.reflectedPodium = self.geom.find('**/Podium_Geo1_Refl')
        reflectedZ = self.reflectedPodium.getZ()
        if not self.debugPositions:
            self.reflectedPodium.setZ(reflectedZ)
        if not self.reflectedPodium.isEmpty():
            if self.debugPositions:
                self.reflectedPodium.show()

    def loadCannons(self):
        pass

    def loadWitnessStand(self):
        self.realWitnessStand = self.geom.find('**/WitnessStand')
        if not self.realWitnessStand.isEmpty():
            pass
        self.reflectedWitnessStand = self.geom.find('**/Witnessstand_Geo_Reflect')
        if not self.reflectedWitnessStand.isEmpty():
            pass
        colNode = self.realWitnessStand.find('**/witnessStandCollisions/Witnessstand_Collision')
        colNode.setName('WitnessStand')

    def loadScale(self):
        self.useProgrammerScale = ConfigVariableBool('want-injustice-scale-debug', False).getValue()
        if self.useProgrammerScale:
            self.loadScaleOld()
        else:
            self.loadScaleNew()

    def __debugScale(self):
        prosecutionPanPos = self.prosecutionPanNodePath.getPos()
        origin = Point3(0, 0, 0)
        prosecutionPanRelPos = self.scaleNodePath.getRelativePoint(self.prosecutionPanNodePath, origin)
        panRenderPos = render.getRelativePoint(self.prosecutionPanNodePath, origin)
        self.notify.debug('prosecutionPanPos = %s' % prosecutionPanPos)
        self.notify.debug('prosecutionPanRelPos = %s' % prosecutionPanRelPos)
        self.notify.debug('panRenderPos = %s' % panRenderPos)
        prosecutionLocatorPos = self.prosecutionLocator.getPos()
        prosecutionLocatorRelPos = self.scaleNodePath.getRelativePoint(self.prosecutionLocator, origin)
        locatorRenderPos = render.getRelativePoint(self.prosecutionLocator, origin)
        self.notify.debug('prosecutionLocatorPos = %s ' % prosecutionLocatorPos)
        self.notify.debug('prosecutionLocatorRelPos = %s ' % prosecutionLocatorRelPos)
        self.notify.debug('locatorRenderPos = %s' % locatorRenderPos)
        beamPos = self.beamNodePath.getPos()
        beamRelPos = self.scaleNodePath.getRelativePoint(self.beamNodePath, origin)
        beamRenderPos = render.getRelativePoint(self.beamNodePath, origin)
        self.notify.debug('beamPos = %s' % beamPos)
        self.notify.debug('beamRelPos = %s' % beamRelPos)
        self.notify.debug('beamRenderPos = %s' % beamRenderPos)
        beamBoundsCenter = self.beamNodePath.getBounds().getCenter()
        self.notify.debug('beamBoundsCenter = %s' % beamBoundsCenter)
        beamLocatorBounds = self.beamLocator.getBounds()
        beamLocatorPos = beamLocatorBounds.getCenter()
        self.notify.debug('beamLocatorPos = %s' % beamLocatorPos)

    def loadScaleNew(self):
        self.scaleNodePath = loader.loadModel('phase_11/models/lawbotHQ/scale')
        self.beamNodePath = self.scaleNodePath.find('**/scaleBeam')
        self.defensePanNodePath = self.scaleNodePath.find('**/defensePan')
        self.prosecutionPanNodePath = self.scaleNodePath.find('**/prosecutionPan')
        self.defenseColNodePath = self.scaleNodePath.find('**/DefenseCol')
        self.defenseColNodePath.setTag('pieCode', str(ToontownGlobals.PieCodeDefensePan))
        self.prosecutionColNodePath = self.scaleNodePath.find('**/ProsecutionCol')
        self.prosecutionColNodePath.setTag('pieCode', str(ToontownGlobals.PieCodeProsecutionPan))
        self.standNodePath = self.scaleNodePath.find('**/scaleStand')
        self.scaleNodePath.setPosHpr(*ToontownGlobals.LawbotBossInjusticePosHpr)
        self.defenseLocator = self.scaleNodePath.find('**/DefenseLocator')
        defenseLocBounds = self.defenseLocator.getBounds()
        defenseLocPos = defenseLocBounds.getCenter()
        self.notify.debug('defenseLocatorPos = %s' % defenseLocPos)
        self.defensePanNodePath.setPos(defenseLocPos)
        self.defensePanNodePath.reparentTo(self.beamNodePath)
        self.notify.debug('defensePanNodePath.getPos()=%s' % self.defensePanNodePath.getPos())
        self.prosecutionLocator = self.scaleNodePath.find('**/ProsecutionLocator')
        prosecutionLocBounds = self.prosecutionLocator.getBounds()
        prosecutionLocPos = prosecutionLocBounds.getCenter()
        self.notify.debug('prosecutionLocatorPos = %s' % prosecutionLocPos)
        self.prosecutionPanNodePath.setPos(prosecutionLocPos)
        self.prosecutionPanNodePath.reparentTo(self.beamNodePath)
        self.beamLocator = self.scaleNodePath.find('**/StandLocator1')
        beamLocatorBounds = self.beamLocator.getBounds()
        beamLocatorPos = beamLocatorBounds.getCenter()
        negBeamLocatorPos = -beamLocatorPos
        self.notify.debug('beamLocatorPos = %s' % beamLocatorPos)
        self.notify.debug('negBeamLocatorPos = %s' % negBeamLocatorPos)
        self.beamNodePath.setPos(beamLocatorPos)
        self.scaleNodePath.setScale(*ToontownGlobals.LawbotBossInjusticeScale)
        self.scaleNodePath.wrtReparentTo(self.geom)
        self.baseHighCol = self.scaleNodePath.find('**/BaseHighCol')
        oldBitMask = self.baseHighCol.getCollideMask()
        newBitMask = oldBitMask & ~ToontownGlobals.PieBitmask
        newBitMask = newBitMask & ~ToontownGlobals.CameraBitmask
        self.baseHighCol.setCollideMask(newBitMask)
        self.defenseHighCol = self.scaleNodePath.find('**/DefenseHighCol')
        self.defenseHighCol.stash()
        self.defenseHighCol.setCollideMask(newBitMask)
        self.baseTopCol = self.scaleNodePath.find('**/Scale_base_top_collision')
        self.baseSideCol = self.scaleNodePath.find('**/Scale_base_side_col')
        self.defenseLocator.hide()
        self.prosecutionLocator.hide()
        self.beamLocator.hide()

    def loadScaleOld(self):
        startingTilt = 0
        self.scaleNodePath = NodePath('injusticeScale')
        beamGeom = self.createBlock(0.25, 2, 0.125, -0.25, -2, -0.125, 0, 1.0, 0, 1.0)
        self.beamNodePath = NodePath('scaleBeam')
        self.beamNodePath.attachNewNode(beamGeom)
        self.beamNodePath.setPos(0, 0, 3)
        self.beamNodePath.reparentTo(self.scaleNodePath)
        defensePanGeom = self.createBlock(0.5, 0.5, 0, -0.5, -0.5, -2, 0, 0, 1.0, 0.25)
        self.defensePanNodePath = NodePath('defensePan')
        self.defensePanNodePath.attachNewNode(defensePanGeom)
        self.defensePanNodePath.setPos(0, -2, 0)
        self.defensePanNodePath.reparentTo(self.beamNodePath)
        defenseTube = CollisionTube(0, 0, -0.5, 0, 0, -1.5, 0.6)
        defenseTube.setTangible(1)
        defenseCollNode = CollisionNode('DefenseCol')
        defenseCollNode.addSolid(defenseTube)
        self.defenseColNodePath = self.defensePanNodePath.attachNewNode(defenseCollNode)
        self.defenseColNodePath.setTag('pieCode', str(ToontownGlobals.PieCodeDefensePan))
        prosecutionPanGeom = self.createBlock(0.5, 0.5, 0, -0.5, -0.5, -2, 1.0, 0, 0, 1.0)
        self.prosecutionPanNodePath = NodePath('prosecutionPan')
        self.prosecutionPanNodePath.attachNewNode(prosecutionPanGeom)
        self.prosecutionPanNodePath.setPos(0, 2, 0)
        self.prosecutionPanNodePath.reparentTo(self.beamNodePath)
        prosecutionTube = CollisionTube(0, 0, -0.5, 0, 0, -1.5, 0.6)
        prosecutionTube.setTangible(1)
        prosecutionCollNode = CollisionNode(self.uniqueName('ProsecutionCol'))
        prosecutionCollNode.addSolid(prosecutionTube)
        self.prosecutionColNodePath = self.prosecutionPanNodePath.attachNewNode(prosecutionCollNode)
        self.prosecutionColNodePath.setTag('pieCode', str(ToontownGlobals.PieCodeProsecutionPan))
        standGeom = self.createBlock(0.25, 0.25, 0, -0.25, -0.25, 3)
        self.standNodePath = NodePath('scaleStand')
        self.standNodePath.attachNewNode(standGeom)
        self.standNodePath.reparentTo(self.scaleNodePath)
        self.scaleNodePath.setPosHpr(*ToontownGlobals.LawbotBossInjusticePosHpr)
        self.scaleNodePath.setScale(5.0)
        self.scaleNodePath.wrtReparentTo(self.geom)
        self.setScaleTilt(startingTilt)

    def setScaleTilt(self, tilt):
        self.beamNodePath.setP(tilt)
        if self.useProgrammerScale:
            self.defensePanNodePath.setP(-tilt)
            self.prosecutionPanNodePath.setP(-tilt)
        else:
            self.defensePanNodePath.setP(-tilt)
            self.prosecutionPanNodePath.setP(-tilt)

    def stashBaseCol(self):
        if not self.baseColStashed:
            self.notify.debug('stashBaseCol')
            self.baseTopCol.stash()
            self.baseSideCol.stash()
            self.baseColStashed = True

    def unstashBaseCol(self):
        if self.baseColStashed:
            self.notify.debug('unstashBaseCol')
            self.baseTopCol.unstash()
            self.baseSideCol.unstash()
            self.baseColStashed = False

    def makeScaleReflectDamage(self):
        diffDamage = self.bossDamage - ToontownGlobals.LawbotBossInitialDamage
        diffDamage *= 1.0
        if diffDamage >= 0:
            percentDamaged = diffDamage / (
                    BossCogGlobals.LawbotBossMaxDamage - ToontownGlobals.LawbotBossInitialDamage)
            tilt = percentDamaged * ToontownGlobals.LawbotBossWinningTilt
        else:
            percentDamaged = diffDamage / (ToontownGlobals.LawbotBossInitialDamage - 0)
            tilt = percentDamaged * ToontownGlobals.LawbotBossWinningTilt
        self.setScaleTilt(tilt)
        if self.bossDamage < BossCogGlobals.LawbotBossMaxDamage * 0.85:
            self.unstashBaseCol()
        else:
            self.stashBaseCol()

    def unloadEnvironment(self):
        self.notify.debug('----- unloadEnvironment')
        DistributedBossCog.DistributedBossCog.unloadEnvironment(self)
        self.geom.removeNode()
        del self.geom
        for cookieNode in self.cookieProps:
            cookieNode.removeNode()
        self.cookieProps = []

    def __loadMopaths(self):
        self.notify.debug('----- __loadMopaths')
        self.toonsEnterA = Mopath.Mopath()
        self.toonsEnterA.loadFile('phase_9/paths/bossBattle-toonsEnterA')
        self.toonsEnterA.fFaceForward = 1
        self.toonsEnterA.timeScale = 35
        self.toonsEnterB = Mopath.Mopath()
        self.toonsEnterB.loadFile('phase_9/paths/bossBattle-toonsEnterB')
        self.toonsEnterB.fFaceForward = 1
        self.toonsEnterB.timeScale = 35

    def __unloadMopaths(self):
        self.notify.debug('----- __unloadMopaths')
        self.toonsEnterA.reset()
        self.toonsEnterB.reset()

    def enterOff(self):
        self.notify.debug('----- enterOff')
        DistributedBossCog.DistributedBossCog.enterOff(self)
        if self.witnessToon:
            self.witnessToon.clearChat()

    def enterWaitForToons(self):
        self.notify.debug('----- enterWaitForToons')
        DistributedBossCog.DistributedBossCog.enterWaitForToons(self)
        self.geom.hide()

    def exitWaitForToons(self):
        self.notify.debug('----- exitWaitForToons')
        DistributedBossCog.DistributedBossCog.exitWaitForToons(self)
        self.geom.show()

    def enterElevator(self):
        base.discord.applyPreset('boss-coo')
        self.notify.debug('----- enterElevator')
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                toon.stopLookAround()
                toon.stopSmooth()
                self.placeToonInElevator(toon)
        self.startToonTotal = self.getToonCount()
        self.currentToonTotal = self.getToonCount()
        base.discord.updateParty(self.currentToonTotal, self.startToonTotal)
        self.toMovieMode()
        base.musicMgr.playMusic(self.elevatorMusic, looping=1, volume=1.0)
        base.transitions.fadeIn(0.8)
        ival = Sequence(ElevatorUtils.getRideElevatorInterval(self.elevatorType), ElevatorUtils.getRideElevatorInterval(self.elevatorType), Func(camera.wrtReparentTo, render), Func(self.__doneElevator))
        intervalName = 'ElevatorMovie'
        ival.start()
        self.storeInterval(ival, intervalName)
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleOnePosHpr)
        self.happy = 1
        self.raised = 1
        self.forward = 1
        self.doAnimate()
        self.reparentTo(render)
        self.stash()
        base.camera.reparentTo(self.elevatorModel)
        base.camera.setPosHpr(0, 30, 8, 180, 0, 0)
        base.camLens.setMinFov(ToontownGlobals.VPElevatorFov/(4./3.))

    def __doneElevator(self):
        self.doneBarrier('Elevator')

    def exitElevator(self):
        self.notify.debug('----- exitElevator')
        DistributedBossCog.DistributedBossCog.exitElevator(self)

    def enterIntroduction(self):
        self.notify.debug('----- enterIntroduction')
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleOnePosHpr)
        self.stopAnimate()
        self.controlToons()
        NametagGlobals.setMasterArrowsOn(0)
        intervalName = 'IntroductionMovie'
        delayDeletes = []
        seq = Sequence(self.makeIntroductionMovie(delayDeletes), Func(self.__beginBattleOne), name=intervalName)
        seq.delayDeletes = delayDeletes
        seq.start()
        self.storeInterval(seq, intervalName)
        self.elevatorMusic.stop()

    def exitIntroduction(self):
        self.notify.debug('----- exitIntroduction')
        DistributedBossCog.DistributedBossCog.exitIntroduction(self)

    def __beginBattleOne(self):
        intervalName = 'IntroductionMovie'
        self.clearInterval(intervalName)
        self.doneBarrier('Introduction')

    def enterBattleOne(self):
        base.discord.applyPreset('boss-coo')
        self.notify.debug('----- LawbotBoss.enterBattleOne ')

        self.cleanupIntervals()
        # mult = BattleGlobals.getBossBattleCreditMultiplier(1)
        # localAvatar.inventory.setBattleCreditMult(mult)
        self.toonsToBattlePosition(self.toonsA, self.battleANode)
        self.toonsToBattlePosition(self.toonsB, self.battleBNode)
        self.releaseToons()
        base.musicMgr.playMusic(self.battleBTLMusic, looping=1, volume=0.9)

        self.setPosHpr(*BossCogGlobals.LawbotBossBattleOnePosHpr)
        self.clearChat()
        self.ottoman.clearChat()
        self.ottoman.setPosHpr(*BossCogGlobals.LawbotBossBattleOnePosHpr)
        self.ottoman.setH(180)
        self.loop('Ff_neutral')
        self.notify.debug('self.battleANode = %s' % self.battleANode)
        self.__hideWitnessToon()
        if self.battleA is None or self.battleB is None:
            pass
        return

    def exitBattleOne(self):
        self.notify.debug('----- exitBattleOne')
        self.cleanupBattles()
        self.battleBTLMusic.stop()
        # localAvatar.inventory.setBattleCreditMult(1)

    def stashBoss(self):
        self.stash()

    def unstashBoss(self, task):
        self.unstash()

    def enterRollToBattleTwo(self):
        base.discord.applyPreset('boss-coo')
        self.notify.debug('----- enterRollToBattleTwo')
        self.releaseToons(finalBattle=1)
        self.toonsToBattlePosition(self.toonsA, self.battleANode)
        self.toonsToBattlePosition(self.toonsB, self.battleANode)
        intervalName = 'RollToBattleTwo'
        seq = Sequence(self.__makeRollToBattleTwoMovie(), Func(self.__onToPrepareBattleTwo), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        base.musicMgr.playMusic(self.betweenBattleMusic, looping=1, volume=0.9)

    def __onToPrepareBattleTwo(self):
        self.notify.debug('----- __onToPrepareBattleTwo')
        self.unstickBoss()
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleTwoPosHpr)
        self.doneBarrier('RollToBattleTwo')

    def exitRollToBattleTwo(self):
        self.notify.debug('----- exitRollToBattleTwo')
        self.unstickBoss()
        intervalName = 'RollToBattleTwo'
        self.clearInterval(intervalName)
        self.betweenBattleMusic.stop()

    def enterPrepareBattleTwo(self):
        self.notify.debug('----- enterPrepareBattleTwo')
        self.cleanupIntervals()
        self.controlToons()
        self.setToonsToNeutral(self.involvedToons)
        self.clearChat()
        self.__showWitnessToon()
        prepareBattleTwoMovie = self.__makePrepareBattleTwoMovie()
        intervalName = 'prepareBattleTwo'
        seq = Sequence(prepareBattleTwoMovie, name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        self.acceptOnce('doneChatPage', self.__showCannonsAppearing)
        base.musicMgr.playMusic(self.stingMusic, looping=0, volume=1.0)

    def __showCannonsAppearing(self, elapsedTime = 0):
        base.discord.applyPreset('boss-coo')
        allCannonsAppear = Sequence(Func(self.__positionToonsInFrontOfCannons), Func(base.camera.reparentTo, localAvatar), Func(base.camera.setPos, 5.7 * (base.localAvatar.getClampedAvatarHeight() * 0.3333333333), 7.65 * (base.localAvatar.getClampedAvatarHeight() * 0.3333333333), base.localAvatar.getClampedAvatarHeight() + .25), Func(base.camera.lookAt, localAvatar))
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
        intervalName = 'prepareBattleTwoCannonsAppear'
        seq = Sequence(allCannonsAppear, Func(self.__onToBattleTwo), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)

    def __onToBattleTwo(self, elapsedTime = 0):
        self.notify.debug('----- __onToBattleTwo')
        self.doneBarrier('PrepareBattleTwo')
        taskMgr.doMethodLater(1, self.__showWaitingMessage, self.uniqueName('WaitingMessage'))

    def exitPrepareBattleTwo(self):
        self.notify.debug('----- exitPrepareBattleTwo')
        self.show()
        taskMgr.remove(self.uniqueName('WaitingMessage'))
        self.ignore('doneChatPage')
        self.__clearOnscreenMessage()
        self.stingMusic.stop()

    def enterBattleTwo(self):
        self.notify.debug('----- enterBattleTwo')
        self.cleanupIntervals()
        # mult = BattleGlobals.getBossBattleCreditMultiplier(2)
        # localAvatar.inventory.setBattleCreditMult(mult)
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleTwoPosHpr)
        self.ottoman.clearChat()
        self.witnessToon.clearChat()
        self.releaseToons(finalBattle=1)
        self.__showWitnessToon()
        if not self.useCannons:
            self.toonsToBattlePosition(self.toonsA, self.battleANode)
            self.toonsToBattlePosition(self.toonsB, self.battleBNode)
        base.musicMgr.playMusic(self.battleTwoMusic, looping=1, volume=0.9)
        self.startJuryBoxMoving()
        for index in range(len(self.cannons)):
            cannon = self.cannons[index]
            cannon.cannon.show()
        base.cr.gameGui.expBar.hide()
        self.departmentExpBar = DepartmentExperienceBar.DepartmentExperienceBar(base.localAvatar.departmentExp[ToontownGlobals.DEPARTMENT_LAWBOT], base.localAvatar.departmentLevels[ToontownGlobals.DEPARTMENT_LAWBOT], ToontownGlobals.DEPARTMENT_LAWBOT, base.localAvatar.style)
        self.departmentExpBar.setAvatar(base.localAvatar)
        self.departmentExpBar.setScale(0.075)
        self.departmentExpBar.reparentTo(base.a2dBottomLeft)
        self.departmentExpBar.start()

    def getChairParent(self):
        return self.juryBox

    def startJuryBoxMoving(self):
        curPos = self.juryBox.getPos()
        endingAbsPos = Point3(curPos[0] + ToontownGlobals.LawbotBossJuryBoxRelativeEndPos[0], curPos[1] + ToontownGlobals.LawbotBossJuryBoxRelativeEndPos[1], curPos[2] + ToontownGlobals.LawbotBossJuryBoxRelativeEndPos[2])
        curReflectedPos = self.reflectedJuryBox.getPos()
        reflectedEndingAbsPos = Point3(curReflectedPos[0] + ToontownGlobals.LawbotBossJuryBoxRelativeEndPos[0], curReflectedPos[1] + ToontownGlobals.LawbotBossJuryBoxRelativeEndPos[1], curReflectedPos[2] + ToontownGlobals.LawbotBossJuryBoxRelativeEndPos[2])
        self.juryBoxIval = Parallel(self.juryBox.posInterval(ToontownGlobals.LawbotBossJuryBoxMoveTime, endingAbsPos), self.reflectedJuryBox.posInterval(ToontownGlobals.LawbotBossJuryBoxMoveTime, reflectedEndingAbsPos), SoundInterval(self.juryMovesSfx, node=self.chairs[2].nodePath, duration=ToontownGlobals.LawbotBossJuryBoxMoveTime, loop=1, volume=1.0))
        self.juryBoxIval.start()
        self.juryTimer = ToontownTimer.ToontownTimer()
        self.juryTimer.posInTopRightCorner()
        self.juryTimer.countdown(ToontownGlobals.LawbotBossJuryBoxMoveTime)

    def exitBattleTwo(self):
        self.notify.debug('----- exitBattleTwo')
        intervalName = self.uniqueName('Drop')
        self.clearInterval(intervalName)
        self.cleanupBattles()
        self.battleTwoMusic.stop()
        # localAvatar.inventory.setBattleCreditMult(1)
        if self.juryTimer:
            self.juryTimer.destroy()
            del self.juryTimer
            self.juryTimer = None
        for chair in list(self.chairs.values()):
            chair.stopCogsFlying()

        return

    def enterRollToBattleThree(self):
        self.notify.debug('----- enterRollToBattleThree')
        intervalName = 'RollToBattleThree'
        seq = Sequence(self.__makeRollToBattleThreeMovie(), Func(self.__onToPrepareBattleThree), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        base.musicMgr.playMusic(self.betweenBattleMusic, looping=1, volume=0.9)

    def __onToPrepareBattleThree(self):
        self.notify.debug('----- __onToPrepareBattleThree')
        self.unstickBoss()
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleThreePosHpr)
        self.doneBarrier('RollToBattleThree')

    def exitRollToBattleThree(self):
        self.notify.debug('----- exitRollToBattleThree')
        self.unstickBoss()
        intervalName = 'RollToBattleThree'
        self.clearInterval(intervalName)
        self.betweenBattleMusic.stop()

    def enterPrepareBattleThree(self):
        self.notify.debug('----- enterPrepareBattleThree')
        self.cleanupIntervals()
        self.controlToons()
        self.setToonsToNeutral(self.involvedToons)
        self.clearChat()
        base.musicMgr.playMusic(self.betweenBattleMusic, looping=1, volume=0.9)
        self.__showWitnessToon()
        prepareBattleThreeMovie = self.__makePrepareBattleThreeMovie()
        self.acceptOnce('doneChatPage', self.__onToBattleThree)
        intervalName = 'prepareBattleThree'
        seq = Sequence(prepareBattleThreeMovie, name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)

    def __onToBattleThree(self, elapsed):
        self.notify.debug('----- __onToBattleThree')
        self.doneBarrier('PrepareBattleThree')
        taskMgr.doMethodLater(1, self.__showWaitingMessage, self.uniqueName('WaitingMessage'))

    def exitPrepareBattleThree(self):
        self.notify.debug('----- exitPrepareBattleThree')
        self.show()
        taskMgr.remove(self.uniqueName('WaitingMessage'))
        self.ignore('doneChatPage')
        intervalName = 'PrepareBattleThree'
        self.clearInterval(intervalName)
        self.__clearOnscreenMessage()
        self.betweenBattleMusic.stop()

    def enterBattleThree(self):
        base.discord.applyPreset('boss-coo')
        DistributedBossCog.DistributedBossCog.enterBattleThree(self)
        self.scaleNodePath.unstash()
        localAvatar.setPos(-3, 0, 0)
        base.localAvatar.cameraFSM.request("Orbit")
        self.clearChat()
        self.witnessToon.clearChat()
        self.happy = 1
        self.raised = 1
        self.forward = 1
        self.doAnimate()
        self.accept('enterWitnessStand', self.__touchedWitnessStand)
        self.accept('pieSplat', self.__pieSplat)
        self.accept('localPieSplat', self.__localPieSplat)
        self.accept('outOfPies', self.__outOfPies)
        self.accept('begin-pie', self.__foundPieButton)
        self.accept('enterDefenseCol', self.__enterDefenseCol)
        self.accept('enterProsecutionCol', self.__enterProsecutionCol)
        localAvatar.setCameraFov(ToontownGlobals.BossBattleCameraFov)
        taskMgr.doMethodLater(30, self.__howToGetPies, self.uniqueName('PieAdvice'))
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleThreePosHpr)
        self.ottoman.setPosHpr(-2.798, 79, 21.029, 180, 0, 0)
        self.bossMaxDamage = BossCogGlobals.LawbotBossMaxDamage
        self.healthGui.setMaxHp(self.bossMaxDamage)
        self.healthGui.createBossCogHead()
        self.healthGui.show()
        base.musicMgr.playMusic(self.battleStandIn, looping=1, volume=0.9)
        self.__showWitnessToon()
        #diffSettings = ToontownGlobals.LawbotBossDifficultySettings[self.battleDifficulty]

    def __doneBattleThree(self):
        self.notify.debug('----- __doneBattleThree')
        self.setState('NearVictory')
        self.unstickBoss()

    def exitBattleThree(self):
        self.notify.debug('----- exitBattleThree')
        DistributedBossCog.DistributedBossCog.exitBattleThree(self)
        NametagGlobals.setWant2dNametags(True)
        bossDoneEventName = self.uniqueName('DestroyedBoss')
        self.ignore(bossDoneEventName)
        taskMgr.remove(self.uniqueName('StandUp'))
        self.ignore('enterWitnessStand')
        self.ignore('pieSplat')
        self.ignore('localPieSplat')
        self.ignore('outOfPies')
        self.ignore('begin-pie')
        self.ignore('enterDefenseCol')
        self.ignore('enterProsecutionCol')
        self.__clearOnscreenMessage()
        taskMgr.remove(self.uniqueName('PieAdvice'))
        localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        if self.bossDamageMovie:
            self.bossDamageMovie.finish()
        self.bossDamageMovie = None
        self.unstickBoss()
        taskName = 'RecoverBossDamage'
        taskMgr.remove(taskName)
        self.battleThreeMusicTime = self.battleStandIn.getTime()
        self.battleStandIn.stop()
        return

    def enterNearVictory(self):
        self.cleanupIntervals()
        self.setPos(*BossCogGlobals.LawbotBossDeathPos)
        self.setHpr(*ToontownGlobals.LawbotBossBattleThreeHpr)
        self.clearChat()
        self.releaseToons(finalBattle=1)
        self.accept('pieSplat', self.__finalPieSplat)
        self.accept('localPieSplat', self.__localPieSplat)
        self.accept('outOfPies', self.__outOfPies)
        localAvatar.setCameraFov(ToontownGlobals.BossBattleCameraFov)
        self.happy = 0
        self.raised = 0
        self.forward = 1
        self.doAnimate()
        self.setDizzy(1)
        base.musicMgr.playMusic(self.battleStandIn, looping=1, volume=0.9, time=self.battleThreeMusicTime)

    def exitNearVictory(self):
        self.notify.debug('----- exitNearVictory')
        self.ignore('pieSplat')
        self.ignore('localPieSplat')
        self.ignore('outOfPies')
        self.__clearOnscreenMessage()
        taskMgr.remove(self.uniqueName('PieAdvice'))
        localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        self.setDizzy(0)
        self.battleThreeMusicTime = self.battleStandIn.getTime()
        self.battleStandIn.stop()
        if self.departmentExpBar:
            self.departmentExpBar.hide()
            self.departmentExpBar.stop()
            self.departmentExpBar.destroy()
        base.cr.gameGui.expBar.show()

    def enterVictory(self):
        self.notify.debug('----- enterVictory')
        self.cleanupIntervals()
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleThreePosHpr)
        self.loop('neutral')
        localAvatar.setCameraFov(ToontownGlobals.BossBattleCameraFov)
        self.clearChat()
        self.witnessToon.clearChat()
        self.controlToons()
        self.setToonsToNeutral(self.involvedToons)
        self.happy = 1
        self.raised = 1
        self.forward = 1
        intervalName = 'VictoryMovie'
        seq = Sequence(self.makeVictoryMovie(), Func(self.__continueVictory), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        base.musicMgr.playMusic(self.battleStandIn, looping=1, volume=0.9, time=self.battleThreeMusicTime)

    def __continueVictory(self):
        self.notify.debug('----- __continueVictory')
        self.stopAnimate()
        self.healthGui.destroy()
        self.healthGui = None
        self.doneBarrier('Victory')

    def exitVictory(self):
        self.notify.debug('----- exitVictory')
        self.stopAnimate()
        self.unstash()
        localAvatar.setCameraFov(settings['fieldofview'] + 8)
        self.battleThreeMusicTime = self.battleStandIn.getTime()
        self.battleStandIn.stop()

    def enterDefeat(self):
        self.notify.debug('----- enterDefeat')
        self.cleanupIntervals()
        localAvatar.setCameraFov(ToontownGlobals.BossBattleCameraFov)
        self.clearChat()
        self.releaseToons(finalBattle=1)
        self.happy = 0
        self.raised = 0
        self.forward = 1
        intervalName = 'DefeatMovie'
        seq = Sequence(self.makeDefeatMovie(), Func(self.__continueDefeat), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        base.musicMgr.playMusic(self.battleStandIn, looping=1, volume=0.9, time=self.battleThreeMusicTime)

    def __continueDefeat(self):
        self.notify.debug('----- __continueDefeat')
        self.stopAnimate()
        self.doneBarrier('Defeat')

    def exitDefeat(self):
        self.notify.debug('----- exitDefeat')
        self.stopAnimate()
        self.unstash()
        localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        self.battleThreeMusicTime = self.battleStandIn.getTime()
        self.battleStandIn.stop()

    def enterReward(self):
        self.cleanupIntervals()
        self.clearChat()
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
        base.musicMgr.playMusic(self.battleStandIn, looping=1, volume=0.9, time=self.battleThreeMusicTime)

    def __doneReward(self):
        self.notify.debug('----- __doneReward')
        self.doneBarrier('Reward')
        self.toWalkMode()

    def exitReward(self):
        self.notify.debug('----- exitReward')
        intervalName = 'RewardMovie'
        self.clearInterval(intervalName)
        self.unstash()
        self.rewardPanel.destroy()
        del self.rewardPanel
        self.battleThreeMusicTime = 0
        self.battleStandIn.stop()

    def enterEpilogue(self):
        self.cleanupIntervals()
        self.clearChat()
        self.stash()
        self.stopAnimate()
        self.controlToons()
        intervalName = 'EpilogueMovie'
        #ElevatorUtils.openDoors(self.leftDoor, self.rightDoor, self.elevatorType)
        seq = Sequence(Func(self.__doneEpilogue), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)

    def __doneEpilogue(self, elapsedTime = 0):
        self.notify.debug('----- __doneEpilogue')
        intervalName = 'EpilogueMovieToonAnim'
        self.clearInterval(intervalName)
        track = Parallel(Sequence(Wait(0.5), Func(self.localToonToSafeZone)))
        self.storeInterval(track, intervalName)
        track.start()

    def exitEpilogue(self):
        self.notify.debug('----- exitEpilogue')
        self.clearInterval('EpilogueMovieToonAnim')
        self.unstash()
        self.epilogueMusicBTL.stop()

    def enterFrolic(self):
        self.notify.debug('----- enterFrolic')
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleOnePosHpr)
        DistributedBossCog.DistributedBossCog.enterFrolic(self)
        self.show()

    def doorACallback(self, isOpen):
        if self.insidesANodePath:
            if isOpen:
                self.insidesANodePath.unstash()
            else:
                self.insidesANodePath.stash()

    def doorBCallback(self, isOpen):
        if self.insidesBNodePath:
            if isOpen:
                self.insidesBNodePath.unstash()
            else:
                self.insidesBNodePath.stash()

    def __toonsToPromotionPosition(self, toonIds, battleNode):
        self.notify.debug('----- __toonsToPromotionPosition')
        points = BattleBase.BattleBase.toonPoints[len(toonIds) - 1]
        for i in range(len(toonIds)):
            toon = base.cr.doId2do.get(toonIds[i])
            if toon:
                toon.reparentTo(render)
                pos, h = points[i]
                toon.setPosHpr(battleNode, pos[0], pos[1] + 10, pos[2], h, 0, 0)

    def __outOfPies(self):
        self.notify.debug('----- outOfPies')
        self.__showOnscreenMessage(TTLocalizer.LawbotBossNeedMoreEvidence)
        taskMgr.doMethodLater(20, self.__howToGetPies, self.uniqueName('PieAdvice'))

    def __howToGetPies(self, task):
        self.notify.debug('----- __howToGetPies')
        self.__showOnscreenMessage(TTLocalizer.LawbotBossHowToGetEvidence)

    def __howToThrowPies(self, task):
        self.notify.debug('----- __howToThrowPies')
        self.__showOnscreenMessage(TTLocalizer.LawbotBossHowToThrowPies)

    def __foundPieButton(self):
        self.everThrownPie = 1
        self.__clearOnscreenMessage()
        taskMgr.remove(self.uniqueName('PieAdvice'))

    def __touchedWitnessStand(self, entry):
        self.sendUpdate('touchWitnessStand', [])
        self.__clearOnscreenMessage()
        taskMgr.remove(self.uniqueName('PieAdvice'))
        base.playSfx(self.piesRestockSfx)
        if not self.everThrownPie:
            taskMgr.doMethodLater(30, self.__howToThrowPies, self.uniqueName('PieAdvice'))

    def __pieSplat(self, toon, pieCode):
        if pieCode == ToontownGlobals.PieCodeBossInsides:
            if toon == localAvatar:
                self.d_hitBossInsides()
            self.flashRed()
        elif pieCode == ToontownGlobals.PieCodeBossCog:
            if toon == localAvatar:
                self.d_hitBoss(1)
            if self.dizzy:
                self.flashRed()
                self.doAnimate('hit', now=1)
        elif pieCode == ToontownGlobals.PieCodeDefensePan:
            self.flashRed()
            self.flashPanBlue()
            base.playSfx(self.evidenceHitSfx, node=self.defensePanNodePath, volume=0.25)
            if toon == localAvatar:
                self.d_hitBoss(self.panDamage)
        elif pieCode == ToontownGlobals.PieCodeProsecutionPan:
            self.flashGreen()
            if toon == localAvatar:
                pass
        elif pieCode == ToontownGlobals.PieCodeLawyer:
            pass

    def __localPieSplat(self, pieCode, entry):
        if pieCode == ToontownGlobals.PieCodeLawyer:
            self.__lawyerGotHit(entry)
        if pieCode != ToontownGlobals.PieCodeToon:
            return
        avatarDoId = entry.getIntoNodePath().getNetTag('avatarDoId')
        if avatarDoId == '':
            self.notify.warning('Toon %s has no avatarDoId tag.' % repr(entry.getIntoNodePath()))
            return
        doId = int(avatarDoId)
        if doId != localAvatar.doId:
            self.d_hitToon(doId)

    def flashRed(self):
        self.cleanupFlash()
        self.setColorScale(1, 1, 1, 1)
        i = Sequence(self.ottoman.colorScaleInterval(0.1, colorScale=VBase4(1, 0, 0, 1)), self.ottoman.colorScaleInterval(0.3, colorScale=VBase4(1, 1, 1, 1)))
        self.flashInterval = i
        i.start()

    def flashGreen(self):
        self.cleanupFlash()
        if not self.isEmpty():
            self.setColorScale(1, 1, 1, 1)
            i = Sequence(self.ottoman.colorScaleInterval(0.1, colorScale=VBase4(0, 1, 0, 1)), self.ottoman.colorScaleInterval(0.3, colorScale=VBase4(1, 1, 1, 1)))
            self.flashInterval = i
            i.start()

    def __lawyerGotHit(self, entry):
        lawyerCol = entry.getIntoNodePath()
        names = lawyerCol.getName().split('-')
        lawyerDoId = int(names[1])
        for lawyer in self.lawyers:
            if lawyerDoId == lawyer.doId:
                lawyer.sendUpdate('hitByToon', [])

    def __finalPieSplat(self, toon, pieCode):
        if pieCode != ToontownGlobals.PieCodeDefensePan:
            return
        self.sendUpdate('finalPieSplat', [])
        self.ignore('pieSplat')

    def cleanupAttacks(self):
        self.notify.debug('----- cleanupAttacks')
        self.__cleanupStrafe()

    def __cleanupStrafe(self):
        self.notify.debug('----- __cleanupStrage')
        if self.strafeInterval:
            self.strafeInterval.finish()
            self.strafeInterval = None
        return

    def __cleanupJuryBox(self):
        self.notify.debug('----- __cleanupJuryBox')
        if self.juryBoxIval:
            self.juryBoxIval.finish()
            self.juryBoxIval = None
        if self.juryBox:
            self.juryBox.removeNode()
        return

    def doStrafe(self, side, direction):
        gearRoot = self.rotateNode.attachNewNode('gearRoot')
        if side == 0:
            gearRoot.setPos(0, -7, 3)
            gearRoot.setHpr(180, 0, 0)
            door = self.doorA
        else:
            gearRoot.setPos(0, 7, 3)
            door = self.doorB
        gearRoot.setTag('attackCode', str(BossCogGlobals.BossCogStrafeAttack))
        gearModel = self.getGearFrisbee()
        gearModel.setScale(0.1)
        t = self.getBossDamage() / 100.0
        gearTrack = Parallel()
        numGears = int(4 + 6 * t + 0.5)
        time = 5.0 - 4.0 * t
        spread = 60 * math.pi / 180.0
        if direction == 1:
            spread = -spread
        dist = 50
        rate = time / numGears
        for i in range(numGears):
            node = gearRoot.attachNewNode(str(i))
            node.hide()
            node.setPos(0, 0, 0)
            gearModel.instanceTo(node)
            angle = (float(i) / (numGears - 1) - 0.5) * spread
            x = dist * math.sin(angle)
            y = dist * math.cos(angle)
            h = random.uniform(-720, 720)
            gearTrack.append(Sequence(Wait(i * rate), Func(node.show), Parallel(node.posInterval(1, Point3(x, y, 0), fluid=1), node.hprInterval(1, VBase3(h, 0, 0), fluid=1), Sequence(SoundInterval(self.strafeSfx[i], volume=0.2, node=self), duration=0)), Func(node.detachNode)))

        seq = Sequence(Func(door.request, 'open'), Wait(0.7), gearTrack, Func(door.request, 'close'))
        self.__cleanupStrafe()
        self.strafeInterval = seq
        seq.start()

    def replaceCollisionPolysWithPlanes(self, model):
        newCollisionNode = CollisionNode('collisions')
        newCollideMask = BitMask32(0)
        planes = []
        collList = model.findAllMatches('**/+CollisionNode')
        if not collList:
            collList = [model]
        for cnp in collList:
            cn = cnp.node()
            if not isinstance(cn, CollisionNode):
                self.notify.warning('Not a collision node: %s' % repr(cnp))
                break
            newCollideMask = newCollideMask | cn.getIntoCollideMask()
            for i in range(cn.getNumSolids()):
                solid = cn.getSolid(i)
                if isinstance(solid, CollisionPolygon):
                    plane = Plane(solid.getPlane())
                    planes.append(plane)
                else:
                    self.notify.warning('Unexpected collision solid: %s' % repr(solid))
                    newCollisionNode.addSolid(plane)

        newCollisionNode.setIntoCollideMask(newCollideMask)
        threshold = 0.1
        planes.sort(lambda p1, p2: p1.compareTo(p2, threshold))
        lastPlane = None
        for plane in planes:
            if lastPlane is None or plane.compareTo(lastPlane, threshold) != 0:
                cp = CollisionPlane(plane)
                newCollisionNode.addSolid(cp)
                lastPlane = plane

        return NodePath(newCollisionNode)

    def makeIntroductionMovie(self, delayDeletes):
        self.notify.debug('----- makeIntroductionMovie')
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'BoardbotBoss.makeIntroductionMovie'))

        track = Parallel()
        # bossAnimTrack = Sequence(
            # ActorInterval(self, 'Ff_speech', startTime=2, duration=10, loop=1),
            # ActorInterval(self, 'Ff_lookRt', duration=3),
            # ActorInterval(self, 'Ff_lookRt', duration=3, startTime=3, endTime=0),
            # ActorInterval(self, 'Ff_neutral', duration=2),
            # ActorInterval(self, 'Ff_speech', duration=7, loop=1))
        # track.append(bossAnimTrack)

        # Cookie bowl
        cookie_bowl = loader.loadModel("phase_13/models/events/apriltoons/boredbot/cc_m_ara_int_otto_prp_plate")
        cookie_bowl.setPos((1.6, 15.3, 3.48))
        cookie_bowl.reparentTo(render)
        cookie_bowl.setScale(0.15)
        cookies = []
        for i in range(0, 3):
            cookies.append(loader.loadModel("phase_5/models/props/cc_m_prp_bat_mouthp_cookie"))
            cookies[i].reparentTo(render)
            cookies[i].setScale(0.15)
        cookies[0].setPos(1.7, 15.3, 3.6)
        cookies[0].setHpr(10, 0, 40)
        cookies[0].setScale(0.15)
        cookies[1].setPos(1.5, 15.4, 3.55)
        cookies[1].setHpr(2, 35, 3.48)
        cookies[1].setScale(0.15)
        cookies[2].setPos(1.57, 15.15, 3.5)
        cookies[2].setHpr(2, -35, 3.48)
        cookies[2].setScale(0.15)
        self.cookieProps = [cookie_bowl] + cookies

        propellerOutSfx = loader.loadSfx('phase_5/audio/sfx/ENC_propeller_out.ogg')
        finalOpenSfx = openSfx = base.loader.loadSfx('phase_3.5/audio/sfx/CHQ_FACT_stomper_small.ogg')
        elevatorOpen = ElevatorUtils.getPartlyOpenInterval(self, self.leftDoor, self.rightDoor, self.openSfx, self.finalOpenSfx, self.elevatorType)
        elevatorClose = ElevatorUtils.getPartlyCloseInterval(self, self.leftDoor, self.rightDoor, self.openSfx, finalOpenSfx, self.elevatorType)
        dialogTrack = Track(
            # Intro
            (0, Sequence(elevatorOpen, elevatorClose, Func(self.dividend_king.addActive))),
            (1, Sequence(ActorInterval(self.ottoman, 'writing-stop'), Func(self.ottoman.loop, 'sit'))),
            (5, Sequence(Func(self.ottoman.hide), Func(self.dividend_king.setChatAbsolute, TTLocalizer.COODialogPageOne[0], CFSpeech | CFTimeout))),
            (8, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageOne[1], CFSpeech | CFTimeout)),
            (14, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageOne[2], CFSpeech | CFTimeout)),
            (20, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageOne[3], CFSpeech | CFTimeout)),
            (26, Func(self.dividend_king.setChatAbsolute, TTLocalizer.COODialogPageOne[4], CFSpeech | CFTimeout)),
            (30, Sequence(Func(base.playSfx, propellerOutSfx), Func(self.dividend_king.removeActive))),
            (36, Sequence(Func(self.ottoman.show), self.openDoors, Func(ElevatorUtils.openDoors, self.leftDoor, self.rightDoor, ElevatorUtils.ELEVATOR_CM))),
            (40, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageOne[5], CFSpeech | CFTimeout)),
            (46, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageOne[6], CFSpeech | CFTimeout)),
            (52, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageOne[7], CFSpeech | CFTimeout)),
            (58, Parallel(Sequence(ActorInterval(self.ottoman, 'writing-start'), Func(self.ottoman.loop, 'writing')),
                          Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageOne[8], CFSpeech | CFTimeout))),

            # New boardbot levels hint
            (90, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTwo[0], CFSpeech | CFTimeout)),
            (94, Sequence(ActorInterval(self.ottoman, 'writing-stop'), Func(self.ottoman.loop, 'sit'))),
            (95, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTwo[1], CFSpeech | CFTimeout)),
            (100, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTwo[2], CFSpeech | CFTimeout)),
            (106, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTwo[3], CFSpeech | CFTimeout)),
            (112, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTwo[4], CFSpeech | CFTimeout)),
            (118, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTwo[5], CFSpeech | CFTimeout)),
            (120, Sequence(ActorInterval(self.ottoman, 'writing-start'), Func(self.ottoman.loop, 'writing'))),

            # Promotion/cog level revamp hint
            (158, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageThree[0], CFSpeech | CFTimeout)),
            (164, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageThree[1], CFSpeech | CFTimeout)),
            (168, Sequence(ActorInterval(self.ottoman, 'writing-stop'), ActorInterval(self.ottoman, 'yawn'), Func(self.ottoman.loop, 'sit'))),
            (170, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageThree[2], CFSpeech | CFTimeout)),
            (176, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageThree[3], CFSpeech | CFTimeout)),
            (182, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageThree[4], CFSpeech | CFTimeout)),
            (190, Sequence(ActorInterval(self.ottoman, 'writing-start'), Func(self.ottoman.loop, 'writing'))),

            # Crystalline joining the company?
            (220, Sequence(ActorInterval(self.ottoman, 'writing-stop'), Func(self.ottoman.loop, 'sit'))),
            (225, Sequence(LerpColorScaleInterval(self.ottoman.specialHead, 2, Vec4(1.0, 0.0, 0.0, 1.0)))),
            (226, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFour[0], CFSpeech | CFTimeout)),
            (230, LerpColorScaleInterval(self.ottoman.specialHead, 1, Vec4(1.0, 1.0, 1.0, 1.0))),
            (232, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFour[1], CFSpeech | CFTimeout)),
            (238, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFour[2], CFSpeech | CFTimeout)),
            (244, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFour[3], CFSpeech | CFTimeout)),
            (250, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFour[4], CFSpeech | CFTimeout)),
            (256, Sequence(ActorInterval(self.ottoman, 'writing-start'), Func(self.ottoman.loop, 'writing'))),

            # Otto ace/aro real?
            (290, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFive[0], CFSpeech | CFTimeout)),
            (292, Sequence(ActorInterval(self.ottoman, 'writing-stop'), Func(self.ottoman.loop, 'sit'))),
            (296, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFive[1], CFSpeech | CFTimeout)),
            (302, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFive[2], CFSpeech | CFTimeout)),
            (308, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFive[3], CFSpeech | CFTimeout)),
            (314, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFive[4], CFSpeech | CFTimeout)),
            (320, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFive[5], CFSpeech | CFTimeout)),
            (326, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFive[6], CFSpeech | CFTimeout)),
            (340, Sequence(ActorInterval(self.ottoman, 'writing-start'), Func(self.ottoman.loop, 'writing'))),

            # Otto misses his brother
            (369, Sequence(ActorInterval(self.ottoman, 'writing-stop'), Func(self.ottoman.loop, 'sit'))),
            (370, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSix[0], CFSpeech | CFTimeout)),
            (376, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSix[1], CFSpeech | CFTimeout)),
            (382, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSix[2], CFSpeech | CFTimeout)),
            (388, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSix[3], CFSpeech | CFTimeout)),
            (394, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSix[4], CFSpeech | CFTimeout)),
            (400, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSix[5], CFSpeech | CFTimeout)),
            (406, Sequence(ActorInterval(self.ottoman, 'writing-start'), Func(self.ottoman.loop, 'writing'))),
            (410, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSix[6], CFSpeech | CFTimeout)),

            # Otto x mary
            (470, Sequence(ActorInterval(self.ottoman, 'writing-stop'), Func(self.ottoman.loop, 'sit'))),
            (480, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSeven[0], CFSpeech | CFTimeout)),
            (486, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSeven[1], CFSpeech | CFTimeout)),
            (492, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSeven[2], CFSpeech | CFTimeout)),
            (498, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSeven[3], CFSpeech | CFTimeout)),
            (504, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSeven[4], CFSpeech | CFTimeout)),
            (512, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSeven[5], CFSpeech | CFTimeout)),
            (518, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSeven[6], CFSpeech | CFTimeout)),
            (521, Sequence(ActorInterval(self.ottoman, 'writing-start'), Func(self.ottoman.loop, 'writing'))),
            (523, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSeven[7], CFSpeech | CFTimeout)),
            (529, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSeven[8], CFSpeech | CFTimeout)),

            # Otto x holly
            (568, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageEight[0], CFSpeech | CFTimeout)),
            (570, Sequence(ActorInterval(self.ottoman, 'writing-stop'), Func(self.ottoman.loop, 'sit'))),
            (576, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageEight[1], CFSpeech | CFTimeout)),
            (582, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageEight[2], CFSpeech | CFTimeout)),
            (588, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageEight[3], CFSpeech | CFTimeout)),
            (594, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageEight[4], CFSpeech | CFTimeout)),
            (600, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageEight[5], CFSpeech | CFTimeout)),
            (606, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageEight[6], CFSpeech | CFTimeout)),
            (612, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageEight[7], CFSpeech | CFTimeout)),
            (618, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageEight[8], CFSpeech | CFTimeout)),
            (625, Sequence(ActorInterval(self.ottoman, 'writing-start'), Func(self.ottoman.loop, 'writing'))),
            (665, ActorInterval(self.ottoman, 'yawn')),
            (667, Sequence(ActorInterval(self.ottoman, 'writing-start'), Func(self.ottoman.loop, 'writing'))),

            # Mary x spruce
            (700, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageNine[0], CFSpeech | CFTimeout)),
            (706, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageNine[1], CFSpeech | CFTimeout)),
            (712, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageNine[2], CFSpeech | CFTimeout)),
            (718, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageNine[3], CFSpeech | CFTimeout)),
            (724, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageNine[4], CFSpeech | CFTimeout)),
            (730, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageNine[5], CFSpeech | CFTimeout)),
            (736, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageNine[6], CFSpeech | CFTimeout)),
            (742, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageNine[7], CFSpeech | CFTimeout)),

            # Spruce (cont.)
            (769, Sequence(ActorInterval(self.ottoman, 'writing-stop'), Func(self.ottoman.loop, 'sit'))),
            (770, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTen[0], CFSpeech | CFTimeout)),
            (776, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTen[1], CFSpeech | CFTimeout)),
            (782, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTen[2], CFSpeech | CFTimeout)),
            (788, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTen[3], CFSpeech | CFTimeout)),
            (794, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTen[4], CFSpeech | CFTimeout)),
            (800, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTen[5], CFSpeech | CFTimeout)),
            (806, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTen[6], CFSpeech | CFTimeout)),
            (812, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTen[7], CFSpeech | CFTimeout)),
            (818, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTen[8], CFSpeech | CFTimeout)),
            (822, Sequence(ActorInterval(self.ottoman, 'writing-start'), Func(self.ottoman.loop, 'writing'))),
            (824, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTen[9], CFSpeech | CFTimeout)),

            # Otto x belle
            (879, Sequence(ActorInterval(self.ottoman, 'writing-stop'), Func(self.ottoman.loop, 'sit'))),
            (880, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageEleven[0], CFSpeech | CFTimeout)),
            (881, LerpPosHprInterval(base.camera, 1, (1.58, 12.7,  5), (0, -25, 0), blendType='easeOut')),
            (886, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageEleven[1], CFSpeech | CFTimeout)),
            (890, LerpPosHprInterval(base.camera, 1, (0, -30, 8), (0, 0, 0), blendType='easeOut')),
            (892, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageEleven[2], CFSpeech | CFTimeout)),
            (898, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageEleven[3], CFSpeech | CFTimeout)),
            (904, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageEleven[4], CFSpeech | CFTimeout)),
            (910, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageEleven[5], CFSpeech | CFTimeout)),
            (920, Sequence(ActorInterval(self.ottoman, 'writing-start'), Func(self.ottoman.loop, 'writing'))),

            # Otto x tawney
            (990, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTwelve[0], CFSpeech | CFTimeout)),
            (996, Sequence(ActorInterval(self.ottoman, 'writing-stop'), Func(self.ottoman.loop, 'sit'))),
            (1000, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTwelve[1], CFSpeech | CFTimeout)),
            (1006, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTwelve[2], CFSpeech | CFTimeout)),
            (1012, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTwelve[3], CFSpeech | CFTimeout)),
            (1018, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTwelve[4], CFSpeech | CFTimeout)),
            (1024, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTwelve[5], CFSpeech | CFTimeout)),
            (1030, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTwelve[6], CFSpeech | CFTimeout)),
            (1036, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTwelve[7], CFSpeech | CFTimeout)),
            (1042, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageTwelve[8], CFSpeech | CFTimeout)),
            (1048, Sequence(ActorInterval(self.ottoman, 'writing-start'), Func(self.ottoman.loop, 'writing'))),

            # Dana and tawney
            (1100, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageThirteen[0], CFSpeech | CFTimeout)),
            (1104, Sequence(ActorInterval(self.ottoman, 'writing-stop'), Func(self.ottoman.loop, 'sit'))),
            (1110, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageThirteen[1], CFSpeech | CFTimeout)),
            (1118, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageThirteen[2], CFSpeech | CFTimeout)),
            (1126, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageThirteen[3], CFSpeech | CFTimeout)),
            (1134, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageThirteen[4], CFSpeech | CFTimeout)),
            (1142, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageThirteen[5], CFSpeech | CFTimeout)),
            (1144, Sequence(ActorInterval(self.ottoman, 'writing-start'), Func(self.ottoman.loop, 'writing'))),

            # Belle and the knitting club
            (1190, Sequence(ActorInterval(self.ottoman, 'writing-stop'), Func(self.ottoman.loop, 'sit'))),
            (1196, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFourteen[0], CFSpeech | CFTimeout)),
            (1202, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFourteen[1], CFSpeech | CFTimeout)),
            (1208, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFourteen[2], CFSpeech | CFTimeout)),
            (1214, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFourteen[3], CFSpeech | CFTimeout)),
            (1220, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFourteen[4], CFSpeech | CFTimeout)),
            (1226, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFourteen[5], CFSpeech | CFTimeout)),
            (1232, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFourteen[6], CFSpeech | CFTimeout)),
            (1238, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFourteen[7], CFSpeech | CFTimeout)),
            (1244, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFourteen[8], CFSpeech | CFTimeout)),
            (1249, Sequence(ActorInterval(self.ottoman, 'writing-start'), Func(self.ottoman.loop, 'writing'))),
            (1254, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFourteen[9], CFSpeech | CFTimeout)),

            # Belle and the big idea
            (1300, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFifteen[0], CFSpeech | CFTimeout)),
            (1303, Sequence(ActorInterval(self.ottoman, 'writing-stop'), Func(self.ottoman.loop, 'sit'))),
            (1308, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFifteen[1], CFSpeech | CFTimeout)),
            (1314, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFifteen[2], CFSpeech | CFTimeout)),
            (1320, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFifteen[3], CFSpeech | CFTimeout)),
            (1326, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFifteen[4], CFSpeech | CFTimeout)),
            (1332, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFifteen[5], CFSpeech | CFTimeout)),
            (1338, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageFifteen[6], CFSpeech | CFTimeout)),
            (1340, Sequence(ActorInterval(self.ottoman, 'writing-start'), Func(self.ottoman.loop, 'writing'))),
            (1375, ActorInterval(self.ottoman, 'yawn')),
            (1377, Sequence(ActorInterval(self.ottoman, 'writing-start'), Func(self.ottoman.loop, 'writing'))),

            # Ending
            (1390, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSixteen[0], CFSpeech | CFTimeout)),
            (1396, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSixteen[1], CFSpeech | CFTimeout)),
            (1400, Sequence(ActorInterval(self.ottoman, 'writing-stop'), Func(self.ottoman.loop, 'sit'))),
            (1406, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSixteen[2], CFSpeech | CFTimeout)),
            (1412, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSixteen[3], CFSpeech | CFTimeout)),
            (1418, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSixteen[4], CFSpeech | CFTimeout)),
            (1424, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSixteen[5], CFSpeech | CFTimeout)),
            (1430, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSixteen[6], CFSpeech | CFTimeout)),
            (1436, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSixteen[7], CFSpeech | CFTimeout)),
            (1442, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSixteen[8], CFSpeech | CFTimeout)),
            (1448, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSixteen[9], CFSpeech | CFTimeout)),
            (1454, Func(self.ottoman.setChatAbsolute, TTLocalizer.COODialogPageSixteen[10], CFSpeech | CFTimeout)),
        )
        radioMusicSequence = Sequence(
            Wait(58), *(Sequence(SoundInterval(song, volume=0.9), Wait(8.3)) for song in self.radioMusic))
        track.append(Parallel(dialogTrack, radioMusicSequence))
        return Sequence(
            Func(self.stickToonsToFloor),
            track,
            Func(self.unstickToons), name=self.uniqueName('Introduction'))

    def walkToonsToBattlePosition(self, toonIds, battleNode):
        self.notify.debug('walkToonsToBattlePosition-----------------------------------------------')
        self.notify.debug('toonIds=%s  battleNode=%s' % (toonIds, battleNode))
        ival = Parallel()
        points = BattleBase.BattleBase.toonPoints[len(toonIds) - 1]
        self.notify.debug('walkToonsToBattlePosition: points = %s' % points[0][0])
        for i in range(len(toonIds)):
            toon = base.cr.doId2do.get(toonIds[i])
            if toon:
                pos, h = points[i]
                origPos = pos
                self.notify.debug('origPos = %s' % origPos)
                self.notify.debug('batlleNode.getTransform = %s  render.getTransform=%s' % (battleNode.getTransform(), render.getTransform()))
                self.notify.debug('render.getScale()=%s  battleNode.getScale()=%s' % (render.getScale(), battleNode.getScale()))
                # myCurPos = self.getPos()
                self.notify.debug('myCurPos = %s' % self.getPos())
                self.notify.debug('battleNode.parent() = %s' % battleNode.getParent())
                self.notify.debug('battleNode.parent().getPos() = %s' % battleNode.getParent().getPos())
                bnParent = battleNode.getParent()
                battleNode.wrtReparentTo(render)
                bnWorldPos = battleNode.getPos()
                battleNode.wrtReparentTo(bnParent)
                self.notify.debug('battle node world pos = %s' % bnWorldPos)
                pos = render.getRelativePoint(battleNode, pos)
                self.notify.debug('walktToonsToBattlePosition: render.getRelativePoint result = %s' % pos)
                self.notify.debug('walkToonsToBattlePosition: final pos = %s' % pos)
                ival.append(Sequence(Func(toon.setPlayRate, 0.8, 'walk'), Func(toon.loop, 'walk'), toon.posInterval(3, pos), Func(toon.setPlayRate, 1, 'walk'), Func(toon.loop, 'neutral')))

        return ival

    def touchedGavel(self, gavel, entry):
        self.notify.debug('touchedGavel')
        attackCodeStr = entry.getIntoNodePath().getNetTag('attackCode')
        if attackCodeStr == '':
            self.notify.warning('Node %s has no attackCode tag.' % repr(entry.getIntoNodePath()))
            return
        attackCode = int(attackCodeStr)
        into = entry.getIntoNodePath()
        self.zapLocalToon(attackCode, into)

    def touchedGavelHandle(self, gavel, entry):
        attackCodeStr = entry.getIntoNodePath().getNetTag('attackCode')
        if attackCodeStr == '':
            self.notify.warning('Node %s has no attackCode tag.' % repr(entry.getIntoNodePath()))
            return
        attackCode = int(attackCodeStr)
        into = entry.getIntoNodePath()
        self.zapLocalToon(attackCode, into)

    def createBlock(self, x1, y1, z1, x2, y2, z2, r = 1.0, g = 1.0, b = 1.0, a = 1.0):
        gFormat = GeomVertexFormat.getV3n3cpt2()
        myVertexData = GeomVertexData('holds my vertices', gFormat, Geom.UHDynamic)
        vertexWriter = GeomVertexWriter(myVertexData, 'vertex')
        normalWriter = GeomVertexWriter(myVertexData, 'normal')
        colorWriter = GeomVertexWriter(myVertexData, 'color')
        texWriter = GeomVertexWriter(myVertexData, 'texcoord')
        vertexWriter.addData3f(x1, y1, z1)
        vertexWriter.addData3f(x2, y1, z1)
        vertexWriter.addData3f(x1, y2, z1)
        vertexWriter.addData3f(x2, y2, z1)
        vertexWriter.addData3f(x1, y1, z2)
        vertexWriter.addData3f(x2, y1, z2)
        vertexWriter.addData3f(x1, y2, z2)
        vertexWriter.addData3f(x2, y2, z2)
        for index in range(8):
            normalWriter.addData3f(1.0, 1.0, 1.0)
            colorWriter.addData4f(r, g, b, a)
            texWriter.addData2f(1.0, 1.0)

        tris = GeomTriangles(Geom.UHDynamic)
        tris.addVertex(0)
        tris.addVertex(1)
        tris.addVertex(2)
        tris.closePrimitive()
        tris.addVertex(1)
        tris.addVertex(3)
        tris.addVertex(2)
        tris.closePrimitive()
        tris.addVertex(2)
        tris.addVertex(3)
        tris.addVertex(6)
        tris.closePrimitive()
        tris.addVertex(3)
        tris.addVertex(7)
        tris.addVertex(6)
        tris.closePrimitive()
        tris.addVertex(0)
        tris.addVertex(2)
        tris.addVertex(4)
        tris.closePrimitive()
        tris.addVertex(2)
        tris.addVertex(6)
        tris.addVertex(4)
        tris.closePrimitive()
        tris.addVertex(1)
        tris.addVertex(5)
        tris.addVertex(3)
        tris.closePrimitive()
        tris.addVertex(3)
        tris.addVertex(5)
        tris.addVertex(7)
        tris.closePrimitive()
        tris.addVertex(0)
        tris.addVertex(4)
        tris.addVertex(5)
        tris.closePrimitive()
        tris.addVertex(1)
        tris.addVertex(0)
        tris.addVertex(5)
        tris.closePrimitive()
        tris.addVertex(4)
        tris.addVertex(6)
        tris.addVertex(7)
        tris.closePrimitive()
        tris.addVertex(7)
        tris.addVertex(5)
        tris.addVertex(4)
        tris.closePrimitive()
        cubeGeom = Geom(myVertexData)
        cubeGeom.addPrimitive(tris)
        cubeGN = GeomNode('cube')
        cubeGN.addGeom(cubeGeom)
        return cubeGN

    def __enterDefenseCol(self, entry):
        self.notify.debug('__enterDefenseCol')

    def __enterProsecutionCol(self, entry):
        self.notify.debug('__enterProsecutionCol')

    def makeVictoryMovie(self):
        paperwork = loader.loadModel('phase_11/models/lawbotHQ/LB_paper_big_stacks3')
        paperwork.setScale(3)
        whistleSfx = base.loader.loadSfx('phase_5/audio/sfx/incoming_whistleALT.ogg')
        dropSfx = base.loader.loadSfx('phase_5/audio/sfx/AA_drop_safe_miss.ogg')
        myFromPos = Point3(BossCogGlobals.LawbotBossBattleThreePosHpr[0], BossCogGlobals.LawbotBossBattleThreePosHpr[1], BossCogGlobals.LawbotBossBattleThreePosHpr[2])
        paperwork.setPos(myFromPos)
        myToPos = Point3(myFromPos[0], myFromPos[1] + 30, myFromPos[2])
        paperPosStart = Point3(myFromPos[0], myFromPos[1] + 30, myFromPos[2]+30)
        paperToPos = Point3(myFromPos[0], myFromPos[1] + 36, myFromPos[2])
        self.rollBossToPoint(fromPos=myFromPos, fromHpr=None, toPos=myToPos, toHpr=None, reverse=0)
        rollTrack = Sequence(
            Func(self.ottoman.setH, 0),
            Func(self.ottoman.loop, 'walk'),
            LerpPosInterval(self.ottoman, 5, Vec3(self.ottoman.getX(), self.ottoman.getY() + 30, self.ottoman.getZ())),
            Func(self.ottoman.loop, 'neutral'),
            Func(self.ottoman.setH, 180))
        rollTrackDuration = rollTrack.getDuration()
        self.notify.debug('rollTrackDuration = %f' % rollTrackDuration)
        doorStartPos = self.door3.getPos()
        doorEndPos = Point3(doorStartPos[0], doorStartPos[1], doorStartPos[2] + 35)
        bossTrack = Track(
            (0.5, Sequence(
                Func(self.ottoman.clearChat),
                Func(base.camera.reparentTo, render),
                Func(base.camera.setPos, -3, 45, 25),
                Func(base.camera.setHpr, 0, 10, 0))),
            (1.0, Func(self.ottoman.setChatAbsolute, TTLocalizer.LawbotBossDefenseWins1, CFSpeech)),
            (5.5, Func(self.ottoman.setChatAbsolute, TTLocalizer.LawbotBossDefenseWins2, CFSpeech)),
            (9.5, Sequence(Func(base.camera.wrtReparentTo, render))),
            (9.6, Parallel(
                rollTrack,
                Func(self.ottoman.setChatAbsolute, TTLocalizer.LawbotBossDefenseWins3, CFSpeech),
                self.door3.posInterval(2, doorEndPos, startPos=doorStartPos))),
            (13.1, Sequence(Parallel(SoundInterval(whistleSfx),
                   Sequence(
                       Func(self.ottoman.setChatAbsolute, TTLocalizer.LawbotBossDefenseWins4, CFSpeech),
                       LerpScaleInterval(self.dropShadow, 3, Point3(15, 15, 15)),
                       Func(paperwork.reparentTo, render),
                       Parallel(LerpPosInterval(paperwork, 0.1, paperToPos, startPos = paperPosStart),
                       SoundInterval(dropSfx),
                       Func(self.ottoman.stash)),
                       Func(paperwork.detachNode))))),
            (17, Sequence(self.door3.posInterval(1, doorStartPos))))
        # retTrack = Parallel(bossTrack, ActorInterval(self, 'Ff_speech', loop=1))
        return bossTrack

    def makeEpilogueMovie(self):
        epSpeech = TTLocalizer.WitnessToonCongratulations
        epSpeech = self.__talkAboutPromotion(epSpeech)
        bossTrack = Sequence(Func(self.witnessToon.request, 'Neutral'), Func(self.witnessToon.setLocalPageChat, epSpeech, 0))
        return bossTrack

    def makeDefeatMovie(self):
        bossTrack = Track((0.0, Sequence(Func(self.ottoman.clearChat), Func(self.reverseHead), Func(self.ottoman.loop, 'victory'))), (1.0, Func(self.ottoman.setChatAbsolute, TTLocalizer.LawbotBossProsecutionWins, CFSpeech)))
        return bossTrack

    def __makeWitnessToon(self):
        self.witnessToon = NPCToons.createLocalNPC(2009)
        self.witnessToon.addActive()
        self.witnessToon.request('Sit')
        self.witnessToon.setName(TTLocalizer.WitnessToonName)
        self.witnessToon.setPickable(0)
        self.witnessToon.setPlayerType(CCNonPlayer)
        self.witnessToon.setPosHpr(*ToontownGlobals.LawbotBossWitnessStandPosHpr)

    def __cleanupWitnessToon(self):
        self.__hideWitnessToon()
        if self.witnessToon:
            self.witnessToon.removeActive()
            self.witnessToon.delete()
            self.witnessToon = None
        return

    def __showWitnessToon(self):
        if not self.witnessToonOnstage:
            self.witnessToon.addActive()
            self.witnessToon.reparentTo(self.geom)
            seatCenter = self.realWitnessStand.find('**/witnessStandSeatEdge')
            center = seatCenter.getPos()
            self.notify.debug('center = %s' % center)
            self.witnessToon.setPos(center)
            self.witnessToon.setH(180)
            self.witnessToon.setZ(self.witnessToon.getZ() - 1.5)
            self.witnessToon.setY(self.witnessToon.getY() - 1.15)
            self.witnessToonOnstage = 1

    def __hideWitnessToon(self):
        if self.witnessToonOnstage:
            self.witnessToon.removeActive()
            self.witnessToon.detachNode()
            self.witnessToonOnstage = 0

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

    def __arrangeToonsAroundWitnessToon(self):
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
            newCogSuitReviveLevel = localAvatar.getCogReviveLevels()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
            newCogSuitType = localAvatar.getCogTypes()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
            if newCogSuitLevel == ToontownGlobals.MaxCogSuitLevel:
                speech += TTLocalizer.WitnessToonLastPromotion % (ToontownGlobals.MaxCogSuitLevel + 1)
            if newCogSuitLevel in ToontownGlobals.CogSuitHPLevels and newCogSuitType != 6:
                speech += TTLocalizer.WitnessToonHPBoost
            if newCogSuitReviveLevel == ToontownGlobals.MaxCogSuitLevel:
                speech += TTLocalizer.WitnessToonLastRevivePromotion % (ToontownGlobals.MaxCogSuitLevel + 1)
            if newCogSuitReviveLevel in ToontownGlobals.CogReviveSuitHPLevels and newCogSuitReviveLevel != self.prevCogSuitReviveLevel:
                speech += TTLocalizer.WitnessToonHPBoost
            if self.prevCogSuitType != 4 and newCogSuitType == 4:
                speech += TTLocalizer.WitnessToonTeleportAccess
        else:
            speech += TTLocalizer.WitnessToonMaxed % (ToontownGlobals.MaxCogSuitLevel + 1)
        return speech

    def __positionToonsInFrontOfCannons(self):
        self.notify.debug('__positionToonsInFrontOfCannons')
        index = 0
        for toonId in self.involvedToons:
            if index in self.cannons:
                cannon = self.cannons[index]
                toon = self.cr.doId2do.get(toonId)
                self.notify.debug('cannonId = %d' % cannon.doId)
                cannonPos = cannon.nodePath.getPos(render)
                self.notify.debug('cannonPos = %s' % cannonPos)
                if toon:
                    self.notify.debug('toon = %s' % toon.getName())
                    toon.reparentTo(cannon.nodePath)
                    toon.setPos(0, 8, 0)
                    toon.setH(180)
                    renderPos = toon.getPos(render)
                    self.notify.debug('renderPos =%s' % renderPos)
                    index += 1

        self.notify.debug('done with positionToons')

    def __makePrepareBattleTwoMovie(self):
        chatString = TTLocalizer.WitnessToonPrepareBattleTwo % ToontownGlobals.LawbotBossJurorsForBalancedScale
        movie = Sequence(Func(base.camera.reparentTo, self.witnessToon), Func(base.camera.setPos, 0, 8, 2), Func(base.camera.setHpr, 180, 10, 0), Func(self.witnessToon.setLocalPageChat, chatString, 0))
        return movie

    def __doWitnessPrepareBattleThreeChat(self):
        self.notify.debug('__doWitnessPrepareBattleThreeChat: original self.numToonJurorsSeated = %d' % self.numToonJurorsSeated)
        self.countToonJurors()
        self.notify.debug('after calling self.countToonJurors, numToonJurorsSeated=%d' % self.numToonJurorsSeated)
        if self.numToonJurorsSeated == 0:
            juryResult = TTLocalizer.WitnessToonNoJuror
        elif self.numToonJurorsSeated == 1:
            juryResult = TTLocalizer.WitnessToonOneJuror
        elif self.numToonJurorsSeated == 12:
            juryResult = TTLocalizer.WitnessToonAllJurors
        else:
            juryResult = TTLocalizer.WitnessToonSomeJurors % self.numToonJurorsSeated
        juryResult += '\x07'
        trialSpeech = juryResult
        trialSpeech += TTLocalizer.WitnessToonPrepareBattleThree % base.PRIMARY_KEY.upper()
        diffSettings = ToontownGlobals.LawbotBossDifficultySettings[self.battleDifficulty]
        if diffSettings[4]:
            newWeight, self.bonusWeight, self.numJurorsLocalToonSeated = self.calculateWeightOfToon(base.localAvatar.doId)
            if self.bonusWeight > 0:
                if self.bonusWeight == 1:
                    juryWeightBonus = TTLocalizer.WitnessToonJuryWeightBonusSingular.get(self.battleDifficulty)
                else:
                    juryWeightBonus = TTLocalizer.WitnessToonJuryWeightBonusPlural.get(self.battleDifficulty)
                if juryWeightBonus:
                    weightBonusText = juryWeightBonus % (self.numJurorsLocalToonSeated, self.bonusWeight)
                    trialSpeech += '\x07'
                    trialSpeech += weightBonusText
        self.witnessToon.setLocalPageChat(trialSpeech, 0)

    def __makePrepareBattleThreeMovie(self):
        movie = Sequence(Func(base.camera.reparentTo, render), Func(base.camera.setPos, -15, 15, 20), Func(base.camera.setHpr, -90, 0, 0), Wait(3), Func(base.camera.reparentTo, self.witnessToon), Func(base.camera.setPos, 0, 8, 2), Func(base.camera.setHpr, 180, 10, 0), Func(self.__doWitnessPrepareBattleThreeChat))
        return movie

    def countToonJurors(self):
        self.numToonJurorsSeated = 0
        for key in list(self.chairs.keys()):
            chair = self.chairs[key]
            if chair.state == 'ToonJuror' or chair.state is None and chair.newState == 'ToonJuror':
                self.numToonJurorsSeated += 1

        self.notify.debug('self.numToonJurorsSeated = %d' % self.numToonJurorsSeated)
        return

    def cleanupPanFlash(self):
        if self.panFlashInterval:
            self.panFlashInterval.finish()
            self.panFlashInterval = None
        return

    def flashPanBlue(self):
        self.cleanupPanFlash()
        intervalName = 'FlashPanBlue'
        self.defensePanNodePath.setColorScale(1, 1, 1, 1)
        seq = Sequence(self.defensePanNodePath.colorScaleInterval(0.1, colorScale=VBase4(0, 0, 1, 1)), self.defensePanNodePath.colorScaleInterval(0.3, colorScale=VBase4(1, 1, 1, 1)), name=intervalName)
        self.panFlashInterval = seq
        seq.start()
        self.storeInterval(seq, intervalName)

    def saySomething(self, chatString):
        intervalName = 'ChiefJusticeTaunt'
        seq = Sequence(name=intervalName)
        seq.append(Func(self.ottoman.setChatAbsolute, chatString, CFSpeech))
        seq.append(Wait(4.0))
        seq.append(Func(self.ottoman.clearChat))
        oldSeq = self.activeIntervals.get(intervalName)
        if oldSeq:
            oldSeq.finish()
        seq.start()
        self.storeInterval(seq, intervalName)

    def setTaunt(self, tauntIndex, extraInfo):
        gotError = False
        if not hasattr(self, 'state'):
            self.notify.warning('returning from setTaunt, no attr state')
            gotError = True
        elif not self.state == 'BattleThree':
            self.notify.warning('returning from setTaunt, not in battle three state, state=%s', self.state)
            gotError = True
        if not hasattr(self, 'nametag'):
            self.notify.warning('returning from setTaunt, no attr nametag')
            gotError = True
        if gotError:
            return
        chatString = TTLocalizer.LawbotBossTaunts[1]
        if tauntIndex == 0:
            if extraInfo < len(self.involvedToons):
                toonId = self.involvedToons[extraInfo]
                toon = base.cr.doId2do.get(toonId)
                if toon:
                    chatString = TTLocalizer.LawbotBossTaunts[tauntIndex] % toon.getName()
        else:
            chatString = TTLocalizer.LawbotBossTaunts[tauntIndex]
        self.saySomething(chatString)

    def toonGotHealed(self, toonId):
        toon = base.cr.doId2do.get(toonId)
        if toon:
            base.playSfx(self.toonUpSfx, node=toon)

    def toonDied(self, avId):
        DistributedBossCog.DistributedBossCog.toonDied(self, avId)

        # If our toon died, get rid of the dept exp bar
        if avId == base.localAvatar.doId:
            if self.departmentExpBar:
                self.departmentExpBar.hide()
                self.departmentExpBar.stop()
                self.departmentExpBar.destroy()
            base.cr.gameGui.expBar.show()

    def hideBonusTimer(self):
        if self.bonusTimer:
            timerSeq = Sequence(
                Func(self.bonusTimer.popHide, 0.2),
                Func(self.bonusTimer.hide)
            )
            timerSeq.start()
        self.enteredCooldownState()

    def hideCooldownTimer(self):
        try:
            if self.cooldownTimer:
                timerSeq = Sequence(
                    Func(self.cooldownTimer.popHide, 0.2),
                    Wait(0.2),
                    Func(self.healthGui.moveBackFromAvPanel),
                )
                timerSeq.start()
            else:
                self.healthGui.moveBackFromAvPanel()
        except Exception:
            self.notify.debug("Can't move health bar, CJ Ended")


    def enteredBonusState(self):
        self.witnessToon.clearChat()
        text = TTLocalizer.WitnessToonBonus % (2, ToontownGlobals.LawbotBossBonusDuration)
        self.witnessToon.setChatAbsolute(text, CFSpeech | CFTimeout)
        base.playSfx(self.toonUpSfx)
        timerSeq = Sequence(
            Func(self.healthGui.moveForAvPanel),
            Wait(0.2),
            Func(self.bonusTimer.popShow, 0.2, ToontownGlobals.LawbotBossBonusDuration, self.hideBonusTimer),
        )
        timerSeq.start()

    def enteredCooldownState(self):
        self.witnessToon.clearChat()
        text = TTLocalizer.WitnessToonCooldown
        self.witnessToon.setChatAbsolute(text, CFSpeech | CFTimeout)
        self.cooldownTimer.setFontColor(Vec4(0, 0.63, 1, 1))
        timerSeq = Sequence(
            Func(self.cooldownTimer.popShow, 0.2, ToontownGlobals.LawbotBossBonusWaitTime - ToontownGlobals.LawbotBossBonusDuration, self.hideCooldownTimer),
        )
        timerSeq.start()

    def setAttackCode(self, attackCode, avId = 0):
        DistributedBossCog.DistributedBossCog.setAttackCode(self, attackCode, avId)
        if attackCode == BossCogGlobals.BossCogAreaAttack:
            self.saySomething(TTLocalizer.LawbotBossAreaAttackTaunt)
            base.playSfx(self.warningSfx)

    def announceAreaAttack(self):
        self.jumpTime.tick()
        self.jumpFullTime += self.jumpTime.getDt()
        if self.jumpFullTime < 1.1:
            return

    def setBattleDifficulty(self, diff):
        self.notify.debug('battleDifficulty = %d' % diff)
        self.battleDifficulty = diff

    def toonEnteredCannon(self, toonId, cannonIndex):
        if base.localAvatar.doId == toonId:
            self.cannonIndex = cannonIndex

    def numJurorsSeatedByCannon(self, cannonIndex):
        retVal = 0
        for chair in list(self.chairs.values()):
            if chair.state == 'ToonJuror':
                if chair.toonJurorIndex == cannonIndex:
                    retVal += 1

        return retVal

    def calculateWeightOfToon(self, toonId):
        defaultWeight = 1
        bonusWeight = 0
        newWeight = 1
        cannonIndex = self.cannonIndex
        numJurors = 0
        if cannonIndex is None and cannonIndex >= 0:
            diffSettings = ToontownGlobals.LawbotBossDifficultySettings[self.battleDifficulty]
            if diffSettings[4]:
                numJurors = self.numJurorsSeatedByCannon(cannonIndex)
                bonusWeight = numJurors - diffSettings[5]
                if bonusWeight < 0:
                    bonusWeight = 0
            newWeight = defaultWeight + bonusWeight
            self.notify.debug('toon %d has weight of %d' % (toonId, newWeight))
        return (newWeight, bonusWeight, numJurors)
