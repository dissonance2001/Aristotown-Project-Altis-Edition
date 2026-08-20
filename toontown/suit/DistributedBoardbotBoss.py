from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from direct.directutil import Mopath
from direct.distributed.ClockDelta import *
from direct.fsm import ClassicFSM, State
from direct.fsm import FSM
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from toontown.toonbase.ToonPythonUtil import Functor
from direct.showutil import Rope
from direct.task import Task
from toontown.building import ElevatorConstants
import math
from toontown.friends import FriendsListManager
from toontown.nametag import NametagGlobals
from toontown.toon import Toon
from toontown.toon import ToonDNA
from toontown.nametag import NametagGroup
from pandac.PandaModules import *
import random
from toontown.suit import DistributedBossCog
from toontown.suit import SuitDNA
from toontown.suit import FourBossBattleGlobals
from toontown.battle import BattleBase
from toontown.battle import BattleParticles
from toontown.battle import MovieToonVictory
from toontown.battle import RewardPanel
from toontown.battle import SuitBattleGlobals
from toontown.battle.BattleProps import *
from toontown.chat.ChatGlobals import *
from toontown.suit import BossCog
from toontown.coghq import CogDisguiseGlobals
from toontown.distributed import DelayDelete
from toontown.nametag.NametagGlobals import *
from toontown.suit import SellbotBossGlobals
from toontown.toon import NPCToons
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import ToontownGlobals
from six.moves import range

OneBossCog = None

class DistributedBoardbotBoss(DistributedBossCog.DistributedBossCog, FSM.FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedBoardbotBoss')


    cageHeights = [25,
     15,
     0,
     -15,
     -25,
     -50]

    def __init__(self, cr):
        DistributedBossCog.DistributedBossCog.__init__(self, cr)
        FSM.FSM.__init__(self, 'DistributedBoardbotBoss')
        self.elevatorType = ElevatorConstants.ELEVATOR_BB
        self.cagedToonNpcId = None
        self.doobers = []
        self.dooberRequest = None
        self.bossDamage = 0
        self.currHP = self.bossDamage
        self.attackCode = None
        self.attackAvId = 0
        self.recoverRate = 0
        self.recoverStartTime = 0
        self.bossDamageMovie = None
        self.cagedToon = None
        self.cageShadow = None
        self.cioBoss = None
        self.cpoBoss = None
        self.vpBoss = None
        self.cfoBoss = None
        self.cjBoss = None
        self.ceoBoss = None
        self.cjBoss2 = None
        self.cageIndex = 0
        self.everThrownPie = 0
        self.battleThreeMusicTime = 0
        self.insidesANodePath = None
        self.insidesBNodePath = None
        self.elevatorEntrance = None
        self.elevatorChairman = None
        self.paperStack1 = None
        self.paperStack2 = None
        self.meetingTable = None
        self.tableEnclosureColl = None
        self.presentation = None
        self.strafeInterval = None
        self.onscreenMessage = None
        self.chandeliers = []
        self.bookshelves = []
        self.geomProps = []
        self.cagedToons = []
        self.toonMopathInterval = []
        self.nerfed = ToontownGlobals.SELLBOT_NERF_HOLIDAY in base.cr.newsManager.getHolidayIdList()
        self.localToonPromoted = True
        self.resetMaxDamage()
        self.maxHP = self.bossMaxDamage

        from toontown.suit.DistributedSuitBase import DistributedSuitBase
        self.contingency = DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('cdirector')
        self.contingency.setDNA(suitDNA)
        self.contingency.setPickable(0)
        self.contingency.setDisplayName('Contingency Director\nBoardbot\nLevel 66.mgr')
        self.contingency.doId = 0
        self.contingency.loop('neutral')
        self.contingency.reparentTo(render)
        self.contingency.setPosHpr(0, -131.321, 0, 180.0, 0.0, 0.0)

        self.dividend = DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('dking')
        self.dividend.setDNA(suitDNA)
        self.dividend.setPickable(0)
        self.dividend.setDisplayName('Dividend King\nBoardbot\nLevel 60.mgr')
        self.dividend.doId = 0
        self.dividend.loop('sit-exec')
        self.dividend.reparentTo(render)
        self.dividend.setPosHpr(49.844, -80.266, 2.5, 180.0, 0.0, 0.0)

        self.recordkeeper = DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('rkeeper')
        self.recordkeeper.setDNA(suitDNA)
        self.recordkeeper.setPickable(0)
        self.recordkeeper.setDisplayName('Recordkeeper\nBoardbot\nLevel 60.mgr')
        self.recordkeeper.doId = 0
        self.recordkeeper.loop('sit-exec')
        self.recordkeeper.reparentTo(render)
        self.recordkeeper.setPosHpr(-82.031, -80.266, 2.5, 180.0, 0.0, 0.0)

        self.tollmaster = DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('liquid')
        self.tollmaster.setDNA(suitDNA)
        self.tollmaster.setPickable(0)
        self.tollmaster.setDisplayName('Tollmaster\nBoardbot\nLevel 56.mgr')
        self.tollmaster.doId = 0
        self.tollmaster.loop('sit-exec')
        self.tollmaster.reparentTo(render)
        self.tollmaster.setPosHpr(-53.594, -80.266, 2.5, 180.0, 0.0, 0.0)

    def announceGenerate(self):
        global OneBossCog
        DistributedBossCog.DistributedBossCog.announceGenerate(self)
        self.setName('Chairman')
        nameInfo = TTLocalizer.BossCogNameWithDept % {'name': self.name,
         'dept': SuitDNA.getDeptFullname(self.style.dept)}
        self.setDisplayName(nameInfo)
        self.cageDoorSfx = loader.loadSfx('phase_5/audio/sfx/CHQ_SOS_cage_door.ogg')
        self.cageLandSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_cage_land.ogg')
        self.cageLowerSfx = loader.loadSfx('phase_5/audio/sfx/CHQ_SOS_cage_lower.ogg')
        self.piesRestockSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_pies_restock.ogg')
        self.rampSlideSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_ramp_slide.ogg')
        self.strafeSfx = []
        for i in range(10):
            self.strafeSfx.append(loader.loadSfx('phase_3.5/audio/sfx/SA_shred.ogg'))

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
        shieldNodePath = self.pelvis.attachNewNode(shieldNode)
        disk = loader.loadModel('phase_9/models/char/bossCog-gearCollide')
        disk.find('**/+CollisionNode').setName('BossZap')
        disk.reparentTo(self.pelvis)
        disk.setZ(0.8)
        self.loadEnvironment()
        self.__makeCagedToon()
        self.__loadMopaths()
        if OneBossCog is not None:
            self.notify.warning('Multiple BossCogs visible.')
        OneBossCog = self

    def disable(self):
        global OneBossCog
        DistributedBossCog.DistributedBossCog.disable(self)
        self.request('Off')
        self.unloadEnvironment()
        self.__unloadMopaths()
        self.__cleanupCagedToon()
        self.__clearOnscreenMessage()
        taskMgr.remove(self.uniqueName('PieAdvice'))
        self.__cleanupStrafe()
        render.clearTag('pieCode')
        self.targetNodePath.detachNode()
        self.cr.relatedObjectMgr.abortRequest(self.dooberRequest)
        self.dooberRequest = None
        self.betweenBattleMusic.stop()
        self.promotionMusic.stop()
        self.stingMusic.stop()
        self.battleTwoMusic.stop()
        self.battleThreeMusic.stop()
        self.epilogueMusic.stop()
        while len(self.toonMopathInterval):
            toonMopath = self.toonMopathInterval[0]
            toonMopath.finish()
            toonMopath.destroy()
            self.toonMopathInterval.remove(toonMopath)

        if OneBossCog == self:
            OneBossCog = None

    def resetMaxDamage(self):
        if self.nerfed:
            self.bossMaxDamage = ToontownGlobals.SellbotBossMaxDamageNerfed
        else:
            self.bossMaxDamage = ToontownGlobals.SellbotBossMaxDamage

    def d_hitBoss(self, bossDamage):
        self.sendUpdate('hitBoss', [bossDamage])

    def d_hitBossInsides(self):
        self.sendUpdate('hitBossInsides', [])

    def d_hitToon(self, toonId):
        self.sendUpdate('hitToon', [toonId])

    def setCagedToonNpcId(self, npcId):
        self.cagedToonNpcId = npcId

    def gotToon(self, toon):
        stateName = self.state
        if stateName == 'Elevator':
            self.placeToonInElevator(toon)

    def setDooberIds(self, dooberIds):
        self.doobers = []
        self.cr.relatedObjectMgr.abortRequest(self.dooberRequest)
        self.dooberRequest = self.cr.relatedObjectMgr.requestObjects(dooberIds, allCallback=self.__gotDoobers)

    def __gotDoobers(self, doobers):
        self.dooberRequest = None
        self.doobers = doobers

    def setBossDamage(self, bossDamage, recoverRate, timestamp):
        recoverStartTime = globalClockDelta.networkToLocalTime(timestamp)
        self.bossDamage = bossDamage
        self.recoverRate = recoverRate
        self.recoverStartTime = recoverStartTime
        taskName = 'RecoverBossDamage'
        taskMgr.remove(taskName)
        if self.bossDamageMovie:
            if self.bossDamage >= self.bossMaxDamage:
                self.bossDamageMovie.resumeUntil(self.bossDamageMovie.getDuration())
            else:
                self.bossDamageMovie.resumeUntil(self.bossDamage * self.bossDamageToMovie)
                if self.recoverRate:
                    taskMgr.add(self.__recoverBossDamage, taskName)
        self.updateHealthBar()

    def getBossDamage(self):
        now = globalClock.getFrameTime()
        elapsed = now - self.recoverStartTime
        return max(self.bossDamage - self.recoverRate * elapsed / 60.0, 0)

    def __recoverBossDamage(self, task):
        self.bossDamageMovie.setT(self.getBossDamage() * self.bossDamageToMovie)
        return Task.cont

    def __makeCagedToon(self):
        if self.cagedToon:
            return
        self.cagedToon = NPCToons.createLocalNPC(self.cagedToonNpcId)
        self.cagedToon.addActive()
        self.cagedToon.reparentTo(self.cage)
        self.cagedToon.setPosHpr(3, 6.0, 52.400, 0.0, 0.0, 0.0)
        self.cagedToon.loop('neutral')
        self.cagedToon.setActiveShadow(0)
        touch = CollisionPolygon(
            Point3(-3.0382, 3.0382, -1), Point3(3.0382, 3.0382, -1),
            Point3(3.0382, -3.0382, -1), Point3(-3.0382, -3.0382, -1))
        touch.setTangible(0)
        touchNode = CollisionNode('Cage')
        touchNode.setCollideMask(ToontownGlobals.WallBitmask)
        touchNode.addSolid(touch)
        self.cage.attachNewNode(touchNode)

    def __cleanupCagedToon(self):
        if self.cagedToon:
            self.cagedToon.removeActive()
            self.cagedToon.delete()
            self.cagedToon = None

    def __walkToonToPromotion(self, toonId, delay, mopath, track, delayDeletes):
        toon = base.cr.doId2do.get(toonId)
        if toon:
            destPos = toon.getPos()
            self.placeToonInElevator(toon)
            toon.wrtReparentTo(render)
            walkMopath = MopathInterval(mopath, toon)
            ival = Sequence(Wait(delay), Func(toon.suit.setPlayRate, 1, 'walk'), Func(toon.suit.loop, 'walk'), toon.posInterval(1, Point3(0, 90, 20)), ParallelEndTogether(walkMopath, toon.posInterval(2, destPos, blendType='noBlend')), Func(toon.suit.loop, 'neutral'))
            self.toonMopathInterval.append(walkMopath)
            track.append(ival)
            delayDeletes.append(DelayDelete.DelayDelete(toon, 'SellbotBoss.__walkToonToPromotion'))

    def __walkDoober(self, suit, delay, turnPos, track, delayDeletes):
        turnPos = Point3(*turnPos)
        turnPosDown = Point3(*ToontownGlobals.SellbotBossDooberTurnPosDown)
        flyPos = Point3(*ToontownGlobals.SellbotBossDooberFlyPos)
        seq = Sequence(Func(suit.headsUp, turnPos), Wait(delay), Func(suit.loop, 'walk', 0), self.__walkSuitToPoint(suit, suit.getPos(), turnPos), self.__walkSuitToPoint(suit, turnPos, turnPosDown), self.__walkSuitToPoint(suit, turnPosDown, flyPos), suit.beginSupaFlyMove(flyPos, 0, 'flyAway'), Func(suit.fsm.request, 'Off'))
        track.append(seq)
        delayDeletes.append(DelayDelete.DelayDelete(suit, 'SellbotBoss.__walkDoober'))

    def __walkSuitToPoint(self, node, fromPos, toPos):
        vector = Vec3(toPos - fromPos)
        distance = vector.length()
        time = distance / (ToontownGlobals.SuitWalkSpeed * 1.8)
        return Sequence(Func(node.setPos, fromPos), Func(node.headsUp, toPos), node.posInterval(time, toPos))

    def makeIntroductionMovie(self, delayDeletes):
        track = Parallel()
        camera.reparentTo(render)
        rightDoors = render.findAllMatches('**/rightDoor')
        leftDoors = render.findAllMatches('**/leftDoor')
        localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        loseSuitCamAngle = (0, 19, 6, -180, 0, 0)
        bossTrack = Sequence(Func(self.loop, 'Ff_neutral'), self.loseCogSuits(self.toonsA + self.toonsB, render, (0, -161.321, 5, 180, 0.0, 0.0)),
                             Parallel(LerpPosHprInterval(base.camera, 2.0, (0, -161.321, 10), (0, 0.0, 0.0),  blendType='easeInOut'),
                             Sequence(Wait(4.0)),
                                      Func(self.contingency.setChatAbsolute, "Well well... this is unexpected.", CFSpeech | CFTimeout)), Wait(4.0),
                                      Func(self.contingency.setChatAbsolute, "You've made quite the series of poor decisions.", CFSpeech | CFTimeout), Wait(4.0),
                                      Func(self.contingency.setChatAbsolute, "You've disrupted our departments, damaged our operations, and interfered with corporate productivity!", CFSpeech | CFTimeout), ActorInterval(self.contingency, 'speak'),
                             Func(self.contingency.loop, 'neutral'),
                                      Func(self.contingency.setChatAbsolute, "Fortunately... my team specializes in dealing with such unexpected complications.", CFSpeech | CFTimeout), Wait(4.0),
                                      Func(self.contingency.setChatAbsolute, "But first...", CFSpeech | CFTimeout), Wait(4.0),
                                      Func(self.contingency.setChatAbsolute, "The board is currently in session.", CFSpeech | CFTimeout), Wait(2.0),
                                      Parallel(Sequence(ActorInterval(self.contingency, 'walk'), Func(self.contingency.loop, 'neutral')),
                                               LerpHprInterval(self.contingency, self.contingency.getDuration('walk'), (0, 0, 0), blendType='easeInOut')),
                                      Func(self.contingency.setChatAbsolute, "How about we bring this matter directly to them!", CFSpeech | CFTimeout), Wait(3.0),
                             Func(self.loop, 'Ff_speech'),
                             Func(self.setChatAbsolute, "Let the record show that the executive board of C.O.G.S. Inc. is now in session.", CFSpeech | CFTimeout),
                             LerpPosHprInterval(base.camera, 0.0, (0, -37.5721, 60), (0, -20, 0), blendType='easeInOut'),
                             Wait(4.0),
                             Func(self.setChatAbsolute, "Reports indicate the Toons have begun interfering with multiple corporate divisions.", CFSpeech | CFTimeout),
                             LerpPosHprInterval(base.camera, 4.0, (-102.322, -3.0205, 60), (-62.2962, -20, 0), blendType='easeInOut'),
                             Func(self.setChatAbsolute, "Such disruptions are unacceptable!", CFSpeech | CFTimeout),
                             Wait(4.0),
                             Func(self.setChatAbsolute, "We will discuss the necessary measures to correct this situation.", CFSpeech | CFTimeout),
                             LerpPosHprInterval(base.camera, 4.0, (0, -27.5721, 60), (0, -20, 0), blendType='easeInOut'),
                             Func(self.setChatAbsolute, "Now then... Let's review the situation.", CFSpeech | CFTimeout),
                             Wait(4.0),
                             Func(self.setChatAbsolute, "Where do we stand against these... Toons?", CFSpeech | CFTimeout),
                             LerpPosHprInterval(base.camera, 4.0, (24.8814, 55.2589, 45), (-50.0743, 0, 0), blendType='easeInOut'),
                             Func(self.loop, 'Ff_neutral'),
                             LerpPosHprInterval(base.camera, 3.0, (5.9252, 39.0836, 43), (-90, -0, 0), blendType='easeInOut'),
                             Sequence(Func(self.cfoBoss.loop, 'Ff_speech')),
                             Func(self.cfoBoss.setChatAbsolute, "Revenue losses from Toon interference have exceeded projections.", CFSpeech | CFTimeout), Wait(4.0), Func(self.cfoBoss.loop, 'Ff_neutral'),
                             Func(base.camera.setPosHpr, -2.410, 31.641, 37.078, 71.8, 5.34, 0.0),
                            Parallel(Sequence(ActorInterval(self.vpBoss, 'Ff_lookRt'), ActorInterval(self.vpBoss, 'Ff_lookRt', startTime=self.vpBoss.getDuration('Ff_lookRt'), endTime=0), Func(self.vpBoss.loop, 'Ff_neutral')),
                                     Func(self.vpBoss.setChatAbsolute, "My sales force is being flattened out there.", CFSpeech | CFTimeout)),
                             Func(base.camera.setPosHpr, 13.761, 34.660, 39.585, 27.2, 4.38, 0.0),
                             Func(self.ceoBoss.setChatAbsolute, "Then hire more.", CFSpeech | CFTimeout), Wait(4.0),
                             Func(base.camera.setPosHpr, 5.9252, 39.0836, 43, -90, -0, 0),
                             Func(self.cfoBoss.setChatAbsolute, "Hiring requires money!", CFSpeech | CFTimeout), Wait(4.0),
                             Func(base.camera.setPosHpr, -2.410, 31.641, 37.078, 71.8, 5.34, 0.0),
                             Func(self.vpBoss.setChatAbsolute, "Which we're losing by the way...", CFSpeech | CFTimeout), Wait(4.0),
                             Func(base.camera.setPosHpr, 45.081, 40.301, 36.134, 35.3, -0.4, 0.0),
                             Parallel(Sequence(ActorInterval(self.cjBoss, 'Ff_cross_arms_into'), Func(self.cjBoss.loop, 'Ff_cross_arms_loop')),
                                      Func(self.cjBoss.setChatAbsolute, "I can hear the disruption spreading across the organization.", CFSpeech | CFTimeout)), Wait(4.0),
                             Func(self.cjBoss.setChatAbsolute, "Chaos leaves a very... distinct sound.", CFSpeech | CFTimeout), Wait(4.0),
                             Func(base.camera.setPosHpr, -27.6814, 50.6378, 43, -325, 0, 0.0),
                             Parallel(Sequence(ActorInterval(self.cjBoss2, 'Ff_speech'), Func(self.cjBoss2.loop, 'Ff_neutral')),
                                      Func(self.cjBoss2.setChatAbsolute, "That's why I came out of retirement.", CFSpeech | CFTimeout)),
                             Func(self.cjBoss2.setChatAbsolute, "Someone needs to ensure the law is properly enforced.", CFSpeech | CFTimeout), Wait(4.0),
                             Func(base.camera.setPosHpr, 5.9252, 39.0836, 43, -90, -0, 0),
                             Parallel(Func(self.cfoBoss.setChatAbsolute, "Didn't the board say your courtroom was... ineffective?", CFSpeech | CFTimeout), Sequence(ActorInterval(self.cfoBoss, 'Ff_lookRt'),
                                                                                                                                                       ActorInterval(self.cfoBoss, 'Ff_lookRt', playRate=-1),
                                                                                                                                                       Func(self.cfoBoss.loop, 'Ff_neutral'))),
                             Func(base.camera.setPosHpr, -27.6814, 50.6378, 43, -325, 0, 0.0),
                             Func(self.cjBoss2.setChatAbsolute, "The board said my methods were outdated.", CFSpeech | CFTimeout), Wait(4.0),
                             Func(base.camera.setPosHpr, 45.081, 40.301, 36.134, 35.3, -0.4, 0.0),
                             Func(self.cjBoss.setChatAbsolute, "And inefficient.", CFSpeech | CFTimeout), Wait(4.0),
                             Func(base.camera.setPosHpr, -27.6814, 50.6378, 43, -325, 0, 0.0),
                             Parallel(Func(self.cjBoss2.setChatAbsolute, "Efficiency is not the purpose of the law.", CFSpeech | CFTimeout),
                                      Sequence(ActorInterval(self.cjBoss2, 'Ff_lookLt'),
                                               ActorInterval(self.cjBoss2, 'Ff_lookLt', playRate=-1),
                                               Func(self.cjBoss2.loop, 'Ff_neutral'))),
                             Func(base.camera.setPosHpr, 45.081, 40.301, 36.134, 35.3, -0.4, 0.0),
                             Func(self.cjBoss.setChatAbsolute, "No, but it DOES keep the criminals from walking away!", CFSpeech | CFTimeout), Wait(4.0),
                             Func(base.camera.setPosHpr, 13.761, 34.660, 39.585, 27.2, 4.38, 0.0), Func(self.ceoBoss.loop, 'Ff_speech'),
                             Func(self.ceoBoss.setChatAbsolute, "Alright that's enough! This is NOT what we were brought here to discuss!", CFSpeech | CFTimeout), Wait(4.0),
                             Func(self.ceoBoss.setChatAbsolute, "You two can debate legal philosophy all day, but while you argue about how the law should work...", CFSpeech | CFTimeout), Wait(4.0),
                             Func(self.ceoBoss.setChatAbsolute, "My department has been dealing with the Toons longer than anyone else in this room!", CFSpeech | CFTimeout), Wait(4.0),
                             Func(self.ceoBoss.setChatAbsolute, "Bossbots have been handling these pests since the beginning.", CFSpeech | CFTimeout), Wait(4.0),
                             Func(self.ceoBoss.setChatAbsolute, "We've seen every trick they use. Every stunt they pull. Every way they try to disrupt operations.", CFSpeech | CFTimeout), Wait(4.0), Func(self.ceoBoss.loop, 'Ff_neutral'),
                             Func(base.camera.setPosHpr, -17.77, 26.875, 24.818, -362, 17.4, 10.5),
                             Func(self.ceoBoss.setChatAbsolute, "And I can assure you...", CFSpeech | CFTimeout), Wait(4.0),
                             Parallel(Sequence(ActorInterval(self.ceoBoss, 'Ff_point'), Func(self.ceoBoss.loop, 'Ff_neutral')),
                                      Func(self.ceoBoss.setChatAbsolute, "Debating procedure has never stopped them!", CFSpeech | CFTimeout)),
                             Func(self.switchIntroMusic),
                             LerpPosHprInterval(base.camera, 3.0, (0, -46.3761, 10), (180, 0, 0), blendType='easeInOut'),
                             # walk into the office
                             Parallel(Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/CHQ_door_open.ogg')), rightDoors[1].hprInterval(2.0, (-20.0, 0.0, 0.0)),
                                      leftDoors[1].hprInterval(2.0, (200.0, 0.0, 0.0))),
                             Func(self.contingency.loop, 'walk'),
                             LerpPosInterval(self.contingency, 5.0, (0, -76.3761, 0)), Func(self.contingency.loop, 'neutral'),
                            Func(self.contingency.setChatAbsolute, "Sorry to interrupt you, Sir, but we have unauthorized visitors.", CFSpeech | CFTimeout), Wait(3.0),
                             LerpPosHprInterval(base.camera, 3.0, (24.8814, 55.2589, 45), (-50.0743, 0, 0), blendType='easeInOut'),
                             Func(self.setChatAbsolute, "Hmm, it seems our meeting has acquired guests.", CFSpeech | CFTimeout), Wait(4.0),
                             Func(base.camera.setPosHpr, 5.9252, 39.0836, 43, -90, -0, 0),
                             Func(self.cfoBoss.setChatAbsolute, "So these are the ones hurting our margins?", CFSpeech | CFTimeout), Wait(4.0),
                             Func(base.camera.setPosHpr, -2.410, 31.641, 37.078, 71.8, 5.34, 0.0),
                             Func(self.vpBoss.setChatAbsolute, "They're smaller than I expected.", CFSpeech | CFTimeout), Wait(4.0),
                             Func(base.camera.setPosHpr, -27.6814, 50.6378, 43, -325, 0, 0.0),
                             Parallel(Sequence(ActorInterval(self.cjBoss2, 'Ff_speech'), Func(self.cjBoss2.loop, 'Ff_neutral')),
                                      Func(self.cjBoss2.setChatAbsolute, "Yes... I can hear them. The sound of disorder.", CFSpeech | CFTimeout)), Wait(2.0),
                             Func(base.camera.setPosHpr, 45.081, 40.301, 36.134, 35.3, -0.4, 0.0),
                             Parallel(Sequence(ActorInterval(self.cjBoss, 'Ff_cross_arms_out'), Func(self.cjBoss.loop, 'Ff_neutral_f')),
                                      Func(self.cjBoss.setChatAbsolute, "Then let's correct it!", CFSpeech | CFTimeout)), Wait(2.0),
                             LerpPosHprInterval(base.camera, 3.0, (24.8814, 55.2589, 50), (-50.0743, 0, 0), blendType='easeInOut'),
                             Func(self.setChatAbsolute, "Your division oversees the executive operations of C.O.G.S. Inc. Explain how this happened.", CFSpeech | CFTimeout), Wait(4.0),
                             LerpPosHprInterval(base.camera, 3.0, (0, -46.3761, 10), (180, 0, 0), blendType='easeInOut'),
                             Func(self.contingency.setChatAbsolute, "The Toons have been disrupting multiple departments.", CFSpeech | CFTimeout), Wait(4.0),
                             Func(self.contingency.setChatAbsolute, "Security breaches, operational damage, financial loss...", CFSpeech | CFTimeout), Wait(4.0),
                             LerpPosHprInterval(base.camera, 2.0, (49.844, -95.266, 10), (0, 0, 0), blendType='easeInOut'),
                             Func(self.dividend.setChatAbsolute, "Corporate liquidity remains stable.", CFSpeech | CFTimeout), Wait(4.0),
                             Func(self.dividend.setChatAbsolute, "Once these Toons are removed... profits will rebound.", CFSpeech | CFTimeout), Wait(4.0),
                             LerpPosHprInterval(base.camera, 2.0, (-82.031, -95.266, 10), (0, 0, 0), blendType='easeInOut'),
                             Func(self.recordkeeper.setChatAbsolute, "All incident reports documented. All disciplinary actions prepared.", CFSpeech | CFTimeout), Wait(4.0),
                             Func(self.recordkeeper.setChatAbsolute, "Just waiting for the outcome!", CFSpeech | CFTimeout), Wait(4.0),
                             LerpPosHprInterval(base.camera, 2.0, (-53.594, -95.266, 10), (0, 0, 0), blendType='easeInOut'),
                             Func(self.tollmaster.setChatAbsolute, "Security routes sealed. Escape options are minimal.", CFSpeech | CFTimeout), Wait(4.0),
                             LerpPosHprInterval(base.camera, 2.0, (24.8814, 55.2589, 45), (-50.0743, 0, 0), blendType='easeInOut'),
                             Func(self.setChatAbsolute, "Contingency Director...", CFSpeech | CFTimeout), Wait(3.0),
                             Func(self.setChatAbsolute, "Your team was created for situations exactly like this.", CFSpeech | CFTimeout), Wait(4.0),
                             Func(self.setChatAbsolute, "Are they capable of resolving this problem?", CFSpeech | CFTimeout), Wait(4.0),
                             LerpPosHprInterval(base.camera, 3.0, (0, -46.3761, 10), (180, 0, 0), blendType='easeInOut'),
                             Func(self.contingency.setChatAbsolute, "My team specializes in preventing corporate collapse.", CFSpeech | CFTimeout), Wait(4.0),
                             Parallel(Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/CHQ_door_close.ogg')), rightDoors[1].hprInterval(1.0, (90.0, 0.0, 0.0)),
                                      leftDoors[1].hprInterval(1.0, (90.0, 0.0, 0.0)), Func(self.contingency.setChatAbsolute, "I can assure you they will be able to handle this situation, Sir.", CFSpeech | CFTimeout)), Wait(4.0),
                             LerpPosHprInterval(base.camera, 2.0, (49.844, -95.266, 10), (0, 0, 0), blendType='easeInOut'),
                             Func(self.dividend.setChatAbsolute, "I've already calculated the return on investment.", CFSpeech | CFTimeout), Wait(4.0),
                             Func(self.dividend.setChatAbsolute, "Eliminating these Toons should bring our profits right back into the green!", CFSpeech | CFTimeout), Wait(4.0),
                             Parallel(Func(self.contingency.loop, 'sit-exec'), Func(self.contingency.setPosHpr, (79.219, -80.266, 2.5), (180.0, 0.0, 0.0))),
                             LerpPosHprInterval(base.camera, 2.0, (-82.031, -95.266, 10), (0, 0, 0), blendType='easeInOut'),
                             Func(self.recordkeeper.setChatAbsolute, "Documentation prepared. Damage assessments complete. Defeat reports drafted in advance...", CFSpeech | CFTimeout), Wait(4.0),
                             Func(self.recordkeeper.setChatAbsolute, "All that's missing is their signatures!", CFSpeech | CFTimeout), Wait(4.0),
                             LerpPosHprInterval(base.camera, 2.0, (-53.594, -95.266, 10), (0, 0, 0), blendType='easeInOut'),
                             Func(self.tollmaster.setChatAbsolute, "Every corridor sealed. Every checkpoint active. No shortcuts. No exits.", CFSpeech | CFTimeout), Wait(4.0),
                             Func(self.tollmaster.setChatAbsolute, "They're not leaving this floor without paying the toll!", CFSpeech | CFTimeout), Wait(4.0),
                             LerpPosHprInterval(base.camera, 3.0, (79.219, -95.266, 10), (0, 0, 0), blendType='easeInOut'),
                             Func(self.contingency.setChatAbsolute, "You Toons are simply another contingency.", CFSpeech | CFTimeout), Wait(4.0),
                             Func(self.contingency.setChatAbsolute, "You wanted the board's attention, now you have it!", CFSpeech | CFTimeout), Wait(4.0),
                             Func(self.contingency.setChatAbsolute, "Let's see how well chaos performs under... proper oversight!", CFSpeech | CFTimeout), Wait(4.0),
                             Func(base.camera.setPosHpr, 13.761, 34.660, 39.585, 27.2, 4.38, 0.0), Func(self.ceoBoss.loop, 'Ff_speech'),
                             Func(self.ceoBoss.setChatAbsolute, "Quite the efficient group you've assembled here.", CFSpeech | CFTimeout), Wait(4.0),
                             Func(self.ceoBoss.setChatAbsolute, "Mr. Chairman, if her team performs the way the reports say they do...", CFSpeech | CFTimeout), Wait(4.0),
                             Func(self.ceoBoss.setChatAbsolute, "These Toons won't make it past this floor!", CFSpeech | CFTimeout), Wait(4.0),
                             Func(self.ceoBoss.loop, 'Ff_neutral'),
                             LerpPosHprInterval(base.camera, 2.0, (24.8814, 55.2589, 45), (-50.0743, 0, 0), blendType='easeInOut'),
                             Func(self.setChatAbsolute, "Very well.", CFSpeech | CFTimeout), Wait(3.0),
                             Func(self.setChatAbsolute, "Oversight Committee... you are authorized to resolve this matter.", CFSpeech | CFTimeout), Wait(4.0),
                             Parallel(Sequence(ActorInterval(self, 'Ff_point'), Func(self.loop, 'Ff_neutral')),
                                      Func(self.setChatAbsolute, "Show them why this company remains in control!", CFSpeech | CFTimeout)), Wait(2.0),
                             Func(self.setChatAbsolute, "", CFSpeech | CFTimeout)
                             )
        return Sequence(Func(self.stickToonsToFloor), bossTrack, Func(self.unstickToons), name=self.uniqueName('Introduction'))

    def __makeRollToBattleTwoMovie(self):
        startPos = Point3(ToontownGlobals.SellbotBossBattleOnePosHpr[0], ToontownGlobals.SellbotBossBattleOnePosHpr[1], ToontownGlobals.SellbotBossBattleOnePosHpr[2])
        if self.arenaSide:
            topRampPos = Point3(*ToontownGlobals.SellbotBossTopRampPosB)
            topRampTurnPos = Point3(*ToontownGlobals.SellbotBossTopRampTurnPosB)
            p3Pos = Point3(*ToontownGlobals.SellbotBossP3PosB)
        else:
            topRampPos = Point3(*ToontownGlobals.SellbotBossTopRampPosA)
            topRampTurnPos = Point3(*ToontownGlobals.SellbotBossTopRampTurnPosA)
            p3Pos = Point3(*ToontownGlobals.SellbotBossP3PosA)
        battlePos = Point3(ToontownGlobals.SellbotBossBattleTwoPosHpr[0], ToontownGlobals.SellbotBossBattleTwoPosHpr[1], ToontownGlobals.SellbotBossBattleTwoPosHpr[2])
        battleHpr = VBase3(ToontownGlobals.SellbotBossBattleTwoPosHpr[3], ToontownGlobals.SellbotBossBattleTwoPosHpr[4], ToontownGlobals.SellbotBossBattleTwoPosHpr[5])
        bossTrack = Sequence()
        bossTrack.append(Func(self.getGeomNode().setH, 180))
        bossTrack.append(Func(self.loop, 'Ff_neutral'))
        track, hpr = self.rollBossToPoint(startPos, None, topRampPos, None, 0)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(topRampPos, hpr, topRampTurnPos, None, 0)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(topRampTurnPos, hpr, p3Pos, None, 0)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(p3Pos, hpr, battlePos, None, 0)
        bossTrack.append(track)
        return Sequence(bossTrack, Func(self.getGeomNode().setH, 0), name=self.uniqueName('BattleTwo'))

    def cagedToonMovieFunction(self, instruct, cageIndex):
        self.notify.debug('cagedToonMovieFunction()')
        if not (hasattr(self, 'cagedToon') and hasattr(self.cagedToon, 'nametag') and hasattr(self.cagedToon, 'nametag3d')):
            return
        if instruct == 1:
            self.cagedToon.nametag3d.setScale(2)
        elif instruct == 2:
            self.cagedToon.setChatAbsolute("", CFSpeech | CFTimeout)
        elif instruct == 3:
            self.cagedToon.nametag3d.setScale(1)
        elif instruct == 4:
            self.cagedToon.setChatAbsolute("", CFSpeech | CFTimeout)

    def makeEndOfBattleMovie(self, hasLocalToon):
        name = self.uniqueName('CageDrop')
        seq = Sequence(name=name)
        seq.append(Func(self.cage.setPos, self.cagePos[self.cageIndex]))
        if hasLocalToon:
            seq += [Func(camera.wrtReparentTo, render),
             base.camera.posHprInterval(1, Point3(0, -50, 0), Point3(0, 0, 0), blendType = 'easeInOut', other = self.cage),
             Func(localAvatar.setCameraFov, ToontownGlobals.CogHQCameraFov),
             Func(self.hide)]
        seq += [Wait(0.5),
         Parallel(self.cage.posInterval(1, self.cagePos[self.cageIndex + 1], blendType='easeInOut'), SoundInterval(self.cageLowerSfx, duration=1)),
         Func(self.cagedToonMovieFunction, 1, self.cageIndex),
         Func(self.cagedToonMovieFunction, 2, self.cageIndex),
         Wait(3),
         Func(self.cagedToonMovieFunction, 3, self.cageIndex),
         Func(self.cagedToonMovieFunction, 4, self.cageIndex)]
        if hasLocalToon:
            seq += [Func(self.show),
             Func(camera.wrtReparentTo, localAvatar),
             base.camera.posHprInterval(1, Point3(localAvatar.cameraPositions[0][0]), Point3(0, 0, 0), blendType = 'easeInOut')]
        self.cageIndex += 1
        return seq

    def __makeBossDamageMovie(self):
        startPos = Point3(ToontownGlobals.SellbotBossBattleTwoPosHpr[0], ToontownGlobals.SellbotBossBattleTwoPosHpr[1], ToontownGlobals.SellbotBossBattleTwoPosHpr[2])
        startHpr = Point3(*ToontownGlobals.SellbotBossBattleThreeHpr)
        bottomPos = Point3(*ToontownGlobals.SellbotBossBottomPos)
        deathPos = Point3(*ToontownGlobals.SellbotBossDeathPos)
        self.setPosHpr(startPos, startHpr)
        bossTrack = Sequence()
        bossTrack.append(Func(self.loop, 'Ff_neutral'))
        track, hpr = self.rollBossToPoint(startPos, startHpr, bottomPos, None, 1)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(bottomPos, startHpr, deathPos, None, 1)
        bossTrack.append(track)
        duration = bossTrack.getDuration()
        return bossTrack

    def testMovie(self):
        bossTrack = Sequence()
        bossTrack.append(Func(self.ceoBoss.setChatAbsolute, "This is a test speech.", CFSpeech | CFTimeout))
        return bossTrack

    def __talkAboutPromotion(self, speech):
        if not self.localToonPromoted:
            pass
        elif ((self.prevCogSuitLevel < ToontownGlobals.MaxCogSuitLevel) or (self.prevCogSuitReviveLevel < ToontownGlobals.MaxCogSuitLevel)):
            newCogSuitLevel = localAvatar.getCogLevels()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
            newCogSuitReviveLevel = localAvatar.getCogReviveLevels()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
            if newCogSuitLevel == ToontownGlobals.MaxCogSuitLevel:
                speech += TTLocalizer.CagedToonLastPromotion % (ToontownGlobals.MaxCogSuitLevel + 1)
            if newCogSuitReviveLevel == ToontownGlobals.MaxCogSuitLevel:
                speech += TTLocalizer.CagedToonLastRevivePromotion % (ToontownGlobals.MaxCogSuitLevel + 1)
            if newCogSuitLevel in ToontownGlobals.CogSuitHPLevels and newCogSuitLevel != self.prevCogSuitLevel:
                speech += TTLocalizer.CagedToonHPBoost
            if newCogSuitReviveLevel in ToontownGlobals.CogReviveSuitHPLevels and newCogSuitReviveLevel != self.prevCogSuitReviveLevel:
                speech += TTLocalizer.CagedToonHPBoost
        else:
            speech += TTLocalizer.CagedToonMaxed % (ToontownGlobals.MaxCogSuitLevel + 1)

        return speech

    def __makeCageOpenMovie(self):
        speech = TTLocalizer.CagedToonThankYou
        speech = self.__talkAboutPromotion(speech)
        name = self.uniqueName('CageOpen')
        seq = Sequence(
            Func(self.cage.setPos, self.cagePos[4]),
            Func(self.cageDoor.setHpr, VBase3(0, 0, 0)),
            Func(self.cagedToon.setPos, Point3(0, -2, 0)),
            Parallel(
                self.cage.posInterval(0.5, self.cagePos[5], blendType='easeOut'),
                SoundInterval(self.cageLowerSfx, duration=0.5)),
            Parallel(
                self.cageDoor.hprInterval(0.5, VBase3(0, 90, 0), blendType='easeOut'),
                Sequence(SoundInterval(self.cageDoorSfx), duration=0)),
            Wait(0.2),
            Func(self.cagedToon.loop, 'walk'),
            self.cagedToon.posInterval(0.8, Point3(0, -6, 0)),
            Func(self.cagedToon.setChatAbsolute, TTLocalizer.CagedToonYippee, CFSpeech | CFTimeout),
            ActorInterval(self.cagedToon, 'jump'),
            Func(self.cagedToon.loop, 'neutral'),
            Func(self.cagedToon.headsUp, localAvatar),
            Func(self.cagedToon.setLocalPageChat, speech, 0),
            Func(camera.reparentTo, localAvatar),
            Func(camera.setPos, 0, -9, 9),
            Func(camera.lookAt, self.cagedToon, Point3(0, 0, 2)), name=name)
        return seq

    def __showOnscreenMessage(self, text):
        if self.onscreenMessage:
            self.onscreenMessage.destroy()
            self.onscreenMessage = None
        self.onscreenMessage = DirectLabel(text=text, text_fg=VBase4(1, 1, 1, 1), text_align=TextNode.ACenter, relief=None, pos=(0, 0, 0.35), scale=0.1)

    def __clearOnscreenMessage(self):
        if self.onscreenMessage:
            self.onscreenMessage.destroy()
            self.onscreenMessage = None

    def __showWaitingMessage(self, task):
        self.__showOnscreenMessage(TTLocalizer.BuildingWaitingForVictors)

    def __placeCageShadow(self):
        if self.cageShadow == None:
            self.cageShadow = loader.loadModel('phase_3/models/props/drop_shadow')
            self.cageShadow.setPos(0, 77.9, 18)
            self.cageShadow.setColorScale(1, 1, 1, 0.6)
        self.cageShadow.reparentTo(render)

    def __removeCageShadow(self):
        if self.cageShadow != None:
            self.cageShadow.detachNode()

    def setCageIndex(self, cageIndex):
        self.cageIndex = cageIndex
        self.cage.setPos(self.cagePos[self.cageIndex])
        if self.cageIndex >= 4:
            self.__placeCageShadow()
        else:
            self.__removeCageShadow()

    def setupBosses(self):
        self.fourBosses = [self.vpBoss, self.cfoBoss, self.cjBoss, self.ceoBoss]
        self.bossNames = ['Senior V.P.', 'C. F. O.', 'C. L. O.',
                          'C. E. O.']
        for x in range(4):
            boss = BossCog.generateBossCog()
            boss.setName(self.bossNames[x])
            bossNameInfo = TTLocalizer.BossCogNameWithDept % {'name': boss._name,
                                                              'dept': SuitDNA.getDeptFullname(boss.style.dept)}
            boss.setDisplayName(bossNameInfo)
            boss.reparentTo(self.geom)
            if self.cjBoss:
                boss.loop('Ff_neutral_f')
            else:
                boss.loop('Ff_neutral_f')
        for boss in [(self.fourBosses[0], 'VPStand'), (self.fourBosses[1], 'CFOStand'), (self.fourBosses[2], 'CJStand'),
                     (self.fourBosses[3], 'CEOStand')]:
            boss[0].reparentTo(self.geom.find('**/%s' % (boss[1])))
            boss[0].setZ(22)
        self.vpBoss.setH(90)
        self.cfoBoss.setPosHpr(0.0, 0.0, 22.0, -90.0, 0.0, 0.0)
        self.ceoBoss.setPosHpr(0, 5, 22, 0, 0, 0)
        self.geom.find('**/CFOStand').setPos(45.925, 39.084, 0.0)

    def loadEnvironment(self):
        DistributedBossCog.DistributedBossCog.loadEnvironment(self)
        self.geom = loader.loadModel('phase_14/models/modules/ExecutiveMeetingRoom')
        self.paperStack1 = loader.loadModel('phase_11/models/lawbotHQ/LB_paper_stacks')
        # self.paperStack2 = loader.loadModel('phase_11/models/lawbotHQ/LB_paper_stacks')
        # self.paperStack3 = loader.loadModel('phase_11/models/lawbotHQ/LB_paper_stacks')
        #self.paperStack2.setScale(1.5)
        self.paperStack1.setScale(1.5)
       # self.paperStack3.setScale(1.5)
        self.paperStack1.reparentTo(self.geom)
       # self.paperStack3.reparentTo(self.geom)
       # self.paperStack2.reparentTo(self.geom)
        self.paperStack1.setPosHpr(52.2653, 78.2118, -0.05, 126.891, 0, 0)
        # self.paperStack2.setPosHpr(20, -8.55076, -0.05, 0, 0, 0) # Chairman Stack
        # self.paperStack3.setPosHpr(-20, -8.55076, -0.05, 0, 0, 0) # CJ Stack
        # self.rampA = self.geom.find('**/north_ramp')
        # self.rampB = self.geom.find('**/west_ramp')
        # self.rampC = self.geom.find('**/east_ramp')
        self.cage = self.geom.find('**/toon_cage')
        self.elevatorEntrance = self.geom.find('**/elevatorIN_origin')
        self.elevatorEntrance.getChildren().detach()
        self.elevatorEntrance.setScale(1)
        elevatorModel = loader.loadModel('phase_12/models/bossbotHQ/BB_Inside_Elevator')
        elevatorModel.reparentTo(self.elevatorEntrance)
        self.setupElevator(elevatorModel)
        self.elevatorChairman = self.geom.find('**/elevatorOUT_origin')
        self.elevatorChairman.getChildren().detach()
        self.elevatorChairman.setScale(1)
        elevatorModel = loader.loadModel('phase_14/models/modules/RooftopElevator')
        elevatorModel.reparentTo(self.elevatorChairman)
        #self.setupChairmanElevator(elevatorModel)
        #self.setupElevator(elevatorModel)
        self.meetingTable = loader.loadModel('phase_14/models/props/executive_table-mod')
        self.meetingTable.reparentTo(self.geom)
       # self.meetingTable.setBlend(frameBlend=True)
        self.presentation = loader.loadModel('phase_14/models/props/screen-mod')
        self.presentation.reparentTo(self.geom.find('**/presentation_origin'))
       # self.presentation.setBlend(frameBlend=config.GetBool('interpolate-animations', True))
        self.geomProps.append(self.presentation)
        self.geom.reparentTo(render)
        for prop in FourBossBattleGlobals.MeetingProps:
            model = loader.loadModel('phase_%s/models/%s/%s.bam' % (prop[0], prop[1], prop[2]))
            model.setPosHprScale(*prop[3])
            model.reparentTo(self.geom)
            self.geomProps.append(model)
        pos = self.cage.getPos()
        self.cagePos = []
        for height in self.cageHeights:
            self.cagePos.append(Point3(pos[0], pos[1], height))

        for i in range(8):
            chandelier = loader.loadModel('phase_14/models/props/ExecutiveChandelier')
            chandelier.setPosHpr(*FourBossBattleGlobals.ChandelierInitialPositions[i])
            chandelier.reparentTo(self.geom)
            self.chandeliers.append(chandelier)

        for i in range(4):
            bookshelf = loader.loadModel('phase_11/models/lawbotHQ/LawbotBossRoomChair')
            bookshelf.setPosHpr(*FourBossBattleGlobals.BookshelfPosHprs[i])
            bookshelf.reparentTo(self.geom)
            bookshelf.setScale(.75)
            self.bookshelves.append(bookshelf)

        for i in range(4):
            bookshelf2 = loader.loadModel('phase_9/models/cogHQ/multislacker_tv')
            texture2 = loader.loadTexture('phase_9/maps/sellbotHQ/multislacker/ttcc_int_ms_tvScreen_boardbot.png')
            texture = loader.loadTexture('phase_9/maps/sellbotHQ/multislacker/ttcc_int_ms_palette_board.png')
            screen = loader.loadModel('phase_9/models/cogHQ/ms_tvScreen')
            screen.reparentTo(bookshelf2.find('**/tvScreen_origin'))
            screen.setTexture(texture2, 1)
            bookshelf2.find('**/tv_body').setTexture(texture, 1)
            bookshelf2.find('**/tv_legs').setTexture(texture, 1)
            bookshelf2.setPosHpr(*FourBossBattleGlobals.BookshelfPosHprs2[i])
            bookshelf2.reparentTo(self.geom)
            bookshelf2.setScale(1)
            self.bookshelves.append(bookshelf)


        self.cageDoor = self.geom.find('**/cage_sides')
        self.cage.setScale(1)

        self.vpBoss = BossCog.BossCog()
        dna = SuitDNA.SuitDNA()
        dna.newBossCog('s')
        self.vpBoss.vpBoss = True
        self.vpBoss.setDNA(dna)
        self.vpBoss.initializeDropShadow()
        self.vpBoss.setH(90)
        self.vpBoss.loop('Ff_neutral')
        self.vpBoss.reparentTo(self.geom.find('**/VPStand'))
        self.vpBoss.setZ(22)
        self.vpBoss.setName('Senior V.P.\nSellbot')
        self.vpBoss.doId = 0

        self.cfoBoss = BossCog.BossCog()
        dna = SuitDNA.SuitDNA()
        dna.newBossCog('m')
        self.cfoBoss.cfoBoss = True
        self.cfoBoss.setDNA(dna)
        self.cfoBoss.initializeDropShadow()
        self.cfoBoss.setH(-90)
        self.cfoBoss.loop('Ff_neutral')
        self.cfoBoss.reparentTo(self.geom.find('**/CFOStand'))
        self.cfoBoss.setZ(22)
        self.cfoBoss.setName('C. F. O.\nCashbot')
        self.geom.find('**/CFOStand').setPos(45.925, 39.084, 0.0)
        self.cfoBoss.doId = 0

        self.cjBoss = BossCog.BossCog()
        dna = SuitDNA.SuitDNA()
        dna.newBossCog('l')
        self.cjBoss.cjBoss = True
        self.cjBoss.setDNA(dna)
        self.cjBoss.initializeDropShadow()
        self.cjBoss.setH(0)
        self.cjBoss.loop('Ff_neutral_f')
        self.cjBoss.reparentTo(self.geom.find('**/CJStand'))
        self.cjBoss.setZ(22)
        self.cjBoss.setName('C. L. O.\nLawbot')
        self.cjBoss.doId = 0

        self.ceoBoss = BossCog.BossCog()
        dna = SuitDNA.SuitDNA()
        dna.newBossCog('c')
        self.ceoBoss.ceoBoss = True
        self.ceoBoss.setDNA(dna)
        self.ceoBoss.initializeDropShadow()
        self.ceoBoss.setH(0)
        self.ceoBoss.loop('Ff_neutral')
        self.ceoBoss.reparentTo(self.geom.find('**/CEOStand'))
        self.ceoBoss.setPosHpr(0, 5, 22, 0, 0, 0)
        self.ceoBoss.setName('C. E. O.\nBossbot')
        self.ceoBoss.doId = 0

        # self.cioBoss = BossCog.BossCog()
        # dna = SuitDNA.SuitDNA()
        # dna.newBossCog('t')
        # self.cioBoss.cioBoss = True
        # self.cioBoss.setDNA(dna)
        # self.cioBoss.initializeDropShadow()
        # self.cioBoss.setH(0)
        # self.cioBoss.loop('Ff_neutral')
        # self.cioBoss.reparentTo(self.geom)
        # self.cioBoss.setZ(22)
        # self.cioBoss.setName('C. I. O.\nTechbot')
        # self.cioBoss.setPosHpr(52.2653, 78.2118, 22, 307, 0, 0)
        # self.cioBoss.doId = 0

        # self.cpoBoss = BossCog.BossCog()
        # dna = SuitDNA.SuitDNA()
        # dna.newBossCog('p')
        # self.cpoBoss.cpoBoss = True
        # self.cpoBoss.setDNA(dna)
        # self.cpoBoss.initializeDropShadow()
        # self.cpoBoss.setH(0)
        # self.cpoBoss.loop('Ff_neutral')
        # self.cpoBoss.reparentTo(self.geom)
        # self.cpoBoss.setPosHpr(-50.0306, 77.9406, 22, -325, 0, 0)
        # self.cpoBoss.setName('C. P. O.\nPressbot')
        # self.cpoBoss.doId = 0

        self.cjBoss2 = BossCog.BossCog()
        dna = SuitDNA.SuitDNA()
        dna.newBossCog('l2')
        self.cjBoss2.cjBoss2 = True
        self.cjBoss2.setDNA(dna)
        self.cjBoss2.initializeDropShadow()
        self.cjBoss2.setH(0)
        self.cjBoss2.loop('Ff_neutral')
        self.cjBoss2.reparentTo(self.geom)
        self.cjBoss2.setPosHpr(-50.0306, 77.9406, 22, -325, 0, 0)
        self.cjBoss2.setName('Chief Justice\nLawbot')
        self.cjBoss2.doId = 0

        self.reparentTo(render)
        self.setPosHpr(52.2653, 78.2118, 22, 307, 0, 0)

        self.toonsDiscovered = base.loadMusic('phase_9/audio/bgm/encntr_sting_announce.ogg')
        self.betweenBattleMusic = base.loadMusic('phase_9/audio/bgm/encntr_toon_winning.ogg')
        self.battleTwoMusic = base.loadMusic('phase_7/audio/bgm/encntr_suit_winning_indoor.ogg')
        self.battleThreeMusic = base.loadMusic('phase_9/audio/bgm/encntr_head_suit_theme.ogg')
        self.promotionMusic = base.loader.loadMusic('phase_14/audio/bgm/ET_introduction_stinger.ogg')
        self.promotionMusic2 = base.loader.loadMusic('phase_14/audio/bgm/ET_boss_prep.ogg')
        self.betweenPhaseMusic = base.loader.loadMusic('phase_9/audio/bgm/encntr_toon_winning.ogg')
        self.battleOneMusic = loader.loadMusic('phase_12/audio/bgm/encntr_penultimate_intro.ogg')
        self.battleOneMusic2 = loader.loadMusic('phase_12/audio/bgm/encntr_penultimate_unlock-loop.ogg')
        self.battleOneMusic3 = loader.loadMusic('phase_12/audio/bgm/encntr_penultimate_intro.ogg')
        self.geom.reparentTo(render)

    def hideContingency(self):
        self.contingency.hide()

    def hideDividend(self):
        self.dividend.hide()

    def hideRecordkeeper(self):
        self.recordkeeper.hide()

    def hideTollmaster(self):
        self.tollmaster.hide()

    def switchIntroMusic(self):
        self.promotionMusic.stop()
        base.playMusic(self.promotionMusic2, looping=1, volume=0.9)

    def unloadEnvironment(self):
        DistributedBossCog.DistributedBossCog.unloadEnvironment(self)
        self.geom.removeNode()
        del self.geom
        del self.cage
        del self.meetingTable
        del self.elevatorChairman
        del self.elevatorEntrance
        del self.geomProps
        del self.presentation
        del self.ceoBoss
        del self.cjBoss
        del self.cjBoss2
        del self.cfoBoss
        del self.vpBoss
        del self.paperStack1
        del self.paperStack2
        del self.bookshelves
        del self.chandeliers
        del self.cioBoss
        del self.cpoBoss

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

    def __findRamp(self, name, path):
        ramp = self.geom.find(path)
        children = ramp.getChildren()
        animate = ramp.attachNewNode(name)
        children.reparentTo(animate)
        fsm = ClassicFSM.ClassicFSM(name, [
            State.State('extend',
                        Functor(self.enterRampExtend, animate),
                        Functor(self.exitRampExtend, animate), [
                            'extended',
                            'retract',
                            'retracted']),
         State.State('extended',
                     Functor(self.enterRampExtended, animate),
                     Functor(self.exitRampExtended, animate), [
                         'retract',
                         'retracted']),
         State.State('retract',
                     Functor(self.enterRampRetract, animate),
                     Functor(self.exitRampRetract, animate), [
                         'extend',
                         'extended',
                         'retracted']),
         State.State('retracted',
                     Functor(self.enterRampRetracted, animate),
                     Functor(self.exitRampRetracted, animate), [
                         'extend',
                         'extended']),
         State.State('off',
                     Functor(self.enterRampOff, animate),
                     Functor(self.exitRampOff, animate))],
         'off', 'off', onUndefTransition=ClassicFSM.ClassicFSM.DISALLOW)
        fsm.enterInitialState()
        return fsm

    def enterRampExtend(self, animate):
        intervalName = self.uniqueName('extend-%s' % animate.getName())
        adjustTime = 2.0 * animate.getX() / 18.0
        ival = Parallel(SoundInterval(self.rampSlideSfx, node=animate), animate.posInterval(adjustTime, Point3(0, 0, 0), blendType='easeInOut', name=intervalName))
        ival.start()
        self.storeInterval(ival, intervalName)

    def exitRampExtend(self, animate):
        intervalName = self.uniqueName('extend-%s' % animate.getName())
        self.clearInterval(intervalName)

    def enterRampExtended(self, animate):
        animate.setPos(0, 0, 0)

    def exitRampExtended(self, animate):
        pass

    def enterRampRetract(self, animate):
        intervalName = self.uniqueName('retract-%s' % animate.getName())
        adjustTime = 2.0 * (18 - animate.getX()) / 18.0
        ival = Parallel(SoundInterval(self.rampSlideSfx, node=animate), animate.posInterval(adjustTime, Point3(18, 0, 0), blendType='easeInOut', name=intervalName))
        ival.start()
        self.storeInterval(ival, intervalName)

    def exitRampRetract(self, animate):
        intervalName = self.uniqueName('retract-%s' % animate.getName())
        self.clearInterval(intervalName)

    def enterRampRetracted(self, animate):
        animate.setPos(18, 0, 0)

    def exitRampRetracted(self, animate):
        pass

    def enterRampOff(self, animate):
        pass

    def exitRampOff(self, animate):
        pass

    def enterOff(self):
        DistributedBossCog.DistributedBossCog.enterOff(self)
        if self.cagedToon:
            self.cagedToon.clearChat()

    def enterWaitForToons(self):
        DistributedBossCog.DistributedBossCog.enterWaitForToons(self)
        self.geom.hide()
        self.cagedToon.removeActive()

    def exitWaitForToons(self):
        DistributedBossCog.DistributedBossCog.exitWaitForToons(self)
        self.geom.show()
        self.cagedToon.addActive()

    def enterElevator(self):
        DistributedBossCog.DistributedBossCog.enterElevator(self)
        #self.setupBosses()
        self.setCageIndex(0)
        self.reparentTo(render)
        self.setPosHpr(52.2653, 78.2118, 22, 307, 0, 0)
        self.happy = 1
        self.raised = 1
        self.forward = 1
        self.doAnimate()
        self.cagedToon.removeActive()
        base.camLens.setMinFov(ToontownGlobals.VPElevatorFov/(4./3.))

    def exitElevator(self):
        DistributedBossCog.DistributedBossCog.exitElevator(self)
        self.cagedToon.addActive()

    def enterIntroduction(self):
        self.reparentTo(render)
        self.setPosHpr(52.2653, 78.2118, 22, 307, 0, 0)
        self.stopAnimate()
        DistributedBossCog.DistributedBossCog.enterIntroduction(self)
        self.accept('clickedNametag', self.__clickedNameTag)
        self.accept('friendAvatar', self.__handleFriendAvatar)
        self.accept('avatarDetails', self.__handleAvatarDetails)
        NametagGlobals.setWant2dNametags(False)
        NametagGlobals.setWantActiveNametags(True)
        self.setCageIndex(0)
        base.playMusic(self.promotionMusic, looping=1, volume=0.9)

    def exitIntroduction(self):
        DistributedBossCog.DistributedBossCog.exitIntroduction(self)
        self.promotionMusic.stop()
        self.promotionMusic2.stop()

    def enterBattleOne(self):
        DistributedBossCog.DistributedBossCog.enterBattleOne(self)
        self.reparentTo(render)
        self.setPosHpr(52.2653, 78.2118, 22, 307, 0, 0)
        self.accept('clickedNametag', self.__clickedNameTag)
        self.accept('friendAvatar', self.__handleFriendAvatar)
        self.accept('avatarDetails', self.__handleAvatarDetails)
        NametagGlobals.setWant2dNametags(False)
        NametagGlobals.setWantActiveNametags(True)
        self.clearChat()
        self.cagedToon.clearChat()
        if self.battleA == None or self.battleB == None:
            cageIndex = 1
        else:
            cageIndex = 0
        self.setCageIndex(cageIndex)
        self.battleOneMusic2.setLoop(True)
        self.battleOneMusic3.play()
        self.battleOneMusic.stop()
        taskMgr.doMethodLater(
            self.battleOneMusic3.length(),
            self.__startBattleOneLoop,
            'startBattleOneLoop'
        )

    def exitBattleOne(self):
        DistributedBossCog.DistributedBossCog.exitBattleOne(self)

    def enterRollToBattleTwo(self):
        self.disableToonCollision()
        self.releaseToons()
        self.reparentTo(render)
        self.battleOneMusic2.stop()
        self.battleOneMusic3.stop()
        self.battleOneMusic2.stop()
        self.setPosHpr(52.2653, 78.2118, 22, 307, 0, 0)
        self.setCageIndex(2)
        self.stickBossToFloor()
        intervalName = 'RollToBattleTwo'
        seq = Sequence(self.__makeRollToBattleTwoMovie(), Func(self.__onToPrepareBattleTwo), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        base.playMusic(self.betweenBattleMusic, looping=1, volume=0.9)
        self.__showEasyBarrels()
        taskMgr.doMethodLater(0.5, self.enableToonCollision, 'enableToonCollision')

    def __startBattleOneLoop(self, task):
        self.battleOneMusic2.play()
        return task.done

    def __onToPrepareBattleTwo(self):
        self.disableToonCollision()
       # self.unstickBoss()
        self.reparentTo(render)
        self.setPosHpr(52.2653, 78.2118, 22, 307, 0, 0)
        self.doneBarrier('RollToBattleTwo')

    def exitRollToBattleTwo(self):
        self.unstickBoss()
        intervalName = 'RollToBattleTwo'
        self.clearInterval(intervalName)
        self.betweenBattleMusic.stop()

    def disableToonCollision(self):
        base.localAvatar.collisionsOff()

    def enableToonCollision(self, task):
        base.localAvatar.collisionsOn()

    def enterPrepareBattleTwo(self):
        self.cleanupIntervals()
        self.__hideEasyBarrels()
        self.controlToons()
        self.clearChat()
        self.cagedToon.clearChat()
        self.reparentTo(render)
        self.setPosHpr(52.2653, 78.2118, 22, 307, 0, 0)
        self.setCageIndex(2)
        camera.reparentTo(render)
        camera.setPosHpr(self.cage, 0, -17, 3.3, 0, 0, 0)
        (localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov),)
        self.hide()
        self.__onToBattleTwo()
        base.playMusic(self.stingMusic, looping=0, volume=1.0)
        taskMgr.doMethodLater(0.5, self.enableToonCollision, 'enableToonCollision')

    def __onToBattleTwo(self):
        self.doneBarrier('PrepareBattleTwo')
        taskMgr.doMethodLater(1, self.__showWaitingMessage, self.uniqueName('WaitingMessage'))

    def exitPrepareBattleTwo(self):
        self.show()
        taskMgr.remove(self.uniqueName('WaitingMessage'))
        self.ignore('doneChatPage')
        self.__clearOnscreenMessage()
        self.stingMusic.stop()

    def enterBattleTwo(self):
        self.cleanupIntervals()
        mult = ToontownBattleGlobals.getBossBattleCreditMultiplier(2)
        localAvatar.inventory.setBattleCreditMultiplier(mult)
        self.reparentTo(render)
        self.setPosHpr(52.2653, 78.2118, 22, 307, 0, 0)
        self.accept('clickedNametag', self.__clickedNameTag)
        self.accept('friendAvatar', self.__handleFriendAvatar)
        self.accept('avatarDetails', self.__handleAvatarDetails)
        NametagGlobals.setWant2dNametags(False)
        NametagGlobals.setWantActiveNametags(True)
        self.clearChat()
        self.cagedToon.clearChat()
        self.releaseToons()
        self.toonsToBattlePosition(self.toonsA, self.battleANode)
        self.toonsToBattlePosition(self.toonsB, self.battleBNode)
        if self.battleA == None or self.battleB == None:
            cageIndex = 3
        else:
            cageIndex = 2
        self.setCageIndex(cageIndex)
        base.playMusic(self.battleTwoMusic, looping=1, volume=0.9)

    def __clickedNameTag(self, avatar):
        self.notify.debug('__clickedNameTag')
        if self.cr:
            place = self.cr.playGame.getPlace()
            if place and hasattr(place, 'fsm'):
                FriendsListManager.FriendsListManager._FriendsListManager__handleClickedNametag(place, avatar)

    def __handleFriendAvatar(self, avId, avName, avDisableName):
        self.notify.debug('__handleFriendAvatar')
        if self.cr:
            place = self.cr.playGame.getPlace()
            if place and hasattr(place, 'fsm'):
                FriendsListManager.FriendsListManager._FriendsListManager__handleFriendAvatar(place, avId, avName, avDisableName)

    def __handleAvatarDetails(self, avId, avName, playerId = None):
        self.notify.debug('__handleAvatarDetails')
        if self.cr:
            place = self.cr.playGame.getPlace()
            if place and hasattr(place, 'fsm'):
                FriendsListManager.FriendsListManager._FriendsListManager__handleAvatarDetails(place, avId, avName, playerId)

    def exitBattleTwo(self):
        intervalName = self.uniqueName('cageDrop')
        self.clearInterval(intervalName)
        self.cleanupBattles()
        self.battleTwoMusic.stop()
        localAvatar.inventory.setBattleCreditMultiplier(1)

    def enterPrepareBattleThree(self):
        self.cleanupIntervals()
        self.controlToons()
        self.clearChat()
        self.cagedToon.clearChat()
        self.reparentTo(render)
        self.setCageIndex(4)
        self.generateHealthBar()
        self.updateHealthBar()
        camera.reparentTo(render)
        camera.setPosHpr(self.cage, 0, -17, 3.3, 0, 0, 0)
        (localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov),)
        self.hide()
        self.acceptOnce('doneChatPage', self.__onToBattleThree)
        self.cagedToon.setLocalPageChat(TTLocalizer.CagedToonPrepareBattleThree, 1)
        base.playMusic(self.betweenBattleMusic, looping=1, volume=0.9)

    def __onToBattleThree(self, elapsed):
        self.doneBarrier('PrepareBattleThree')
        taskMgr.doMethodLater(1, self.__showWaitingMessage, self.uniqueName('WaitingMessage'))

    def exitPrepareBattleThree(self):
        self.show()
        taskMgr.remove(self.uniqueName('WaitingMessage'))
        self.ignore('doneChatPage')
        intervalName = 'PrepareBattleThree'
        self.clearInterval(intervalName)
        self.__clearOnscreenMessage()
        self.betweenBattleMusic.stop()

    def enterBattleThree(self):
        DistributedBossCog.DistributedBossCog.enterBattleThree(self)
        self.clearChat()
        self.cagedToon.clearChat()
        self.reparentTo(render)
        self.setCageIndex(4)
        self.happy = 0
        self.raised = 1
        self.forward = 1
        self.doAnimate()
        self.accept('enterCage', self.__touchedCage)
        self.accept('pieSplat', self.__pieSplat)
        self.accept('localPieSplat', self.__localPieSplat)
        self.accept('outOfPies', self.__outOfPies)
        self.accept('begin-pie', self.__foundPieButton)
        localAvatar.setCameraFov(ToontownGlobals.BossBattleCameraFov)
        taskMgr.doMethodLater(30, self.__howToGetPies, self.uniqueName('PieAdvice'))
        self.stickBossToFloor()
        self.bossDamageMovie = self.__makeBossDamageMovie()
        bossDoneEventName = self.uniqueName('DestroyedBoss')
        self.bossDamageMovie.setDoneEvent(bossDoneEventName)
        self.acceptOnce(bossDoneEventName, self.__doneBattleThree)
        self.resetMaxDamage()
        self.bossDamageToMovie = self.bossDamageMovie.getDuration() / self.bossMaxDamage
        self.bossDamageMovie.setT(self.bossDamage * self.bossDamageToMovie)
        base.playMusic(self.battleThreeMusic, looping=1, volume=0.9)

    def __doneBattleThree(self):
        self.setState('NearVictory')
        self.unstickBoss()

    def exitBattleThree(self):
        DistributedBossCog.DistributedBossCog.exitBattleThree(self)
        bossDoneEventName = self.uniqueName('DestroyedBoss')
        self.ignore(bossDoneEventName)
        taskMgr.remove(self.uniqueName('StandUp'))
        self.ignore('enterCage')
        self.ignore('pieSplat')
        self.ignore('localPieSplat')
        self.ignore('outOfPies')
        self.ignore('begin-pie')
        self.__clearOnscreenMessage()
        taskMgr.remove(self.uniqueName('PieAdvice'))
        localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        self.__removeCageShadow()
        self.bossDamageMovie.finish()
        self.bossDamageMovie = None
        self.unstickBoss()
        taskName = 'RecoverBossDamage'
        taskMgr.remove(taskName)
        self.battleThreeMusicTime = self.battleThreeMusic.getTime()
        self.battleThreeMusic.stop()

    def enterNearVictory(self):
        self.cleanupIntervals()
        self.reparentTo(render)
        self.setPos(*ToontownGlobals.SellbotBossDeathPos)
        self.setHpr(*ToontownGlobals.SellbotBossBattleThreeHpr)
        self.clearChat()
        self.cagedToon.clearChat()
        self.setCageIndex(4)
        self.releaseToons(finalBattle=1)
        self.accept('enterCage', self.__touchedCage)
        self.accept('pieSplat', self.__finalPieSplat)
        self.accept('localPieSplat', self.__localPieSplat)
        self.accept('outOfPies', self.__outOfPies)
        localAvatar.setCameraFov(ToontownGlobals.BossBattleCameraFov)
        self.happy = 0
        self.raised = 0
        self.forward = 1
        self.doAnimate()
        self.setDizzy(1)
        base.playMusic(self.battleThreeMusic, looping=1, volume=0.9, time=self.battleThreeMusicTime)

    def exitNearVictory(self):
        self.ignore('enterCage')
        self.ignore('pieSplat')
        self.ignore('localPieSplat')
        self.ignore('outOfPies')
        self.__clearOnscreenMessage()
        taskMgr.remove(self.uniqueName('PieAdvice'))
        localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        self.__removeCageShadow()
        self.setDizzy(0)
        self.battleThreeMusicTime = self.battleThreeMusic.getTime()
        self.battleThreeMusic.stop()

    def enterVictory(self):
        self.cleanupIntervals()
        localAvatar.setCameraFov(ToontownGlobals.BossBattleCameraFov)
        self.reparentTo(render)
        self.setPos(*ToontownGlobals.SellbotBossDeathPos)
        self.setHpr(*ToontownGlobals.SellbotBossBattleThreeHpr)
        self.clearChat()
        self.cagedToon.clearChat()
        self.setCageIndex(4)
        self.releaseToons(finalBattle=1)
        self.happy = 0
        self.raised = 0
        self.forward = 1
        self.doAnimate('Fb_fall', now=1)
        self.acceptOnce(self.animDoneEvent, self.__continueVictory)
        base.playMusic(self.battleThreeMusic, looping=1, volume=0.9, time=self.battleThreeMusicTime)

    def __continueVictory(self):
        self.stopAnimate()
        self.stash()
        self.doneBarrier('Victory')

    def exitVictory(self):
        self.stopAnimate()
        self.unstash()
        self.__removeCageShadow()
        localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        self.battleThreeMusicTime = self.battleThreeMusic.getTime()
        self.battleThreeMusic.stop()

    def enterReward(self):
        self.cleanupIntervals()
        self.clearChat()
        self.cagedToon.clearChat()
        self.stash()
        self.stopAnimate()
        self.setCageIndex(4)
        self.releaseToons(finalBattle=1)
        self.toMovieMode()
        panelName = self.uniqueName('reward')
        self.rewardPanel = RewardPanel.RewardPanel(panelName)
        victory, camVictory, skipper = MovieToonVictory.doToonVictory(1, self.involvedToons, self.toonRewardIds, self.toonRewardDicts, self.deathList, self.rewardPanel, allowGroupShot=0, uberList=self.uberList, noSkip=True)
        ival = Sequence(Parallel(victory, camVictory), Func(self.__doneReward))
        intervalName = 'RewardMovie'
        delayDeletes = []
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'SellbotBoss.enterReward'))

        ival.delayDeletes = delayDeletes
        ival.start()
        self.storeInterval(ival, intervalName)
        base.playMusic(self.battleThreeMusic, looping=1, volume=0.9, time=self.battleThreeMusicTime)

    def __doneReward(self):
        self.doneBarrier('Reward')
        self.toWalkMode()

    def exitReward(self):
        intervalName = 'RewardMovie'
        self.clearInterval(intervalName)
        self.unstash()
        self.rewardPanel.destroy()
        del self.rewardPanel
        self.__removeCageShadow()
        self.battleThreeMusicTime = 0
        self.battleThreeMusic.stop()

    def enterEpilogue(self):
        self.cleanupIntervals()
        self.clearChat()
        self.cagedToon.clearChat()
        self.stash()
        self.stopAnimate()
        self.setCageIndex(4)
        self.controlToons()
        self.__arrangeToonsAroundCage()
        base.camera.wrtReparentTo(render)
        base.camera.posHprInterval(1, Point3(-25, 52, 27.5), Point3(-53, -13, 0), blendType = 'easeInOut').start()
        intervalName = 'EpilogueMovie'
        seq = Sequence(self.__makeCageOpenMovie(), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        self.accept('nextChatPage', self.__epilogueChatNext)
        self.accept('doneChatPage', self.__epilogueChatDone)
        base.playMusic(self.epilogueMusic, looping=1, volume=0.9)

    def __epilogueChatNext(self, pageNumber, elapsed):
        if pageNumber == 2:
            if self.cagedToon.style.torso[1] == 'd':
                track = ActorInterval(self.cagedToon, 'curtsy')
            else:
                track = ActorInterval(self.cagedToon, 'bow')
            track = Sequence(track, Func(self.cagedToon.loop, 'neutral'))
            intervalName = 'EpilogueMovieToonAnim'
            self.storeInterval(track, intervalName)
            track.start()

    def __epilogueChatDone(self, elapsed):
        self.cagedToon.setChatAbsolute(TTLocalizer.CagedToonGoodbye, CFSpeech | CFTimeout)
        self.ignore('nextChatPage')
        self.ignore('doneChatPage')
        intervalName = 'EpilogueMovieToonAnim'
        self.clearInterval(intervalName)
        track = Parallel(Sequence(ActorInterval(self.cagedToon, 'wave'), Func(self.cagedToon.loop, 'neutral')), Sequence(Wait(0.5), Func(self.localToonToSafeZone)))
        self.storeInterval(track, intervalName)
        track.start()

    def exitEpilogue(self):
        self.clearInterval('EpilogueMovieToonAnim')
        self.unstash()
        self.__removeCageShadow()
        self.epilogueMusic.stop()

    def __arrangeToonsAroundCage(self):
        radius = 15
        numToons = len(self.involvedToons)
        center = (numToons - 1) / 2.0
        for i in range(numToons):
            toon = base.cr.doId2do.get(self.involvedToons[i])
            if toon:
                angle = 270 - 15 * (i - center)
                radians = angle * math.pi / 180.0
                x = math.cos(radians) * radius
                y = math.sin(radians) * radius
                toon.setPos(self.cage, x, y, 0)
                toon.setZ(18.0)
                toon.headsUp(self.cage)

    def enterFrolic(self):
        DistributedBossCog.DistributedBossCog.enterFrolic(self)
        self.setPosHpr(*ToontownGlobals.SellbotBossBattleOnePosHpr)

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
        points = BattleBase.BattleBase.toonPoints[len(toonIds) - 1]
        for i in range(len(toonIds)):
            toon = base.cr.doId2do.get(toonIds[i])
            if toon:
                toon.reparentTo(render)
                pos, h = points[i]
                toon.setPosHpr(battleNode, pos[0], pos[1] + 10, pos[2], h, 0, 0)

    def __doobersToPromotionPosition(self, doobers, battleNode):
        points = BattleBase.BattleBase.toonPoints[len(doobers) - 1]
        for i in range(len(doobers)):
            suit = doobers[i]
            suit.fsm.request('neutral')
            suit.loop('neutral')
            pos, h = points[i]
            suit.setPosHpr(battleNode, pos[0], pos[1] + 10, pos[2], h, 0, 0)

    def __touchedCage(self, entry):
        self.sendUpdate('touchCage', [])
        self.__clearOnscreenMessage()
        taskMgr.remove(self.uniqueName('PieAdvice'))
        base.playSfx(self.piesRestockSfx)
        if not self.everThrownPie:
            taskMgr.doMethodLater(30, self.__howToThrowPies, self.uniqueName('PieAdvice'))

    def __outOfPies(self):
        self.__showOnscreenMessage(TTLocalizer.BossBattleNeedMorePies)
        taskMgr.doMethodLater(20, self.__howToGetPies, self.uniqueName('PieAdvice'))

    def __howToGetPies(self, task):
        self.__showOnscreenMessage(TTLocalizer.BossBattleHowToGetPies)

    def __howToThrowPies(self, task):
        self.__showOnscreenMessage(TTLocalizer.BossBattleHowToThrowPies)

    def __foundPieButton(self):
        self.everThrownPie = 1
        self.__clearOnscreenMessage()
        taskMgr.remove(self.uniqueName('PieAdvice'))

    def __pieSplat(self, toon, pieCode):
        if base.config.GetBool('easy-vp', 0):
            if not self.dizzy:
                pieCode = ToontownGlobals.PieCodeBossInsides
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

    def __localPieSplat(self, pieCode, entry):
        if pieCode != ToontownGlobals.PieCodeToon:
            return
        avatarDoId = entry.getIntoNodePath().getNetTag('avatarDoId')
        if avatarDoId == '':
            self.notify.warning('Toon %s has no avatarDoId tag.' % repr(entry.getIntoNodePath()))
            return
        doId = int(avatarDoId)
        if doId != localAvatar.doId:
            self.d_hitToon(doId)

    def __finalPieSplat(self, toon, pieCode):
        if pieCode != ToontownGlobals.PieCodeBossCog:
            return
        self.sendUpdate('finalPieSplat', [])
        self.ignore('pieSplat')

    def cagedToonBattleThree(self, index, avId):
        str = TTLocalizer.CagedToonBattleThree.get(index)
        if str:
            toonName = ''
            if avId:
                toon = self.cr.doId2do.get(avId)
                if not toon:
                    self.cagedToon.clearChat()
                    return
                toonName = toon.getName()
            text = str % {'toon': toonName}
            self.cagedToon.setChatAbsolute("", CFSpeech | CFTimeout)
        else:
            self.cagedToon.clearChat()

    def cleanupAttacks(self):
        self.__cleanupStrafe()

    def __cleanupStrafe(self):
        if self.strafeInterval:
            self.strafeInterval.finish()
            self.strafeInterval = None

    def doStrafe(self, side, direction):
        gearRoot = self.rotateNode.attachNewNode('gearRoot')
        if side == 0:
            gearRoot.setPos(0, -7, 3)
            gearRoot.setHpr(180, 0, 0)
            door = self.doorA
        else:
            gearRoot.setPos(0, 7, 3)
            door = self.doorB
        gearRoot.setTag('attackCode', str(ToontownGlobals.BossCogStrafeAttack))
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
            gear = gearModel.instanceTo(node)
            angle = (float(i) / (numGears - 1) - 0.5) * spread
            x = dist * math.sin(angle)
            y = dist * math.cos(angle)
            h = random.uniform(-720, 720)
            gearTrack.append(Sequence(Wait(i * rate), Func(node.show), Parallel(node.posInterval(1, Point3(x, y, 0), fluid=1), node.hprInterval(1, VBase3(h, 0, 0), fluid=1), Sequence(SoundInterval(self.strafeSfx[i], volume=0.2, node=self), duration=0)), Func(node.detachNode)))

        seq = Sequence(Func(door.request, 'open'), Wait(0.7), gearTrack, Func(door.request, 'close'))
        self.__cleanupStrafe()
        self.strafeInterval = seq
        seq.start()

    def __showEasyBarrels(self):
        barrelNodes = hidden.findAllMatches('**/Distributed*Barrel-*')
        if not barrelNodes or barrelNodes.isEmpty():
            return
        if render.find('barrelsRootNode'):
            self.notify.warning('__showEasyBarrels(): barrelsRootNode already exists')
            return
        self.barrelsRootNode = render.attachNewNode('barrelsRootNode')
        self.barrelsRootNode.setPos(*SellbotBossGlobals.BarrelsStartPos)
        if self.arenaSide == 0:
            self.barrelsRootNode.setHpr(180, 0, 0)
        else:
            self.barrelsRootNode.setHpr(0, 0, 0)
        for i, barrelNode in enumerate(barrelNodes):
            barrel = base.cr.doId2do.get(int(barrelNode.getNetTag('doId')))
            SellbotBossGlobals.setBarrelAttr(barrel, barrel.entId)
            if hasattr(barrel, 'applyLabel'):
                barrel.applyLabel()
            barrel.setPosHpr(barrel.pos, barrel.hpr)
            barrel.reparentTo(self.barrelsRootNode)

        intervalName = 'MakeBarrelsAppear'
        seq = Sequence(LerpPosInterval(self.barrelsRootNode, 0.5, Vec3(*SellbotBossGlobals.BarrelsFinalPos), blendType='easeInOut'), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)

    def __hideEasyBarrels(self):
        if hasattr(self, 'barrelsRootNode'):
            self.barrelsRootNode.removeNode()
            intervalName = 'MakeBarrelsAppear'
            self.clearInterval(intervalName)

    def toonPromoted(self, promoted):
        self.localToonPromoted = promoted

    def setVPDoId(self, vpId):
        if vpId in self.cr.doId2do:
            self.setVPBoss(self.cr.doId2do[vpId])
        else:
            self.acceptOnce('generate-%d' % vpId, self.setVPBoss)

    def setVPBoss(self, vpBoss):
        self.vpBoss = vpBoss

    def setCFODoId(self, cfoId):
        if cfoId in self.cr.doId2do:
            self.setCFOBoss(self.cr.doId2do[cfoId])
        else:
            self.acceptOnce('generate-%d' % cfoId, self.setCFOBoss)

    def setCFOBoss(self, cfoBoss):
        self.cfoBoss = cfoBoss

    def setCJDoId(self, cjId):
        if cjId in self.cr.doId2do:
            self.setCJBoss(self.cr.doId2do[cjId])
        else:
            self.acceptOnce('generate-%d' % cjId, self.setCJBoss)

    def setCJBoss(self, cjBoss):
        self.cjBoss = cjBoss

    def setCEODoId(self, ceoId):
        if ceoId in self.cr.doId2do:
            self.setCEOBoss(self.cr.doId2do[ceoId])
        else:
            self.acceptOnce('generate-%d' % ceoId, self.setCEOBoss)

    def setCEOBoss(self, ceoBoss):
        self.ceoBoss = ceoBoss