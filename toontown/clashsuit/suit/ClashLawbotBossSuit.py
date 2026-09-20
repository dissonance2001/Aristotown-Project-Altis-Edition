from panda3d.core import *
from direct.fsm import FSM
from direct.interval.IntervalGlobal import *
from direct.task.Task import Task

from toontown.clashsuit.suit import BossCogGlobals
from toontown.clashbattle.battle import MovieUtil
from toontown.clashsuit.suit import ClashSuitBase
from toontown.clashsuit.suit import SuitHealthMeter
from toontown.toonbase import ToontownGlobals, TTLocalizer


class ClashLawbotBossSuit(ClashSuitBase.ClashSuitBase, FSM.FSM):

    def __init__(self, cr):
        try:
            self.DistributedSuit_initialized
            return
        except:
            self.DistributedSuit_initialized = 1

        ClashSuitBase.ClashSuitBase.__init__(self, cr)
        FSM.FSM.__init__(self, 'ClashLawbotBossSuit')
        self.boss = None
        self.newPosition = None
        self.toonPosition = None
        self.flyingSeq = None
        self.suitDamage = 0
        self.suitMaxDamage = 1
        self.healthCondition = 0
        self.destroyTrack = None
        self.isVirtual = 0
        self.isSkelecog = 0
        self.travelTime = -1
        self.travelMovie = None
        self.propellerInterval = None
        self.trapIndex = -1
        self.initialMove = 1
        self.cannonBossState = 'BattleTwo'
        self.isForCutscene = 0

    def generate(self):
        """
        Called when the DistributedObject is reintroduced to the world, either for the first time or from the cache.
        """
        ClashSuitBase.ClashSuitBase.generate(self)

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        ClashSuitBase.ClashSuitBase.announceGenerate(self)
        self.flyingSeq = Sequence(
            ActorInterval(self, 'landing', startFrame=10, endFrame=20, playRate=0.5),
            ActorInterval(self, 'landing', startFrame=20, endFrame=10, playRate=0.5)
        )
        self.flyingSeq.loop()
        self.attachPropeller()
        lastSpinFrame = 8
        fr = self.prop.getFrameRate('propeller')
        spinTime = lastSpinFrame / fr
        self.propellerInterval = ActorInterval(self.prop, 'propeller', constrainedLoop=1, duration=spinTime)
        self.propellerInterval.loop()
        self.hideName()
        self.setPickable(False)
        if not self.getVirtual():
            self.healthBar.updateMeterMode(SuitHealthMeter.MODE_BATTLE)
        if not self.isForCutscene:
            colNode = self.find('**/distAvatarCollNode*')
            colNode.setTag("pieCode", str(ToontownGlobals.PieCodeLawyer))
            colNode.setTag("attackCode", str(BossCogGlobals.BossCogLawyerAttack))
            colName = "HitToon-{}".format(self.getDoId())
            colNode.setName(colName)
            self.accept("enter{}".format(colName), self.doHitToon)
            nearbyBoss = CollisionSphere(0, 0, 0, 5)
            nearbyBoss.setTangible(0)
            nearbyBossNode = CollisionNode('CloseBoss-%s' % self.getDoId())
            nearbyBossNode.setCollideMask(ToontownGlobals.WallBitmask | ToontownGlobals.LawyerNearbyBitmask)
            nearbyBossNode.addSolid(nearbyBoss)
            self.attachNewNode(nearbyBossNode)
            if not self.isVirtual:
                nearBubble = CollisionSphere(0, 0, 0, 50)
            elif self.isVirtual:
                nearBubble = CollisionSphere(0, 0, 0, 38)
            nearBubble.setTangible(0)
            nearBubbleNode = CollisionNode('NearSuit-%s' % self.getDoId())
            nearBubbleNode.setCollideMask(ToontownGlobals.WallBitmask)
            nearBubbleNode.addSolid(nearBubble)
            self.attachNewNode(nearBubbleNode)
            self.accept('enterNearSuit-%s' % self.getDoId(), self.avatarNearEnter)
            self.accept('exitNearSuit-%s' % self.getDoId(), self.avatarNearExit)
        if self.isVirtual:
            self.disableBodyCollisions()
            self.setColorScale(0, 0, 0, 0)
            self.updateHealthBar(self.suitMaxDamage - self.suitDamage, forceUpdate=1)
        if self.isElite:
            self.nametag3d.setColorScale(1, 1, 0, 1)  # gold nametag

    def disable(self):
        self.setState('Off')
        self.boss = None
        ClashSuitBase.ClashSuitBase.disable(self)

    def delete(self):
        try:
            self.DistributedSuit_deleted
            return
        except:
            self.DistributedSuit_deleted = 1

        ClashSuitBase.ClashSuitBase.delete(self)
        self.ignoreAll()
        del self.boss
        del self.newPosition
        del self.toonPosition
        self.flyingSeq.finish()
        del self.flyingSeq

        self.propellerInterval.finish()
        del self.propellerInterval

        try:
            self.destroyTrack.finish()
        except:
            pass
        del self.destroyTrack

        try:
            self.travelMovie.finish()
        except:
            pass
        del self.travelMovie

        del self.suitDamage
        del self.suitMaxDamage
        del self.isVirtual
        del self.isSkelecog
        del self.travelTime
        del self.trapIndex

    def setTravelTime(self, time):
        self.travelTime = float(time)

    def doTravel(self, time, x, y, z):
        self.setTravelTime(time)
        self.newPosition = Point3(x, y, z)
        self.request('Travel')

    def setBossCogId(self, bossCogId):
        self.bossCogId = bossCogId
        self.boss = base.cr.doId2do[bossCogId]

    def makeTravelingTrack(self, toPos):
        travelingTrack = Sequence()
        if self.trapIndex != -1:
            travelingTrack.append(
                Func(base.localAvatar.showHpString, TTLocalizer.LawbotBossLawyerTrapWarning, duration=3, scale=0.5, color=(1, 0.64, 0, 1))
            )
        travelingTrack.append(
            Sequence(
                Func(self.setPos, self.getPos()),
                Func(self.headsUp, toPos),
                self.posInterval(self.travelTime, toPos)
            )
        )
        currState = self.boss.getCurrentOrNextState()
        if currState == "BattleFour" and (self.trapIndex != -1 or Vec3(Vec3(toPos) - Vec3(base.localAvatar.getPos())).length() <= 10): # This determines the "awareness" radius for the visual indicator.
            toPos.setZ(toPos.getZ() + self.height / 2)
            base.localAvatar.doCogCrosshairIndicator(toPos)
        return travelingTrack

    def makeVirtualEnterTrack(self, pos):
        return Sequence(Func(self.setPos, pos), LerpColorScaleInterval(self, self.travelTime, (1, 1, 1, 1)))

    def enterTravel(self):
        if self.travelMovie:
            self.travelMovie.pause()
            self.travelMovie = None
        if self.isVirtual and self.initialMove:
            self.travelMovie = self.makeVirtualEnterTrack(self.newPosition)
        else:
            self.travelMovie = self.makeTravelingTrack(self.newPosition)
        self.initialMove = 0
        self.travelMovie.start()

    def avatarNearEnter(self, entry):
        self.sendUpdate('avatarNearEnter')

    def avatarNearExit(self, entry):
        self.sendUpdate('avatarNearExit')

    def enterDefeated(self):
        if self in self.boss.lawyers:
            self.boss.lawyers.remove(self)
        if self.travelMovie and self.travelMovie.isPlaying():
            self.travelMovie.pause()
        self.travelMovie = None
        self.flyingSeq.finish()
        deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
        gearPoint = Point3(self.getX(), self.getY(), self.getZ() + self.height - 0.2)
        self.destroyTrack = Parallel(
            MovieUtil.createKapowExplosionTrack(render, explosionPoint=gearPoint),
            SoundInterval(deathSound, volume=0.32),
            Func(self.detachNode)
        )
        self.destroyTrack.start()

    def setSuitDamage(self, suitDamage):
        self.showHpText(self.suitDamage - suitDamage)
        self.suitDamage = suitDamage
        self.updateHealthBar(self.suitMaxDamage - self.suitDamage)
        if self.suitDamage == self.suitMaxDamage:
            self.request('Defeated')

    def getSuitDamage(self):
        return self.suitDamage

    def setSuitMaxDamage(self, suitMaxDamage):
        self.suitMaxDamage = suitMaxDamage
        self.updateHealthBar(self.suitMaxDamage - self.suitDamage)

    def getSuitMaxDamage(self):
        return self.suitMaxDamage

    def getHealthPercentage(self):
        try:
            health = (float(self.suitMaxDamage) - float(self.suitDamage)) / float(self.suitMaxDamage)
        except ZeroDivisionError:
            health = 0.96
        return health

    def updateHealthBar(self, hp, forceUpdate = 0):
        if hp > self.suitMaxDamage - self.suitDamage:
            hp = self.suitMaxDamage - self.suitDamage
        health = 1.0 - float(self.suitDamage) / float(self.suitMaxDamage)
        
        self.healthBar.updateHealthBar()

    def removeHealthBar(self):
        if self.healthBar:
            self.healthBar.delete()
            self.healthBar = None

    def setVirtual(self, virtual):
        self.isVirtual = virtual
        if virtual:
            self.makeSkeleton()
            self.makeVirtual(healthColored=1)
            self.updateHealthBar(self.suitMaxDamage - self.suitDamage, forceUpdate=1)

    def getVirtual(self):
        return self.isVirtual

    def setSkeleton(self, skelecog):
        self.isSkelecog = skelecog
        if skelecog:
            self.makeSkeleton()

    def getSkelecog(self):
        return self.isSkelecog

    def doHitToon(self, entry):
        attackCodeStr = entry.getIntoNodePath().getNetTag("attackCode")
        if attackCodeStr == "":
            self.notify.warning("Node {} has no attackCode tag.".format(repr(entry.getIntoNodePath())))
            return
        currState = self.boss.getCurrentOrNextState()
        if currState == self.cannonBossState:
            return
        attackCode = int(attackCodeStr)
        into = entry.getIntoNodePath()
        self.boss.zapLocalToon(attackCode, into)

    def setTrapIndex(self, trapIndex=-1):
        self.trapIndex = trapIndex

    def d_hitSuit(self, taunt=0):
        self.sendUpdate("hitSuit", [taunt])
