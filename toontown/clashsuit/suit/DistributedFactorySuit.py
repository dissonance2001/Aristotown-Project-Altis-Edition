from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.fsm.FSM import FSM
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.suit.DistributedSuitBase import DistributedSuitBase
from direct.task.Task import Task
from toontown.toonbase import ToontownGlobals
from toontown.level import LevelConstants
from toontown.distributed.DelayDeletable import DelayDeletable


@DirectNotifyCategory()
class DistributedFactorySuit(DistributedSuitBase, FSM, DelayDeletable):
    

    defaultTransitions = {
        "Off": ["Walk", "Battle"],
        "Walk": ["WaitForBattle", "Battle"],
        "Battle": ["Walk", "WaitForBattle"],
        "WaitForBattle": ["Battle"],
    }

    def __init__(self, cr):
        try:
            self.DistributedSuit_initialized
            return
        except:
            self.DistributedSuit_initialized = 1
        
        DistributedSuitBase.__init__(self, cr)
        FSM.__init__(self, self.__class__.__name__)
        self.path = None
        self.walkTrack = None
        self.request("Off")
        self.paused = 0
        self.pauseTime = 0
        self.velocity = 3
        self.factoryRequest = None

    def generate(self):
        """
        Called when the DistributedObject is reintroduced to the world, either for the first time or from the cache.
        """
        DistributedSuitBase.generate(self)

    def enterOff(self, *args):
        self.hideNametag3d()
        if not self.subclassManagesParent():
            self.setParent(ToontownGlobals.SPHidden)

    def exitOff(self):
        if not self.subclassManagesParent():
            self.setParent(ToontownGlobals.SPRender)
        self.showNametag3d()
        self.loop('neutral', 0)

    def setLevelDoId(self, levelDoId):
        self.notify.debug('setLevelDoId(%s)' % levelDoId)
        self.levelDoId = levelDoId

    def setCogId(self, cogId):
        self.cogId = cogId

    def setReserve(self, reserve):
        self.reserve = reserve

    def denyBattle(self):
        self.notify.warning('denyBattle()')
        place = self.cr.playGame.getPlace()
        if place.getCurrentOrNextState() == 'WaitForBattle':
            place.setState('walk')

    def doReparent(self):
        self.notify.debug('Suit requesting reparenting')
        if not hasattr(self, 'factory'):
            self.notify.warning('no factory, get Redmond to look at DistributedFactorySuit.announceGenerate()')
        self.factory.requestReparent(self, self.spec['parentEntId'])
        if self.pathEntId:
            self.factory.setEntityCreateCallback(self.pathEntId, self.setPath)
        else:
            self.setPath()

    def setCogSpec(self, spec):
        self.spec = spec
        self.setPos(spec['pos'])
        self.setH(spec['h'])
        self.originalPos = spec['pos']
        self.escapePos = spec['pos']
        self.pathEntId = spec['path']
        self.behavior = spec['behavior']
        self.skeleton = spec['skeleton']
        self.revives = spec.get('revives')
        self.boss = spec['boss']
        if self.reserve:
            self.reparentTo(hidden)
        else:
            self.doReparent()

    def comeOutOfReserve(self):
        self.doReparent()

    def getCogSpec(self, cogId):
        if self.reserve:
            return self.factory.getReserveCogData(cogId)
        else:
            return self.factory.getCogData(cogId)

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        self.notify.debug('announceGenerate %s' % self.doId)

        def onFactoryGenerate(factoryList, self = self):
            self.factory = factoryList[0]

            def onFactoryReady(self = self):
                self.notify.debug('factory ready, read spec')
                spec = self.getCogSpec(self.cogId)
                self.setCogSpec(spec)
                self.factoryRequest = None
                return

            self.factory.setEntityCreateCallback(LevelConstants.LevelMgrEntId, onFactoryReady)

        self.factoryRequest = self.cr.relatedObjectMgr.requestObjects([self.levelDoId], onFactoryGenerate)
        DistributedSuitBase.announceGenerate(self)

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        self.ignoreAll()
        if self.factoryRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.factoryRequest)
            self.factoryRequest = None
        self.notify.debug('DistributedSuit %d: disabling' % self.getDoId())
        self.setState('Off')
        if self.walkTrack:
            del self.walkTrack
            self.walkTrack = None
        DistributedSuitBase.disable(self)

    def delete(self):
        try:
            self.DistributedSuit_deleted
            return
        except:
            self.DistributedSuit_deleted = 1
        
        self.notify.debug('DistributedSuit %d: deleting' % self.getDoId())
        FSM.cleanup(self)
        DistributedSuitBase.delete(self)

    def d_requestBattle(self, pos, hpr):
        self.cr.playGame.getPlace().setState('WaitForBattle')
        self.factory.lockVisibility(zoneNum=self.factory.getEntityZoneEntId(self.spec['parentEntId']))
        self.sendUpdate('requestBattle', [pos[0],
         pos[1],
         pos[2],
         hpr[0],
         hpr[1],
         hpr[2]])

    def handleBattleBlockerCollision(self):
        self.__handleToonCollision(None)

    def __handleToonCollision(self, collEntry):
        if collEntry:
            if collEntry.getFromNodePath().getParent().getKey() != localAvatar.getKey():
                return
        if hasattr(self, 'factory') and hasattr(self.factory, 'lastToonZone'):
            factoryZone = self.factory.lastToonZone
            unitsBelow = self.getPos(render)[2] - base.localAvatar.getPos(render)[2]
            if factoryZone == 24 and unitsBelow > 10.0:
                self.notify.warning('Ignoring toon collision in %d from %f below.' % (factoryZone, unitsBelow))
                return
        if not base.localAvatar.wantBattles:
            return
        toonId = base.localAvatar.getDoId()
        self.notify.debug('Distributed suit %d: requesting a Battle with toon: %d' % (self.doId, toonId))
        self.d_requestBattle(self.getPos(), self.getHpr())
        self.setState('WaitForBattle')

    def setPath(self):
        self.notify.debug('setPath %s' % self.doId)
        if self.pathEntId is not None:
            parent = self.factory.entities.get(self.spec['parentEntId'])
            self.path = self.factory.entities.get(self.pathEntId)
            self.idealPathNode = self.path.attachNewNode('idealPath')
            self.reparentTo(self.idealPathNode)
            self.setPos(0, 0, 0)
            self.path.reparentTo(parent)
            self.walkTrack = self.path.makePathTrack(self.idealPathNode, self.velocity, self.uniqueName('suitWalk'))
        self.setState('Walk')

    def initializeBodyCollisions(self, collIdStr):
        DistributedSuitBase.initializeBodyCollisions(self, collIdStr)
        self.sSphere = CollisionSphere(0.0, 0.0, 0.0, 15)
        name = self.uniqueName('toonSphere')
        self.sSphereNode = CollisionNode(name)
        self.sSphereNode.addSolid(self.sSphere)
        self.sSphereNodePath = self.attachNewNode(self.sSphereNode)
        self.sSphereNodePath.hide()
        self.sSphereBitMask = ToontownGlobals.WallBitmask
        self.sSphereNode.setCollideMask(self.sSphereBitMask)
        self.sSphere.setTangible(0)
        self.accept('enter' + name, self.__handleToonCollision)

    def enableBattleDetect(self, name, handler):
        DistributedSuitBase.enableBattleDetect(self, name, handler)

    def disableBattleDetect(self):
        DistributedSuitBase.disableBattleDetect(self)

    def subclassManagesParent(self):
        return 1

    def enterWalk(self, ts = 0):
        self.enableBattleDetect('walk', self.__handleToonCollision)
        if self.path:
            if self.walkTrack:
                self.walkTrack.loop()
                self.walkTrack.pause()
                if self.paused:
                    self.walkTrack.setT(self.pauseTime)
                else:
                    self.walkTrack.setT(ts)
                self.walkTrack.resume()
            self.loop('walk', 0)
            self.paused = 0
        else:
            self.loop('neutral', 0)

    def exitWalk(self):
        self.disableBattleDetect()
        if self.walkTrack:
            self.pauseTime = self.walkTrack.pause()
            self.paused = 1

    def resumePath(self, state):
        self.setState('Walk')

    def setActive(self, active):
        if active:
            self.setState('Walk')
        else:
            self.setState('Off')

    def disableBattleDetect(self):
        if self.battleDetectName:
            self.ignore('enter' + self.battleDetectName)
            self.battleDetectName = None
        if self.collNodePath:
            self.collNodePath.removeNode()
            self.collNodePath = None
        return

    def disableBodyCollisions(self):
        self.disableBattleDetect()
        self.enableRaycast(0)
        if self.cRayNodePath:
            self.cRayNodePath.removeNode()
        if hasattr(self, 'cRayNode'):
            del self.cRayNode
        if hasattr(self, 'cRay'):
            del self.cRay
        if hasattr(self, 'lifter'):
            del self.lifter

    def removeCollisions(self):
        self.enableRaycast(0)
        self.cRay = None
        self.cRayNode = None
        self.cRayNodePath = None
        self.lifter = None
        self.cTrav = None
        return

    def setVirtual(self, isVirtual = 1):
        self.virtual = isVirtual
        if self.virtual:
            actorNode = self.find('**/__Actor_modelRoot')
            actorCollection = actorNode.findAllMatches('*')
            for thing in actorCollection:
                if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag'):
                    thing.setColorScale(1.0, 0.0, 0.0, 1.0)
                    thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                    thing.setDepthWrite(False)
                    thing.setBin('fixed', 1)

    def getVirtual(self):
        return self.virtual

    def setLeader(self, leader):
        self.leader = leader

    def getLeader(self):
        return self.leader
