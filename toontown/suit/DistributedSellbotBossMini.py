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
import math
from toontown.friends import FriendsListManager
from toontown.nametag import NametagGlobals
from toontown.nametag import NametagGroup
from pandac.PandaModules import *
import random
from toontown.battle import BattleProps
from toontown.suit import DistributedBossCog
from toontown.suit import SuitDNA
from toontown.battle import BattleBase
from toontown.battle import BattleParticles
from toontown.battle import MovieToonVictory
from toontown.battle import RewardPanel
from toontown.battle import SuitBattleGlobals
from toontown.battle.BattleProps import *
from toontown.chat.ChatGlobals import *
from toontown.coghq import CogDisguiseGlobals
from toontown.distributed import DelayDelete
from toontown.nametag.NametagGlobals import *
from toontown.suit import SellbotBossGlobals
from toontown.toon import NPCToons
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import ToontownGlobals

OneBossCog = None

class DistributedSellbotBossMini(DistributedBossCog.DistributedBossCog, FSM.FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSellbotBossMini')


    cageHeights = [100,
     81,
     63,
     44,
     25,
     18]

    def __init__(self, cr):
        DistributedBossCog.DistributedBossCog.__init__(self, cr)
        FSM.FSM.__init__(self, 'DistributedSellbotBossMini')
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
        self.cageIndex = 0
        self.everThrownPie = 0
        self.battleThreeMusicTime = 0
        self.insidesANodePath = None
        self.insidesBNodePath = None
        self.rampA = None
        self.rampB = None
        self.rampC = None
        self.strafeInterval = None
        self.onscreenMessage = None
        self.helicopter = None
        self.helicopter2 = None
        self.tv = None
        self.tv2 = None
        self.tv3 = None
        self.tv4 = None
        self.toonMopathInterval = []
        self.nerfed = ToontownGlobals.SELLBOT_NERF_HOLIDAY in base.cr.newsManager.getHolidayIdList()
        self.localToonPromoted = True
        self.resetMaxDamage()
        self.maxHP = self.bossMaxDamage

        from toontown.suit.DistributedSuitBase import DistributedSuitBase
        self.pressurizer = DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('safesupervis')
        self.pressurizer.setDNA(suitDNA)
        self.pressurizer.setPickable(0)
        self.pressurizer.setDisplayName('Pressurizer\nSellbot\nLevel 45.mgr')
        self.pressurizer.doId = 0
        self.pressurizer.loop('sit-exec')

        self.unionbuster = DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('ubuster')
        self.unionbuster.setDNA(suitDNA)
        self.unionbuster.setPickable(0)
        self.unionbuster.setDisplayName('Union Buster\nSellbot\nLevel 40.mgr')
        self.unionbuster.doId = 0
        self.unionbuster.loop('sit-exec')

        self.racketeer = DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('racket')
        self.racketeer.setDNA(suitDNA)
        self.racketeer.setPickable(0)
        self.racketeer.setDisplayName('Racketeer\nSellbot\nLevel 40.mgr')
        self.racketeer.doId = 0
        self.racketeer.loop('sit-exec')

        self.radiographer = DistributedSuitBase(cr)
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit('radiog')
        self.radiographer.setDNA(suitDNA)
        self.radiographer.setPickable(0)
        self.radiographer.setDisplayName('Radiographer\nSellbot\nLevel 35.mgr')
        self.radiographer.doId = 0
        self.radiographer.loop('sit-exec')

    def hidePressurizer(self):
        self.pressurizer.hide()

    def hideUnionBuster(self):
        self.unionbuster.hide()

    def hideRacketeer(self):
        self.racketeer.hide()

    def hideRadiographer(self):
        self.radiographer.hide()

    def announceGenerate(self):
        global OneBossCog
        DistributedBossCog.DistributedBossCog.announceGenerate(self)
        self.setName('Senior V.P.')
        nameInfo = TTLocalizer.BossCogNameWithDept % {'name': self.name,
         'dept': SuitDNA.getDeptFullname(self.style.dept)}
        self.setDisplayName(nameInfo)
        self.cageDoorSfx = loader.loadSfx('phase_5/audio/sfx/CHQ_SOS_cage_door.ogg')
        self.cageLandSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_cage_land.ogg')
        self.cageLowerSfx = loader.loadSfx('phase_5/audio/sfx/CHQ_SOS_cage_lower.ogg')
        self.piesRestockSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_pies_restock.ogg')
        self.rampSlideSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_ramp_slide.ogg')
        self.strafeSfx = []
        for i in xrange(10):
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
        self.cagedToon.setPosHpr(0, -2, 0, 180, 0, 0)
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
        self.pressurizer.reparentTo(self.geom)
        self.pressurizer.setPosHpr(102.75, -10, 20.5, -90, 0, 0)
        self.unionbuster.reparentTo(self.geom)
        self.unionbuster.setPosHpr(-102.75, -10, 20.5, 90, 0, 0)
        self.racketeer.reparentTo(self.geom)
        self.racketeer.setPosHpr(77, 38.5, 20.5, -45, 0, 0)
        self.radiographer.reparentTo(self.geom)
        self.radiographer.setPosHpr(-77, 38.5, 20.5, 45, 0, 0)
        light = loader.loadModel('phase_14/models/props/CN-streetlight')
        light.setScale(2.0)
        light.reparentTo(self.geom)
        light.setPosHpr(85, -10, 18, 90, 0, 0)
        light2 = loader.loadModel('phase_14/models/props/CN-streetlight')
        light2.setScale(2.0)
        light2.reparentTo(self.geom)
        light2.setPosHpr(-85, -10, 18, -90, 0, 0)
        light3 = loader.loadModel('phase_14/models/props/CN-streetlight')
        light3.setScale(2.0)
        light3.reparentTo(self.geom)
        light3.setPosHpr(65, 27, 18, 135, 0, 0)
        light4 = loader.loadModel('phase_14/models/props/CN-streetlight')
        light4.setScale(2.0)
        light4.reparentTo(self.geom)
        light4.setPosHpr(-65, 27, 18, -135, 0, 0)
        chairPressurizer = loader.loadModel('phase_11/models/lawbotHQ/LawbotBossRoomChair')
        chairPressurizer.setScale(0.75)
        chairPressurizer.reparentTo(self.geom)
        chairPressurizer.setPosHpr(100, -10, 18, -90, 0, 0)
        chairUnionBuster = loader.loadModel('phase_11/models/lawbotHQ/LawbotBossRoomChair')
        chairUnionBuster.setScale(0.75)
        chairUnionBuster.reparentTo(self.geom)
        chairUnionBuster.setPosHpr(-100, -10, 18, 90, 0, 0)
        chairRacketeer = loader.loadModel('phase_11/models/lawbotHQ/LawbotBossRoomChair')
        chairRacketeer.setScale(0.75)
        chairRacketeer.reparentTo(self.geom)
        chairRacketeer.setPosHpr(75, 37, 18, -45, 0, 0)
        chairRadiographer = loader.loadModel('phase_11/models/lawbotHQ/LawbotBossRoomChair')
        chairRadiographer.setScale(0.75)
        chairRadiographer.reparentTo(self.geom)
        chairRadiographer.setPosHpr(-75, 37, 18, 45, 0, 0)
        self.loop('Bb_neutral')
        track2 = Parallel()
        dooberTrack = Parallel()
        if self.doobers:
            self.__doobersToPromotionPosition(self.doobers)
            turnPosA = ToontownGlobals.SellbotBossDooberTurnPosA
            turnPosB = ToontownGlobals.SellbotBossDooberTurnPosB
            self.__walkDoober(self.doobers[0], 0, turnPosA, dooberTrack, delayDeletes)
            self.__walkDoober(self.doobers[1], 1.5, turnPosB, dooberTrack, delayDeletes)
            self.__walkDoober(self.doobers[2], 3, turnPosA, dooberTrack, delayDeletes)
            self.__walkDoober(self.doobers[3], 4.5, turnPosB, dooberTrack, delayDeletes)
            self.__walkDoober(self.doobers[4], 6, turnPosA, dooberTrack, delayDeletes)
            self.__walkDoober(self.doobers[5], 7.5, turnPosB, dooberTrack, delayDeletes)
            self.__walkDoober(self.doobers[6], 9, turnPosA, dooberTrack, delayDeletes)
            self.__walkDoober(self.doobers[7], 10.5, turnPosB, dooberTrack, delayDeletes)
            self.__walkDoober(self.doobers[8], 12, turnPosA, dooberTrack, delayDeletes)
            self.__walkDoober(self.doobers[9], 13.5, turnPosB, dooberTrack, delayDeletes)
            self.__walkDoober(self.doobers[10], 15, turnPosA, dooberTrack, delayDeletes)
            self.__walkDoober(self.doobers[11], 16.5, turnPosB, dooberTrack, delayDeletes)

        loseSuitCamAngle = (0, 19, 6, -180, 0, 0)
        tempNode = self.attachNewNode('temp')
        tempNode.setPos(0, 60, 15)

        def getCamBossPos(tempNode=tempNode):
            return tempNode.getPos(render)

        tempNode2 = self.attachNewNode('temp')
        tempNode2.setPos(0, -55, 15)

        def getCamBossPos2(tempNode2=tempNode2):
            return tempNode2.getPos(render)

        pressurizerNode = self.attachNewNode('temp')
        pressurizerNode.reparentTo(self.geom)
        pressurizerNode.setPosHpr(125.75, -10, 30, 90, 0, 0)

        def getCamBossPosPressurizer(pressurizerNode=pressurizerNode):
            return pressurizerNode.getPos(render)

        unionbusterNode = self.attachNewNode('temp')
        unionbusterNode.reparentTo(self.geom)
        unionbusterNode.setPosHpr(-125.75, -10, 30, -90, 0, 0)

        def getCamBossPosUnionBuster(unionbusterNode=unionbusterNode):
            return unionbusterNode.getPos(render)

        racketeerNode = self.attachNewNode('temp')
        racketeerNode.reparentTo(self.geom)
        racketeerNode.setPosHpr(90, 51.5, 30, 135, 0, 0)

        def getCamBossPosRackteer(racketeerNode=racketeerNode):
            return racketeerNode.getPos(render)

        radiographerNode = self.attachNewNode('temp')
        radiographerNode.reparentTo(self.geom)
        radiographerNode.setPosHpr(-90, 51.5, 30, -135, 0, 0)

        def getCamBossPosRadiographer(radiographerNode=radiographerNode):
            return radiographerNode.getPos(render)

        dooberTrack2 = Parallel()
        for i in xrange(len(self.doobers)):
            suit = self.doobers[i]
            dooberTrack2.append(Parallel(Sequence(ActorInterval(suit, 'slip-forward'), Func(suit.loop, 'neutral')), Sequence(Func(suit.setChatAbsolute, "We will not let you down, Sir!", CFSpeech), Wait(5.0), Func(suit.setChatAbsolute, "", CFSpeech))))

        track = Sequence(self.loseCogSuits(self.toonsA + self.toonsB, base.localAvatar, loseSuitCamAngle), Wait(2.0), Func(camera.setH, 0), Func(camera.reparentTo, render),
                         LerpPosInterval(camera, 3, getCamBossPos),
                         Func(self.setChatAbsolute, "Let's review the current situation.", CFSpeech), Wait(4.0),
                         Func(self.setChatAbsolute, "Toontown has always been... predictable.", CFSpeech), Wait(4.0),
                         Func(self.setChatAbsolute, "Disorganized enthusiasm. Chaotic little rebellions that burn out just as quickly as they start.", CFSpeech), Wait(4.0),
                         Func(self.setChatAbsolute, "But lately?", CFSpeech), Wait(3.0),
                         Func(self.setChatAbsolute, "They've been far more persistent.", CFSpeech), Wait(4.0),
                         Parallel(Func(self.setChatAbsolute, "Pressurizer, what is your analysis?", CFSpeech), Wait(2.0),
                                  Sequence(ActorInterval(self, 'Ff_lookLt'), Func(self.loop, 'Bb_neutral'))),
                         Parallel(Func(self.setChatAbsolute, "", CFSpeech), LerpPosInterval(camera, 2, getCamBossPosPressurizer), LerpHprInterval(camera, 2, pressurizerNode.getHpr), Sequence(Wait(2),
                     Func(self.pressurizer.setChatAbsolute, "These Toons may be more persistent, but their performance is sloppy.", CFSpeech | CFTimeout))),
                         Wait(4.0),
                         Func(self.pressurizer.setChatAbsolute, "Their movement patterns are easy to track.", CFSpeech | CFTimeout),
                         Wait(4.0),
                         Func(self.pressurizer.setChatAbsolute, "Their heat signatures light up like fireworks.", CFSpeech | CFTimeout),
                         Wait(4.0),
                         Func(self.pressurizer.setChatAbsolute, "They never realize how visible they are.", CFSpeech | CFTimeout),
                         Wait(4.0),
                         Parallel(LerpPosInterval(camera, 2, getCamBossPosRackteer), LerpHprInterval(camera, 2, racketeerNode.getHpr), Sequence(Wait(2),
                        Func(self.racketeer.setChatAbsolute, "That's because they think they're clever.", CFSpeech | CFTimeout))),
                         Wait(4.0),
                         Func(self.racketeer.setChatAbsolute, "Break a few operations... knock over a few Cogs...", CFSpeech | CFTimeout),
                         Wait(4.0),
                         Func(self.racketeer.setChatAbsolute, "Suddenly they think they're running the place.", CFSpeech | CFTimeout),
                         Wait(4.0),
                         Func(self.racketeer.setChatAbsolute, "Heh, I can't wait to collect on that mistake!", CFSpeech | CFTimeout),
                         Wait(4.0),
                         Parallel(LerpPosInterval(camera, 2, getCamBossPosUnionBuster), LerpHprInterval(camera, 2, unionbusterNode.getHpr), Sequence(Wait(2),
                           Func(self.unionbuster.setChatAbsolute, "Teamwork.",  CFSpeech | CFTimeout))),
                         Wait(4.0),
                         Func(self.unionbuster.setChatAbsolute, "That's their whole trick.", CFSpeech | CFTimeout),
                         Wait(4.0),
                         Func(self.unionbuster.setChatAbsolute, "They rally together, shout a few slogans, throw pies around...", CFSpeech | CFTimeout),
                         Wait(4.0),
                         Func(self.unionbuster.setChatAbsolute, "Then when the pressure finally hits... they scatter.", CFSpeech | CFTimeout),
                         Wait(4.0),
                         Parallel(LerpPosInterval(camera, 2, getCamBossPosPressurizer), LerpHprInterval(camera, 2, pressurizerNode.getHpr), Sequence(Wait(2),
                         Func(self.pressurizer.setChatAbsolute, "They don't scatter.",  CFSpeech | CFTimeout))),
                         Wait(4.0),
                         Func(self.pressurizer.setChatAbsolute, "They compress.", CFSpeech | CFTimeout),
                         Wait(4.0),
                         Func(self.pressurizer.setChatAbsolute, "Toons build momentum. They lean on each other.", CFSpeech | CFTimeout),
                         Wait(4.0),
                         Func(self.pressurizer.setChatAbsolute, "But if you apply pressure in the right place... they collapse!", CFSpeech | CFTimeout),
                         Wait(4.0),
                         Parallel(LerpPosInterval(camera, 2, getCamBossPos), LerpHprInterval(camera, 2, (0, 0, 0))),
                         Func(self.setChatAbsolute, "That's exactly why the Pressure Division exists.", CFSpeech), Wait(4.0),
                         Func(self.pelvis.setH, 180),
                         Parallel(ActorInterval(self, 'Ff_speech'), Func(self.setChatAbsolute, "Radiographer... You watch them.", CFSpeech)),
                         Parallel(ActorInterval(self, 'Ff_speech'), Func(self.setChatAbsolute, "Racketeer... You squeeze them.", CFSpeech)),
                         Parallel(ActorInterval(self, 'Ff_speech'), Func(self.setChatAbsolute, "Union Buster... You fracture their cooperation.", CFSpeech)),
                         Parallel(Func(self.pelvis.setH, 180), Parallel(ActorInterval(self, 'Ff_lookLt'), Func(self.loop, 'Ff_neutral')), Func(self.setChatAbsolute, "And you Pressurizer...", CFSpeech),),
                                  Func(self.setChatAbsolute, "", CFSpeech),
                    Parallel(LerpPosInterval(camera, 2, getCamBossPosRadiographer), LerpHprInterval(camera, 2, radiographerNode.getHpr), Wait(2),
                          Func(self.radiographer.setChatAbsolute, "Um... Sir?", CFSpeech | CFTimeout)), Wait(2.0),
                         Parallel(LerpHprInterval(camera, 2, (0, 0, 0)), LerpPosInterval(camera, 2, getCamBossPos)),
                         Parallel(Func(self.pelvis.setH, 180), Parallel(ActorInterval(self, 'Ff_lookRt'), Func(self.loop, 'Ff_neutral')), Func(self.setChatAbsolute, "What is it?", CFSpeech), Wait(4.0)),
                         Func(self.setChatAbsolute, "", CFSpeech),
                         Parallel(LerpPosInterval(camera, 2, getCamBossPosRadiographer), LerpHprInterval(camera, 2, radiographerNode.getHpr), Wait(2),
                                  Func(self.radiographer.setChatAbsolute, "You may want to finish that sentence later...", CFSpeech | CFTimeout)), Wait(2.0),
                         Func(self.radiographer.setChatAbsolute, "Your audience has arrived.", CFSpeech | CFTimeout), Wait(3.0),
                         Parallel(LerpHprInterval(camera, 2, (180, 0, 0)), LerpPosInterval(camera, 2, getCamBossPos2),
                         Sequence(ActorInterval(self, 'Bb2Ff_spin'), Func(self.pelvis.setH, 0), Func(self.loop, 'Ff_neutral')), Func(self.setChatAbsolute, "Well well well...", CFSpeech), Wait(4.0)),
                         Parallel(Func(self.pelvis.setH, 0), ActorInterval(self, 'turn2Fb'), Func(self.setChatAbsolute, "That saves us the trouble of sending an invitation.", CFSpeech), Wait(4.0)),
                         Parallel(ActorInterval(self, 'Ff_speech'), ActorInterval(self, 'Ff_speech'), Func(self.setChatAbsolute, "You've arrived in the middle of an executive meeting.", CFSpeech)),
                         Parallel(ActorInterval(self, 'Ff_speech'), Func(self.setChatAbsolute, "But since you're already here...", CFSpeech)),
                         Parallel(ActorInterval(self, 'Ff_speech'), ActorInterval(self, 'Ff_speech'), Func(self.setChatAbsolute, "You may as well stay for the demonstration.", CFSpeech)),
                         Parallel(Func(self.loop, 'Ff_neutral'), Func(self.setChatAbsolute, "You see, Toons... I already know why you came.", CFSpeech), Wait(4.0)),
                         Parallel(Func(self.loop, 'Ff_neutral'), Func(self.setChatAbsolute, "You came up here thinking you will win.", CFSpeech), Wait(4.0)),
                         Parallel(Func(self.loop, 'Ff_neutral'), Func(self.setChatAbsolute, "And I'm glad you do, confidence makes the fall much more satisfying!", CFSpeech), Wait(4.0)),
                         Parallel(Func(self.loop, 'Ff_neutral'), Func(self.setChatAbsolute, "And we were just discussing...", CFSpeech), Wait(4.0)),
                         Parallel(Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/CHQ_VP_big_jump_stomp.ogg')),
                                  Sequence(ActorInterval(self, 'Fb_jump'), Func(self.loop, 'Ff_neutral')), Func(self.setChatAbsolute, "DEPLOYMENT!", CFSpeech), Sequence(Wait(1.25), dooberTrack2), Wait(4.0)),
                         Parallel(dooberTrack, Sequence(Parallel(Func(self.loop, 'Ff_neutral'), Func(self.setChatAbsolute, "These units will be restoring order across Toontown.", CFSpeech), Wait(4.0)),
                         Parallel(Func(self.loop, 'Ff_neutral'), Func(self.setChatAbsolute, "Something your kind has been interfering with far too often.", CFSpeech), Wait(4.0)),
                         Parallel(LerpHprInterval(camera, 2, (0, 0, 0)), LerpPosInterval(camera, 2, getCamBossPos)),
                         Parallel(Sequence(ActorInterval(self, 'Bb2Ff_spin'), Func(self.pelvis.setH, 180), Func(self.loop, 'Ff_neutral')), Func(self.setChatAbsolute, "Pressurizer... you and the Pressure Division were hoping for field work.", CFSpeech), Wait(3.0)),
                         Parallel(Func(self.loop, 'Ff_neutral'), Func(self.setChatAbsolute, "Now you have it.", CFSpeech), Wait(3.0)), Func(self.setChatAbsolute, "", CFSpeech),
                         Parallel(LerpPosInterval(camera, 2, getCamBossPosPressurizer), LerpHprInterval(camera, 2, pressurizerNode.getHpr), Sequence(Wait(2),
                          Func(self.pressurizer.setChatAbsolute, "Toons.", CFSpeech | CFTimeout))), Wait(3.0),
                         Func(self.pressurizer.setChatAbsolute, "You pushed your way in here.", CFSpeech | CFTimeout),
                         Wait(4.0),
                         Func(self.pressurizer.setChatAbsolute, "Now let's see how long you last!", CFSpeech | CFTimeout), Wait(3.0),
                                  Parallel(LerpPosInterval(camera, 2, getCamBossPosRackteer), LerpHprInterval(camera, 2, racketeerNode.getHpr), Sequence(Wait(2),
                                Func(self.racketeer.setChatAbsolute,  "Sounds like a profitable evening.",  CFSpeech | CFTimeout))),
                                  Wait(3.0),
                                  Parallel(LerpPosInterval(camera, 2, getCamBossPosRadiographer), LerpHprInterval(camera, 2, radiographerNode.getHpr), Sequence(Wait(2),
                                           Func(self.radiographer.setChatAbsolute, "I've already started recording.", CFSpeech | CFTimeout))), Wait(3.0),
                                  Func(self.radiographer.setChatAbsolute, "Every mistake they make is archived.", CFSpeech | CFTimeout), Wait(3.0),
                                  Parallel(LerpPosInterval(camera, 2, getCamBossPosUnionBuster), LerpHprInterval(camera, 2, unionbusterNode.getHpr), Sequence(Wait(2),
                                    Func(self.unionbuster.setChatAbsolute, "They'll break eventually. They always do.", CFSpeech | CFTimeout))),
                                  Wait(3.0),
                                  Parallel(LerpPosInterval(camera, 2, getCamBossPosPressurizer), LerpHprInterval(camera, 2, pressurizerNode.getHpr), Sequence(Wait(2),
                                  Func(self.pressurizer.setChatAbsolute,   "Not eventually.",  CFSpeech | CFTimeout))),
                                  Wait(3.0), Func(self.pressurizer.setChatAbsolute,   "Soon.",  CFSpeech | CFTimeout), Wait(2.0),
                         Parallel(LerpHprInterval(camera, 2, (0, 0, 0)), LerpPosInterval(camera, 2, getCamBossPos)),
                         Func(self.setChatAbsolute, "Try to make it interesting.", CFSpeech), Wait(4.0),
                         Parallel(Func(self.setChatAbsolute, "Pressure Division, take care of these Toons now!", CFSpeech), Sequence(ActorInterval(self, 'Ff_point'), Func(self.loop, 'Ff_neutral'))),
                         Wait(4.0),
                         Parallel(Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/CHQ_VP_big_jump_stomp.ogg')),
                                  Parallel(LerpHprInterval(camera, 1, (180, 0, 0)), LerpPosInterval(camera, 1, getCamBossPos2)), Sequence(ActorInterval(self, 'Fb_jump'), Func(self.loop, 'Ff_neutral')),
                                  LerpPosHprInterval(self, 1, (0, -35, 0), (180, 0, 0)), Wait(4.0)), Func(self.setChatAbsolute, "", CFSpeech)))
                         )


        return track

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
        bossTrack.append(Func(self.loop, 'Fb_neutral'))
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
        startPos = Point3(0, 60, 18)
        startHpr = Point3(180, 0, 0)
        bottomPos = Point3(0, -110, -6.5)
        deathPos = Point3(0, -175, -6.5)
        self.setPosHpr(startPos, startHpr)
        bossTrack = Sequence()
        bossTrack.append(Func(self.loop, 'Fb_neutral'))
        track, hpr = self.rollBossToPoint(startPos, startHpr, bottomPos, None, 1)
        bossTrack.append(track)
        track, hpr = self.rollBossToPoint(bottomPos, startHpr, deathPos, None, 1)
        bossTrack.append(track)
        duration = bossTrack.getDuration()
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

    def loadEnvironment(self):
        DistributedBossCog.DistributedBossCog.loadEnvironment(self)
        self.geom = loader.loadModel('phase_9/models/cogHQ/BossRoomPOV')
        self.helicopter = globalPropPool.getProp('CogNationChopper')
        self.helicopter.reparentTo(self.geom)
        self.helicopter.loop('CogNationChopper')
        self.helicopter.setPosHpr(0, -200, 0, 180, 0, 0)
        self.helicopter.setScale(1.0)
        self.helicopter2 = globalPropPool.getProp('cogChopper_ctc')
        self.helicopter2.reparentTo(self.geom)
        self.helicopter2.loop('cogChopper_ctc')
        self.helicopter2.setPosHpr(50, -225, 0, 180, 0, 0)
        self.helicopter2.setScale(1.0)
        self.tv = loader.loadModel('phase_9/models/cogHQ/multislacker_tv')
        self.tv.reparentTo(self.geom)
        self.tv.setScale(2.0)
        self.tv.setPosHpr(130, -10, 17.9522, 0, 0, 0)
        screen = loader.loadModel('phase_9/models/cogHQ/ms_tvScreen')
        screen.reparentTo(self.tv.find('**/tvScreen_origin'))
        self.tv2 = loader.loadModel('phase_9/models/cogHQ/multislacker_tv')
        self.tv2.reparentTo(self.geom)
        self.tv2.setScale(2.0)
        self.tv2.setPosHpr(-130, -10, 17.9522, 180, 0, 0)
        screen = loader.loadModel('phase_9/models/cogHQ/ms_tvScreen')
        screen.reparentTo(self.tv2.find('**/tvScreen_origin'))
        self.tv3 = loader.loadModel('phase_9/models/cogHQ/multislacker_tv')
        self.tv3.reparentTo(self.geom)
        self.tv3.setScale(2.0)
        self.tv3.setPosHpr(90, 52, 17.9522, 45, 0, 0)
        screen = loader.loadModel('phase_9/models/cogHQ/ms_tvScreen')
        screen.reparentTo(self.tv3.find('**/tvScreen_origin'))
        self.tv4 = loader.loadModel('phase_9/models/cogHQ/multislacker_tv')
        self.tv4.reparentTo(self.geom)
        self.tv4.setScale(2.0)
        self.tv4.setPosHpr(-90, 52, 17.9522, 135, 0, 0)
        screen = loader.loadModel('phase_9/models/cogHQ/ms_tvScreen')
        screen.reparentTo(self.tv4.find('**/tvScreen_origin'))
        self.rampA = self.geom.find('**/north_ramp')
        self.rampB = self.geom.find('**/west_ramp')
        self.rampC = self.geom.find('**/east_ramp')
        self.cage = self.geom.find('**/cage')
        elevatorEntrance = self.geom.find('**/elevator_locator')
        elevatorEntrance.getChildren().detach()
        elevatorEntrance.setScale(1)
        elevatorModel = loader.loadModel('phase_9/models/cogHQ/cogHQ_elevator')
        elevatorModel.reparentTo(elevatorEntrance)
        self.setupElevator(elevatorModel)
        pos = self.cage.getPos()
        self.cagePos = []
        for height in self.cageHeights:
            self.cagePos.append(Point3(pos[0], pos[1], height))

        self.cageDoor = self.geom.find('**/cage_door')
        self.cage.setScale(1)
        self.rope = Rope.Rope(name='supportChain')
        texture = loader.loadTexture('phase_9/maps/hq_chain.png')
        self.rope.setTexture(texture, 1)
        self.rope.reparentTo(self.cage)
        self.rope.setup(2, ((self.cage, (0.15, 0.13, 16)), (self.geom, (0.23, 78, 120))))
        self.rope.ropeNode.setRenderMode(RopeNode.RMBillboard)
        self.rope.ropeNode.setUvMode(RopeNode.UVDistance)
        self.rope.ropeNode.setUvDirection(0)
        self.rope.ropeNode.setUvScale(0.8)
        self.rope.setTransparency(1)
        self.toonsDiscovered = base.loadMusic('phase_9/audio/bgm/encntr_sting_announce.ogg')
        self.betweenBattleMusic = base.loadMusic('phase_9/audio/bgm/encntr_toon_winning.ogg')
        self.battleTwoMusic = base.loadMusic('phase_7/audio/bgm/encntr_suit_winning_indoor.ogg')
        self.battleThreeMusic = base.loadMusic('phase_9/audio/bgm/encntr_head_suit_theme.ogg')
        self.promotionMusic = base.loader.loadMusic('phase_14/audio/bgm/ET_boss_prep.ogg')
        self.betweenPhaseMusic = base.loader.loadMusic('phase_9/audio/bgm/encntr_toon_winning.ogg')
        self.battleOneMusic = loader.loadMusic('phase_12/audio/bgm/encntr_penultimate_intro.ogg')
        self.battleOneMusic2 = loader.loadMusic('phase_12/audio/bgm/encntr_penultimate_unlock-loop.ogg')
        self.battleOneMusic3 = loader.loadMusic('phase_12/audio/bgm/encntr_penultimate_intro.ogg')
        self.geom.reparentTo(render)
        self.setPosHpr(0, 60, 18, 0, 0, 0)

    def unloadEnvironment(self):
        DistributedBossCog.DistributedBossCog.unloadEnvironment(self)
        self.geom.removeNode()
        del self.geom
        del self.cage
        del self.rampA
        del self.rampB
        del self.rampC
        del self.helicopter
        del self.helicopter2

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
        self.setCageIndex(0)
        self.reparentTo(render)
        self.setPosHpr(0, 50, 18, 180, 0, 0)
        self.happy = 1
        self.raised = 1
        self.forward = 1
        #self.doAnimate()
        self.loop('Bb_neutral')
        self.cagedToon.removeActive()
        base.camLens.setMinFov(ToontownGlobals.VPElevatorFov/(4./3.))

    def exitElevator(self):
        DistributedBossCog.DistributedBossCog.exitElevator(self)
        self.cagedToon.addActive()

    def enterIntroduction(self):
        self.reparentTo(render)
        self.setPosHpr(0, 50, 18, 180, 0, 0)
        self.stopAnimate()
        DistributedBossCog.DistributedBossCog.enterIntroduction(self)
        self.accept('clickedNametag', self.__clickedNameTag)
        self.accept('friendAvatar', self.__handleFriendAvatar)
        self.accept('avatarDetails', self.__handleAvatarDetails)
        NametagGlobals.setWant2dNametags(False)
        NametagGlobals.setWantActiveNametags(True)
        self.setCageIndex(0)
        base.playMusic(self.promotionMusic, looping=1, volume=0.9)
        self.loop('Bb_neutral')

    def exitIntroduction(self):
        self.reparentTo(render)
        self.setPosHpr(0, 50, 18, 0, 0, 0)
        DistributedBossCog.DistributedBossCog.exitIntroduction(self)
        self.promotionMusic.stop()

    def enterBattleOne(self):
        DistributedBossCog.DistributedBossCog.enterBattleOne(self)
        self.reparentTo(render)
        self.setPosHpr(0, - 35, 0, 0, 0, 0)
        self.accept('clickedNametag', self.__clickedNameTag)
        self.accept('friendAvatar', self.__handleFriendAvatar)
        self.accept('avatarDetails', self.__handleAvatarDetails)
        NametagGlobals.setWant2dNametags(False)
        NametagGlobals.setWantActiveNametags(True)
        self.clearChat()
        self.cagedToon.clearChat()

        self.battleOneMusic2.setLoop(True)
        self.battleOneMusic3.play()
        self.battleOneMusic.stop()

        if self.battleA == None or self.battleB == None:
            cageIndex = 1
        else:
            cageIndex = 0
        taskMgr.doMethodLater(
            self.battleOneMusic3.length(),
            self.__startBattleOneLoop,
            'startBattleOneLoop'
        )
        self.setCageIndex(cageIndex)

    def __startBattleOneLoop(self, task):
        self.battleOneMusic2.play()
        return task.done

    def exitBattleOne(self):
        DistributedBossCog.DistributedBossCog.exitBattleOne(self)

    def enterRollToBattleTwo(self):
        self.disableToonCollision()
        self.releaseToons()
        self.battleOneMusic2.stop()
        self.reparentTo(render)
        self.setCageIndex(2)
        self.battleOneMusic3.stop()
        self.battleOneMusic2.stop()
        self.stickBossToFloor()
        intervalName = 'RollToBattleTwo'
        seq = Sequence(self.__makeRollToBattleTwoMovie(), Func(self.__onToPrepareBattleTwo), name=intervalName)
        seq.start()
        self.storeInterval(seq, intervalName)
        base.playMusic(self.betweenBattleMusic, looping=1, volume=0.9)
        self.__showEasyBarrels()
        taskMgr.doMethodLater(0.5, self.enableToonCollision, 'enableToonCollision')

    def __onToPrepareBattleTwo(self):
        self.disableToonCollision()
        self.unstickBoss()
        self.setPosHpr(0, 60, 18, 0, 0, 0)
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
        self.setPosHpr(0, 60, 18, 0, 0, 0)
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
        self.accept('clickedNametag', self.__clickedNameTag)
        self.accept('friendAvatar', self.__handleFriendAvatar)
        self.accept('avatarDetails', self.__handleAvatarDetails)
        NametagGlobals.setWant2dNametags(False)
        NametagGlobals.setWantActiveNametags(True)
        self.setPosHpr(0, 60, 18, 0, 0, 0)
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
        self.setPosHpr(0, -175, -6.5, 180, 0, 0)
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
        self.setPosHpr(0, -175, -6.5, 180, 0, 0)
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
        for i in xrange(numToons):
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
        for i in xrange(len(toonIds)):
            toon = base.cr.doId2do.get(toonIds[i])
            if toon:
                toon.reparentTo(render)
                pos, h = points[i]
                toon.setPosHpr(battleNode, pos[0], pos[1] + 10, pos[2], h, 0, 0)


    def __doobersToPromotionPosition(self, doobers):
        positions = [
            (-10, 40, 18, 180),
            (10, 40, 18, 180),
            (-20, 40, 18, 180),
            (20, 40, 18, 180),
            (-30, 40, 18, 180),
            (30, 40, 18, 180),
            (-15, 60, 18, 180),
            (15, 60, 18, 180),
            (-25, 60, 18, 180),
            (25, 60, 18, 180),
            (-35, 60, 18, 180),
            (35, 60, 18, 180),
        ]

        for i in xrange(len(doobers)):
            suit = doobers[i]
            suit.fsm.request('neutral')
            suit.loop('neutral')
            #suit.doId = 0
            suit.setPickable(0)
            suit.hideNametag2d()

            x, y, z, h = positions[i]
            suit.wrtReparentTo(render)
            suit.setPosHpr(x, y, z, h, 0, 0)

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
        for i in xrange(numGears):
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