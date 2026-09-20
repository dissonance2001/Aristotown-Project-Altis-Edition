from panda3d.core import *
from direct.fsm import FSM
from direct.interval.IntervalGlobal import *
from direct.task.Task import Task

from toontown.clashsuit.suit import BossCogGlobals
from toontown.clashbattle.battle import MovieUtil
from toontown.clashsuit.suit import DistributedSuitBase, SuitHealthMeter
from toontown.toonbase import ToontownGlobals, TTLocalizer


class DistributedLawbotBossDefenseSpecialist(DistributedSuitBase.DistributedSuitBase, FSM.FSM):

    def __init__(self, cr):
        try:
            self.DistributedSuit_initialized
            return
        except:
            self.DistributedSuit_initialized = 1

        DistributedSuitBase.DistributedSuitBase.__init__(self, cr)
        FSM.FSM.__init__(self, 'DistributedLawbotBossSuit')
        self.boss = None
        self.flyingSeq = None
        self.propellerInterval = None
        self.suitDamage = 0
        self.suitMaxDamage = 1
        self.destroyTrack = None

    def generate(self):
        """
        Called when the DistributedObject is reintroduced to the world, either for the first time or from the cache.
        """
        DistributedSuitBase.DistributedSuitBase.generate(self)

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        DistributedSuitBase.DistributedSuitBase.announceGenerate(self)
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
        self.healthBar.updateMeterMode(SuitHealthMeter.MODE_BATTLE)
        colNode = self.find('**/distAvatarCollNode*')
        colNode.setTag("pieCode", str(ToontownGlobals.PieCodeLawyer))
        colNode.setTag("attackCode", str(BossCogGlobals.BossCogLawyerAttack))
        colName = "HitToon-{}".format(self.getDoId())
        colNode.setName(colName)
        self.accept("enter{}".format(colName), self.doHitToon)

    def disable(self):
        self.setState('Off')
        self.boss = None
        DistributedSuitBase.DistributedSuitBase.disable(self)

    def delete(self):
        try:
            self.DistributedSuit_deleted
            return
        except:
            self.DistributedSuit_deleted = 1

        DistributedSuitBase.DistributedSuitBase.delete(self)
        self.ignoreAll()
        del self.boss
        self.flyingSeq.finish()
        del self.flyingSeq

        self.propellerInterval.finish()
        del self.propellerInterval

        try:
            self.destroyTrack.finish()
        except:
            pass
        del self.destroyTrack

        del self.suitDamage
        del self.suitMaxDamage

    def setBossCogId(self, bossCogId):
        self.bossCogId = bossCogId
        self.boss = base.cr.doId2do[bossCogId]

    def enterDefeated(self):
        if self in self.boss.defenseSpecialists:
            self.boss.defenseSpecialists.remove(self)
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
        self.updateHealthBar()
        if self.suitDamage == self.suitMaxDamage:
            self.request('Defeated')

    def getSuitDamage(self):
        return self.suitDamage

    def setSuitMaxDamage(self, suitMaxDamage):
        self.suitMaxDamage = suitMaxDamage
        self.updateHealthBar()

    def getSuitMaxDamage(self):
        return self.suitMaxDamage
        
    def getHealthPercentage(self):
        try:
            health = 1.0 - float(self.suitDamage) / float(self.suitMaxDamage)
        except ZeroDivisionError:
            health = 0.96
        return health

    def updateHealthBar(self, hp=0, forceUpdate=0):
        self.healthBar.updateHealthBar(forceUpdate=forceUpdate)

    def removeHealthBar(self):
        if self.healthBar:
            self.healthBar.delete()
            self.healthBar = None

    def doHitToon(self, entry):
        attackCodeStr = entry.getIntoNodePath().getNetTag("attackCode")
        if attackCodeStr == "":
            self.notify.warning("Node {} has no attackCode tag.".format(repr(entry.getIntoNodePath())))
            return
        attackCode = int(attackCodeStr)
        into = entry.getIntoNodePath()
        self.boss.zapLocalToon(attackCode, into)

    def d_hitSuit(self, taunt=0):
        self.sendUpdate("hitSuit", [taunt])
