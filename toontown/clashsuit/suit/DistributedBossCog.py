from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.distributed.ClockDelta import *
from otp.nametag import NametagGroup
from otp.nametag import NametagGlobals
from toontown.inventory.registry import UniteRegistry
from toontown.toon.OldLaffMeter import OldLaffMeter
from toontown.suit import BossCogGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.avatar import DistributedAvatar
from toontown.avatar import Avatar
from toontown.chat.enums.ChatChannel import ChatChannel
from toontown.chat.enums.ChatContentType import ChatContentType
from toontown.chat.enums.ChatNpcPreset import ChatNpcPreset
from toontown.toonbase import ToontownGlobals
from toontown.battle import BattleGlobals
from toontown.battle import BattleExperience
from toontown.battle import BattleBase
from toontown.suit import BossCog
from toontown.suit import BossHealthBar
from toontown.suit import SuitDNA
from toontown.coghq import CogDisguiseGlobals
from otp import *
from direct.showbase import Transitions
from toontown.hood import ZoneUtil
from toontown.building import ElevatorUtils
from toontown.building import ElevatorConstants
from toontown.distributed import DelayDelete
from toontown.effects import DustCloud
from toontown.toonbase import TTLocalizer
from toontown.friends import FriendsListManager
from direct.controls.ControlManager import CollisionHandlerRayStart
from direct.showbase import PythonUtil
import random
from toontown.chat.constants.ChatGlobals import CFSpeech, CFTimeout


@DirectNotifyCategory()
class DistributedBossCog(DistributedAvatar.DistributedAvatar, BossCog.BossCog):
    allowClickedNameTag = True

    def __init__(self, cr):
        DistributedAvatar.DistributedAvatar.__init__(self, cr)
        BossCog.BossCog.__init__(self)
        self.attackCode = None
        self.gotAllToons = 0
        self.toonsA = []
        self.toonsB = []
        self.involvedToons = []
        self.toonRequest = None
        self.battleNumber = 0
        self.battleAId = None
        self.battleBId = None
        self.battleA = None
        self.battleB = None
        self.battleRequest = None
        self.arenaSide = 0
        self.toonSphere = None
        self.localToonIsSafe = 0
        self.__toonsStuckToFloor = []
        self.lastZapLocalTime = 0
        self.attackThreshold = 1.0
        self.TYPE_HURT = 0
        self.TYPE_ATTACK = 1
        self.battleANode = self.attachNewNode('battleA')
        self.battleBNode = self.attachNewNode('battleB')
        self.battleANode.setPosHpr(*BossCogGlobals.BossCogBattleAPosHpr)
        self.battleBNode.setPosHpr(*BossCogGlobals.BossCogBattleBPosHpr)
        self.activeIntervals = {}
        self.flashInterval = None
        self.elevatorType = ElevatorConstants.ELEVATOR_VP
        self.currentToonTotal = 0
        self.finalBattleState = 'BattleThree'
        self.dizzyMusicPlaying = False
        self.uniteRewardId = []
        self.bonusUnites = {}
        self.localUniteEffectPageNumber = 0

    def announceGenerate(self):
        DistributedAvatar.DistributedAvatar.announceGenerate(self)
        self.healthGui = BossHealthBar.BossHealthBar(self.style.dept, 1, 1)
        self.healthGui.load()
        self.healthGui.hide()
        self.prevCogSuitLevel = localAvatar.getCogLevels()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
        self.prevCogSuitType = localAvatar.getCogTypes()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
        self.prevCogSuitReviveLevel = localAvatar.getCogReviveLevels()[CogDisguiseGlobals.dept2deptIndex(self.style.dept)]
        nearBubble = CollisionSphere(0, 0, 0, 50)
        nearBubble.setTangible(0)
        nearBubbleNode = CollisionNode('NearBoss')
        nearBubbleNode.setCollideMask(ToontownGlobals.WallBitmask)
        nearBubbleNode.addSolid(nearBubble)
        self.attachNewNode(nearBubbleNode)
        self.accept('enterNearBoss', self.avatarNearEnter)
        self.accept('exitNearBoss', self.avatarNearExit)
        self.setupCollisions()
        self.setTag('attackCode', str(BossCogGlobals.BossCogElectricFence))
        self.accept('enterBossZap', self.__touchedBoss)
        bubbleL = CollisionSphere(10, -5, 0, 10)
        bubbleL.setTangible(0)
        bubbleLNode = CollisionNode('BossZap')
        bubbleLNode.setCollideMask(ToontownGlobals.WallBitmask)
        bubbleLNode.addSolid(bubbleL)
        self.bubbleL = self.axle.attachNewNode(bubbleLNode)
        self.bubbleL.setTag('attackCode', str(BossCogGlobals.BossCogSwatLeft))
        self.bubbleL.stash()
        bubbleR = CollisionSphere(-10, -5, 0, 10)
        bubbleR.setTangible(0)
        bubbleRNode = CollisionNode('BossZap')
        bubbleRNode.setCollideMask(ToontownGlobals.WallBitmask)
        bubbleRNode.addSolid(bubbleR)
        self.bubbleR = self.axle.attachNewNode(bubbleRNode)
        self.bubbleR.setTag('attackCode', str(BossCogGlobals.BossCogSwatRight))
        self.bubbleR.stash()
        if self.style.dept == 'l':
            atkCStr = BossCogGlobals.BossCogPaperFrontAttack
            bubbleB = CollisionSphere(0, 20, 0, 10)
            bubbleF = CollisionSphere(0, -20, 0, 10)
            bubbleFL = CollisionSphere(-20, 0, 0, 10)
            bubbleFR = CollisionSphere(20, 0, 0, 10)
        else:
            atkCStr = BossCogGlobals.BossCogFrontAttack
            bubbleB = CollisionSphere(0, 25, 0, 12)
            bubbleF = CollisionSphere(0, -25, 0, 12)
            bubbleFL = CollisionSphere(-25, 0, 0, 12)
            bubbleFR = CollisionSphere(25, 0, 0, 12)
        bubbleB.setTangible(0)
        bubbleBNode = CollisionNode('BossZap')
        bubbleBNode.setCollideMask(ToontownGlobals.WallBitmask)
        bubbleBNode.addSolid(bubbleB)
        self.bubbleB = self.rotateNode.attachNewNode(bubbleBNode)
        self.bubbleB.setTag('attackCode', str(atkCStr))
        self.bubbleB.stash()
        bubbleF.setTangible(0)
        bubbleFNode = CollisionNode('BossZap')
        bubbleFNode.setCollideMask(ToontownGlobals.WallBitmask)
        bubbleFNode.addSolid(bubbleF)
        self.bubbleF = self.rotateNode.attachNewNode(bubbleFNode)
        self.bubbleF.setTag('attackCode', str(atkCStr))
        self.bubbleF.stash()
        bubbleFL.setTangible(0)
        bubbleFLNode = CollisionNode('BossZap')
        bubbleFLNode.setCollideMask(ToontownGlobals.WallBitmask)
        bubbleFLNode.addSolid(bubbleFL)
        self.bubbleFL = self.rotateNode.attachNewNode(bubbleFLNode)
        self.bubbleFL.setTag('attackCode', str(atkCStr))
        self.bubbleFL.stash()
        bubbleFR.setTangible(0)
        bubbleFRNode = CollisionNode('BossZap')
        bubbleFRNode.setCollideMask(ToontownGlobals.WallBitmask)
        bubbleFRNode.addSolid(bubbleFR)
        self.bubbleFR = self.rotateNode.attachNewNode(bubbleFRNode)
        self.bubbleFR.setTag('attackCode', str(atkCStr))
        self.bubbleFR.stash()

    def setupCollisions(self):
        self.collNode.removeSolid(0)
        capsule1 = CollisionCapsule(6.5, -7.5, 2, 6.5, 7.5, 2, 2.5)
        capsule2 = CollisionCapsule(-6.5, -7.5, 2, -6.5, 7.5, 2, 2.5)
        roof = CollisionPolygon(Point3(-4.4, 7.1, 5.5), Point3(-4.4, -7.1, 5.5), Point3(4.4, -7.1, 5.5), Point3(4.4, 7.1, 5.5))
        side1 = CollisionPolygon(Point3(-4.4, -7.1, 5.5), Point3(-4.4, 7.1, 5.5), Point3(-4.4, 7.1, 0), Point3(-4.4, -7.1, 0))
        side2 = CollisionPolygon(Point3(4.4, 7.1, 5.5), Point3(4.4, -7.1, 5.5), Point3(4.4, -7.1, 0), Point3(4.4, 7.1, 0))
        front1 = CollisionPolygon(Point3(4.4, -7.1, 5.5), Point3(-4.4, -7.1, 5.5), Point3(-4.4, -7.1, 5.2), Point3(4.4, -7.1, 5.2))
        back1 = CollisionPolygon(Point3(-4.4, 7.1, 5.5), Point3(4.4, 7.1, 5.5), Point3(4.4, 7.1, 5.2), Point3(-4.4, 7.1, 5.2))
        self.collNode.addSolid(capsule1)
        self.collNode.addSolid(capsule2)
        self.collNode.addSolid(roof)
        self.collNode.addSolid(side1)
        self.collNode.addSolid(side2)
        self.collNode.addSolid(front1)
        self.collNode.addSolid(back1)
        self.collNodePath.reparentTo(self.axle)
        self.collNode.setCollideMask(ToontownGlobals.PieBitmask | ToontownGlobals.WallBitmask | ToontownGlobals.CameraBitmask)
        self.collNode.setName('BossZap')

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        DistributedAvatar.DistributedAvatar.disable(self)
        self.battleAId = None
        self.battleBId = None
        self.battleA = None
        self.battleB = None
        if self.healthGui:
            self.healthGui.destroy()
            self.healthGui = None
        self.cr.relatedObjectMgr.abortRequest(self.toonRequest)
        self.toonRequest = None
        self.cr.relatedObjectMgr.abortRequest(self.battleRequest)
        self.battleRequest = None
        self.stopAnimate()
        self.cleanupIntervals()
        self.cleanupFlash()
        self.disableLocalToonSimpleCollisions()
        self.ignoreAll()

    def delete(self):
        try:
            self.DistributedBossCog_deleted
            return
        except Exception:
            self.DistributedBossCog_deleted = 1

        self.ignoreAll()
        self.cleanupIntervals()
        DistributedAvatar.DistributedAvatar.delete(self)
        BossCog.BossCog.delete(self)

    def uniqueName(self, idString):
        return DistributedAvatar.DistributedAvatar.uniqueName(self, idString)

    def setDNAString(self, dnaString):
        BossCog.BossCog.setDNAString(self, dnaString)

    def getDNAString(self):
        return self.dna.makeNetString()

    def setDNA(self, dna):
        BossCog.BossCog.setDNA(self, dna)

    def setToonIds(self, involvedToons, toonsA, toonsB):
        self.involvedToons = involvedToons
        self.toonsA = toonsA
        self.toonsB = toonsB
        self.cr.relatedObjectMgr.abortRequest(self.toonRequest)
        self.gotAllToons = 0
        self.toonRequest = self.cr.relatedObjectMgr.requestObjects(self.involvedToons, allCallback=self.__gotAllToons, eachCallback=self.gotToon)

    def getDialogueArray(self, *args):
        return BossCog.BossCog.getDialogueArray(self, *args)
    
    def acceptIntervals(self) -> None:
        self.accept("boss_storeInterval", self.storeInterval)
        self.accept("boss_clearInterval", self.clearInterval)

    def storeInterval(self, interval, name):
        if name in self.activeIntervals:
            ival = self.activeIntervals[name]
            if hasattr(ival, 'delayDelete') or hasattr(ival, 'delayDeletes'):
                self.clearInterval(name, finish=1)
        self.activeIntervals[name] = interval

    def cleanupIntervals(self):
        for interval in list(self.activeIntervals.values()):
            interval.finish()
            DelayDelete.cleanupDelayDeletes(interval)

        self.activeIntervals = {}

    def clearInterval(self, name, finish = 1):
        if name in self.activeIntervals:
            ival = self.activeIntervals[name]
            if finish:
                ival.finish()
            else:
                ival.pause()
            if name in self.activeIntervals:
                DelayDelete.cleanupDelayDeletes(ival)
                del self.activeIntervals[name]
        else:
            self.notify.debug('interval: %s already cleared' % name)

    def finishInterval(self, name):
        if name in self.activeIntervals:
            interval = self.activeIntervals[name]
            interval.finish()

    def d_avatarEnter(self):
        self.sendUpdate('avatarEnter', [])

    def d_avatarExit(self):
        self.sendUpdate('avatarExit', [])

    def avatarNearEnter(self, entry):
        self.sendUpdate('avatarNearEnter', [])

    def avatarNearExit(self, entry):
        self.sendUpdate('avatarNearExit', [])

    def setBossChatFromIndex(self, index, type, attackCode=0, avId=0):
        if type == self.TYPE_HURT:
            choices = TTLocalizer.BossCogHurtPhrases.get(self.dna.dept, None)
        elif type == self.TYPE_ATTACK:
            choices = TTLocalizer.BossCogTauntPhrases.get(self.dna.dept, None)
            choices = choices.get(attackCode, None)
        if choices is not None:
            choice = choices[index]
            if avId != 0:
                toon = base.cr.doId2do.get(avId)
                if toon:
                    choice = choice.format(toon.getName())
                    self.setChatAbsolute(choice, CFSpeech | CFTimeout)
            else:
                self.setChatAbsolute(choice, CFSpeech | CFTimeout)

    def hasLocalToon(self):
        doId = localAvatar.doId
        return doId in self.toonsA or doId in self.toonsB

    def setBattleExperience(self, toonBattleExp, updatedQuests):
        self.toonRewardDicts = BattleExperience.genRewardDicts(toonBattleExp)
        self.toonRewardIds = [exp[0] for exp in toonBattleExp]
        self.updatedQuests = dict(updatedQuests)

    def setArenaSide(self, arenaSide):
        self.arenaSide = arenaSide

    def setState(self, state):
        self.request(state)

    def gotToon(self, toon):
        pass

    def __gotAllToons(self, toons):
        self.gotAllToons = 1
        messenger.send('gotAllToons')

    def setBattleIds(self, battleNumber, battleAId, battleBId):
        self.battleNumber = battleNumber
        self.battleAId = battleAId
        self.battleBId = battleBId
        self.cr.relatedObjectMgr.abortRequest(self.battleRequest)
        self.battleRequest = self.cr.relatedObjectMgr.requestObjects([self.battleAId, self.battleBId], allCallback=self.__gotBattles)

    def __gotBattles(self, battles):
        self.battleRequest = None
        if self.battleA and self.battleA != battles[0]:
            self.battleA.cleanupBattle()
        if self.battleB and self.battleB != battles[1]:
            self.battleB.cleanupBattle()
        self.battleA = battles[0]
        self.battleB = battles[1]

    def cleanupBattles(self):
        if self.battleA:
            self.battleA.cleanupBattle()
        if self.battleB:
            self.battleB.cleanupBattle()

    def makeEndOfBattleMovie(self, hasLocalToon):
        return Sequence()

    def controlToons(self):
        for panel in self.cr.openAvatarPanels.copy():
            if panel:
                panel.cleanupDialog()

        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                toon.stopLookAround()
                toon.stopSmooth()

        if self.hasLocalToon():
            self.toMovieMode()

    def enableLocalToonSimpleCollisions(self):
        if not self.toonSphere:
            sphere = CollisionSphere(0, 0, 1, 1)
            sphere.setRespectEffectiveNormal(0)
            sphereNode = CollisionNode('SimpleCollisions')
            sphereNode.setFromCollideMask(ToontownGlobals.WallBitmask | ToontownGlobals.FloorBitmask)
            sphereNode.setIntoCollideMask(BitMask32.allOff())
            sphereNode.addSolid(sphere)
            self.toonSphere = NodePath(sphereNode)
            self.toonSphereHandler = CollisionHandlerPusher()
            self.toonSphereHandler.addCollider(self.toonSphere, localAvatar)
        self.toonSphere.reparentTo(localAvatar)
        base.cTrav.addCollider(self.toonSphere, self.toonSphereHandler)

    def disableLocalToonSimpleCollisions(self):
        if self.toonSphere:
            base.cTrav.removeCollider(self.toonSphere)
            self.toonSphere.detachNode()

    def toOuchMode(self):
        if self.cr:
            place = self.cr.playGame.getPlace()
            if place:
                place.setState('Ouch')

    def toCraneMode(self):
        if self.cr:
            place = self.cr.playGame.getPlace()
            if place:
                place.setState('Crane')

    def toMovieMode(self):
        if self.cr:
            place = self.cr.playGame.getPlace()
            if place:
                place.setState('Movie')

    def toWalkMode(self):
        if self.cr:
            place = self.cr.playGame.getPlace()
            if place:
                place.setState('Walk')

    def toFinalBattleMode(self):
        if self.cr:
            place = self.cr.playGame.getPlace()
            if place:
                place.setState('FinalBattle')

    def releaseToons(self, finalBattle = 0):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                if self.battleA and toon in self.battleA.toons and not finalBattle:
                    pass
                elif self.battleB and toon in self.battleB.toons and not finalBattle:
                    pass
                else:
                    toon.startLookAround()
                    toon.startSmooth()
                    toon.wrtReparentTo(render)
                    if toon == localAvatar:
                        if finalBattle:
                            self.toFinalBattleMode()
                        else:
                            self.toWalkMode()

    def getToonCount(self):
        count = 0
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                count += 1
        return count

    def stickToonsToFloor(self):
        self.unstickToons()
        rayNode = CollisionNode('stickToonsToFloor')
        rayNode.addSolid(CollisionRay(0.0, 0.0, CollisionHandlerRayStart, 0.0, 0.0, -1.0))
        rayNode.setFromCollideMask(ToontownGlobals.FloorBitmask)
        rayNode.setIntoCollideMask(BitMask32.allOff())
        ray = NodePath(rayNode)
        lifter = CollisionHandlerFloor()
        lifter.setOffset(ToontownGlobals.FloorOffset)
        lifter.setReach(10.0)
        for toonId in self.involvedToons:
            toon = base.cr.doId2do.get(toonId)
            if toon:
                toonRay = ray.instanceTo(toon)
                lifter.addCollider(toonRay, toon)
                base.cTrav.addCollider(toonRay, lifter)
                self.__toonsStuckToFloor.append(toonRay)

    def unstickToons(self):
        for toonRay in self.__toonsStuckToFloor:
            base.cTrav.removeCollider(toonRay)
            toonRay.removeNode()

        self.__toonsStuckToFloor = []

    @property
    def dizzyMusic(self):
        return self.battleThreeMusic

    @property
    def unDizzyMusic(self):
        return self.battleThreeMusic

    def setDizzy(self, dizzy):
        super().setDizzy(dizzy)
        if self.state != self.finalBattleState:
            return

        # Update our music to become the dizzy/non-dizzy variant if we need to
        if dizzy and not self.dizzyMusicPlaying:
            base.musicMgr.crossfadeIntoMusic(self.preloadedFinalBattleDizzyMusic, duration=0.3, delay=0, looping=1, matchTime=True, volume=0.9, musicCode=self.dizzyMusic)
            self.dizzyMusicPlaying = True
        elif (not dizzy) and self.dizzyMusicPlaying:
            base.musicMgr.crossfadeIntoMusic(self.preloadedFinalBattleMusic, duration=0.3, delay=0, looping=1, matchTime=True, volume=0.9, musicCode=self.unDizzyMusic)
            self.dizzyMusicPlaying = False

    def setupElevator(self, elevatorModel):
        self.elevatorModel = elevatorModel
        self.leftDoor = self.elevatorModel.find('**/left-door')
        if self.leftDoor.isEmpty():
            self.leftDoor = self.elevatorModel.find('**/left_door')
        self.rightDoor = self.elevatorModel.find('**/right-door')
        if self.rightDoor.isEmpty():
            self.rightDoor = self.elevatorModel.find('**/right_door')
        self.openSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_sliding.ogg')
        self.finalOpenSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_final.ogg')
        self.closeSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_sliding.ogg')
        self.finalCloseSfx = base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_door_open_final.ogg')
        self.openDoors = ElevatorUtils.getOpenInterval(self, self.leftDoor, self.rightDoor, self.openSfx, self.finalOpenSfx, self.elevatorType)
        self.closeDoors = ElevatorUtils.getCloseInterval(self, self.leftDoor, self.rightDoor, self.closeSfx, self.finalCloseSfx, self.elevatorType)
        self.closeDoors.start()
        self.closeDoors.finish()

    def putToonInCogSuit(self, toon):
        if not toon.isDisguised:
            deptIndex = SuitDNA.suitDepts.index(self.style.dept)
            toon.setCogIndex(deptIndex)
        toon.getGeomNode().hide()

    def placeToonInElevator(self, toon):
        self.putToonInCogSuit(toon)
        toonIndex = self.involvedToons.index(toon.doId)
        toon.reparentTo(self.elevatorModel)
        toon.setPos(*ElevatorConstants.BigElevatorPoints[toonIndex])
        toon.setHpr(180, 0, 0)
        toon.suit.loop('neutral')

    def toonNormalEyes(self, toons, bArrayOfObjs = False):
        if bArrayOfObjs:
            toonObjs = toons
        else:
            toonObjs = []
            for toonId in toons:
                toon = base.cr.doId2do.get(toonId)
                if toon:
                    toonObjs.append(toon)

        seq = Sequence()
        for toon in toonObjs:
            seq.append(Func(toon.normalEyes))
            seq.append(Func(toon.blinkEyes))

        return seq

    def toonRemoved(self, avid):
        if not hasattr(self, 'currentToonTotal') or not hasattr(self, 'startToonTotal'):
            return
        self.currentToonTotal -= 1
        base.discord.updateParty(self.currentToonTotal, self.startToonTotal)

    def toonDied(self, avId):
        if avId == localAvatar.doId:
            self.localToonDied()

    def localToonToSafeZone(self):
        self.showToonsMeters()
        target_sz = ZoneUtil.getSafeZoneId(localAvatar.defaultZone)
        place = self.cr.playGame.getPlace()

        shardId = None
        if getattr(base.cr, 'districtMgr', None):
            shardId = base.cr.districtMgr.getDrainTarget(checkDelayDeletes=True)

        place.request('TeleportOut', {'loader': ZoneUtil.getLoaderName(target_sz),
          'where': ZoneUtil.getWhereName(target_sz, 1),
          'how': 'TeleportIn',
          'hoodId': target_sz,
          'zoneId': target_sz,
          'shardId': shardId,
          'avId': -1})

    def localToonDied(self):
        target_sz = ZoneUtil.getSafeZoneId(localAvatar.defaultZone)
        place = self.cr.playGame.getPlace()
        shardId = None
        if getattr(base.cr, 'districtMgr', None):
            shardId = base.cr.districtMgr.getDrainTarget(checkDelayDeletes=True)

        place.request('Died', {'loader': ZoneUtil.getLoaderName(target_sz),
          'where': ZoneUtil.getWhereName(target_sz, 1),
          'how': 'TeleportIn',
          'hoodId': target_sz,
          'zoneId': target_sz,
          'shardId': shardId,
          'avId': -1,
          'battle': 1})

    def toonsToBattlePosition(self, toonIds, battleNode):
        points = BattleBase.BattleBase.toonPoints[len(toonIds) - 1]
        self.notify.debug('toonsToBattlePosition: points = %s' % points[0][0])
        for i in range(len(toonIds)):
            toon = base.cr.doId2do.get(toonIds[i])
            if toon:
                toon.reparentTo(render)
                pos, h = points[i]
                self.notify.debug('toonsToBattlePosition: battleNode=%s %.2f %.2f %.2f %.2f %.2f %.2f' % (battleNode,
                 pos[0],
                 pos[1],
                 pos[2],
                 h,
                 0,
                 0))
                self.notify.debug('old toon pos %s' % toon.getPos())
                self.notify.debug('pos=%.2f %.2f %.2f h=%.2f' % (pos[0],
                 pos[1],
                 pos[2],
                 h))
                self.notify.debug('battleNode.pos = %s' % battleNode.getPos())
                self.notify.debug('battleNode.hpr = %s' % battleNode.getHpr())
                toon.setPosHpr(battleNode, pos[0], pos[1], pos[2], h, 0, 0)
                self.notify.debug('new toon pos %s ' % toon.getPos())

    def __touchedBoss(self, entry):
        self.notify.debug('%s' % entry)
        self.notify.debug('fromPos = %s' % entry.getFromNodePath().getPos(render))
        self.notify.debug('intoPos = %s' % entry.getIntoNodePath().getPos(render))
        attackCodeStr = entry.getIntoNodePath().getNetTag('attackCode')
        if attackCodeStr == '':
            self.notify.warning('Node %s has no attackCode tag.' % repr(entry.getIntoNodePath()))
            return

        attackCode = int(attackCodeStr)
        self.zapLocalToon(attackCode)

    def zapLocalToon(self, attackCode, origin = None):
        if self.localToonIsSafe or localAvatar.ghostMode or localAvatar.isStunned:
            return
        if (self.attackCode in BossCogGlobals.BossCogDizzyStates) and (attackCode not in BossCogGlobals.NonBossCogAttacks):
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

    def showZapToon(self, toonId, x, y, z, h, p, r, attackCode, timestamp):
        if toonId == localAvatar.doId:
            return
        ts = globalClockDelta.localElapsedTime(timestamp)
        pos = Point3(x, y, z)
        hpr = VBase3(h, p, r)
        fling = 1
        toon = self.cr.doId2do.get(toonId)
        if toon:
            if attackCode == BossCogGlobals.BossCogAreaAttack:
                pos = None
                hpr = None
                fling = 0
            else:
                ts -= toon.smoother.getDelay()

            self.doZapToon(toon, pos=pos, hpr=hpr, ts=ts, fling=fling)

    def doZapToon(self, toon, pos = None, hpr = None, ts = 0, fling = 1, shake = 1):
        zapName = toon.uniqueName('zap')
        self.clearInterval(zapName)
        zapTrack = Sequence(name=zapName)
        if toon is localAvatar:
            self.toOuchMode()
            localAvatar.stunToon()
            messenger.send('interrupt-pie')
            messenger.send('interrupt-sound')
            self.enableLocalToonSimpleCollisions()
        else:
            zapTrack.append(Func(toon.stopSmooth))

        def getSlideToPos(toon = toon):
            return render.getRelativePoint(toon, Point3(0, -5, 0))

        if pos is not None and hpr is not None:
            (zapTrack.append(Func(toon.setPosHpr, pos, hpr)),)
        toonTrack = Parallel()
        if shake and toon is localAvatar:
            toonTrack.append(Sequence(Func(camera.setZ, camera, 1), Wait(0.15), Func(camera.setZ, camera, -2), Wait(0.15), Func(camera.setZ, camera, 1)))
        if fling:
            toonTrack += [ActorInterval(toon, 'slip-backward'), toon.posInterval(0.5, getSlideToPos, fluid=1)]
        else:
            toonTrack += [ActorInterval(toon, 'slip-forward')]
        zapTrack.append(toonTrack)
        if toon is localAvatar:
            zapTrack.append(Func(self.disableLocalToonSimpleCollisions))
            currentState = self.state
            if currentState == self.finalBattleState:
                zapTrack.append(Func(self.toFinalBattleMode))
            else:
                zapTrack.append(Func(self.toWalkMode))
        else:
            zapTrack.append(Func(toon.startSmooth))
        if ts > 0:
            startTime = ts
        else:
            zapTrack = Sequence(Wait(-ts), zapTrack)
            startTime = 0
        zapTrack.append(Func(self.clearInterval, zapName))
        zapTrack.delayDelete = DelayDelete.DelayDelete(toon, 'BossCog.doZapToon')
        zapTrack.start(startTime)
        self.storeInterval(zapTrack, zapName)

    def setAttackCode(self, attackCode, avId = 0):
        self.attackCode = attackCode
        self.attackAvId = avId
        if attackCode == BossCogGlobals.BossCogDizzy:
            self.setDizzy(1)
            self.cleanupAttacks()
            self.doAnimate(None, raised=0, happy=1)
        elif attackCode == BossCogGlobals.BossCogDizzyNow:
            self.setDizzy(1)
            self.cleanupAttacks()
            self.doAnimate('hit', happy=1, now=1)
        elif attackCode == BossCogGlobals.BossCogSwatLeft:
            self.setDizzy(0)
            self.doAnimate('ltSwing', now=1)
        elif attackCode == BossCogGlobals.BossCogSwatRight:
            self.setDizzy(0)
            self.doAnimate('rtSwing', now=1)
        elif attackCode == BossCogGlobals.BossCogAreaAttack:
            self.setDizzy(0)
            self.doAnimate('areaAttack', now=1)
        elif attackCode == BossCogGlobals.BossCogFrontAttack:
            self.setDizzy(0)
            self.doAnimate('frontAttack', now=1)
        elif attackCode == BossCogGlobals.BossCogRecoverDizzyAttack:
            self.setDizzy(0)
            self.doAnimate('frontAttack', now=1)
        elif attackCode in (BossCogGlobals.BossCogDirectedAttack, BossCogGlobals.BossCogSlowDirectedAttack, BossCogGlobals.BossCogSlowCoinDirectedAttack):
            self.setDizzy(0)
            self.doDirectedAttack(avId, attackCode)
        elif attackCode == BossCogGlobals.BossCogNoAttack:
            self.setDizzy(0)
            self.doAnimate(None, raised=1)

    def cleanupAttacks(self):
        pass

    def cleanupFlash(self):
        if self.flashInterval:
            self.flashInterval.finish()
            self.flashInterval = None

    def flashRed(self):
        self.cleanupFlash()
        self.setColorScale(1, 1, 1, 1)
        i = Sequence(self.colorScaleInterval(0.1, colorScale=VBase4(1, 0, 0, 1)), self.colorScaleInterval(0.3, colorScale=VBase4(1, 1, 1, 1)))
        self.flashInterval = i
        i.start()

    def flashGreen(self):
        self.cleanupFlash()
        if not self.isEmpty():
            self.setColorScale(1, 1, 1, 1)
            i = Sequence(self.colorScaleInterval(0.1, colorScale=VBase4(0, 1, 0, 1)), self.colorScaleInterval(0.3, colorScale=VBase4(1, 1, 1, 1)))
            self.flashInterval = i
            i.start()

    def getGearFrisbee(self):
        return loader.loadModel('phase_9/models/char/gearProp')

    def getBookFrisbee(self):
        model = loader.loadModel('phase_5/models/props/lawbook')
        cBox = CollisionBox(0, 0.5, 0.5, 0.25)
        cBox.setTangible(0)
        cn = CollisionNode('BossZap')
        cn.addSolid(cBox)
        cn.setCollideMask(ToontownGlobals.WallBitmask)
        model.attachNewNode(cn)
        return model

    def getCoinFrisbee(self):
        holderNode = NodePath('coin-holder')
        model = loader.loadModel('phase_3.5/models/props/cc_m_prp_gen_coin_gold')
        model.setP(90)
        model.reparentTo(holderNode)
        cBox = CollisionBox(0, 0.4, 0.4, 0.2)
        cBox.setTangible(0)
        cn = CollisionNode('BossZap')
        cn.addSolid(cBox)
        cn.setCollideMask(ToontownGlobals.WallBitmask)
        holderNode.attachNewNode(cn)
        return holderNode

    def backupToonsToBattlePosition(self, toonIds, battleNode):
        self.notify.debug('backupToonsToBattlePosition:')
        ival = Parallel()
        points = BattleBase.BattleBase.toonPoints[len(toonIds) - 1]
        for i in range(len(toonIds)):
            toon = base.cr.doId2do.get(toonIds[i])
            if toon:
                pos, h = points[i]
                pos = render.getRelativePoint(battleNode, pos)
                ival.append(Sequence(Func(toon.setPlayRate, -0.8, 'walk'), Func(toon.loop, 'walk'), toon.posInterval(3, pos), Func(toon.setPlayRate, 1, 'walk'), Func(toon.loop, 'neutral')))

        return ival

    def loseCogSuits(self, toons, battleNode, camLoc, arrayOfObjs = False):
        seq = Sequence()
        if not toons:
            return seq
        self.notify.debug('battleNode=%s camLoc=%s' % (battleNode, camLoc))
        seq.append(base.camera.posHprInterval(1, Point3(camLoc[0], camLoc[1], camLoc[2]), Point3(camLoc[3], camLoc[4], camLoc[5]), other = battleNode, blendType = 'easeInOut'))
        suitsOff = Parallel()
        if arrayOfObjs:
            toonArray = toons
        else:
            toonArray = []
            for toonId in toons:
                toon = base.cr.doId2do.get(toonId)
                if toon:
                    toonArray.append(toon)

        for toon in toonArray:
            dustCloud = DustCloud.DustCloud()
            dustCloud.setPos(0, 2, 3)
            dustCloud.setScale(0.5)
            dustCloud.setDepthWrite(0)
            dustCloud.setBin('fixed', 0)
            dustCloud.createTrack()
            suitsOff.append(Sequence(Func(dustCloud.reparentTo, toon), Parallel(dustCloud.track, Sequence(Wait(0.3), Func(toon.takeOffSuit), Func(toon.sadEyes), Func(toon.blinkEyes), Func(toon.play, 'slip-backward'), Wait(0.7))), Func(dustCloud.detachNode), Func(toon.normalEyes), Func(dustCloud.destroy)))
        snd = loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cfg_propellerBreaks.ogg')
        seq.append(Func(snd.play))
        seq.append(suitsOff)
        return seq

    def doDirectedAttack(self, avId, attackCode):
        toon = base.cr.doId2do.get(avId)
        if toon:
            gearRoot = self.rotateNode.attachNewNode('gearRoot')
            gearRoot.setZ(10)
            gearRoot.setTag('attackCode', str(attackCode))
            if attackCode in (BossCogGlobals.BossCogBookDirectedAttack,
                              BossCogGlobals.BossCogSpreadBookDirectedAttack):
                gearModel = self.getBookFrisbee()
                gearModel.setScale(3.0)
            elif attackCode == BossCogGlobals.BossCogSlowCoinDirectedAttack:
                gearModel = self.getCoinFrisbee()
                gearModel.setScale(3.5)
            else:
                gearModel = self.getGearFrisbee()
                gearModel.setScale(0.2)
            gearRoot.headsUp(toon)
            toToonH = PythonUtil.fitDestAngle2Src(0, gearRoot.getH() + 180)
            gearRoot.lookAt(toon)
            neutral = 'Fb_neutral'
            if not self.twoFaced:
                neutral = 'Ff_neutral'
            gearTrack = Parallel()
            timesToDo = 3 if attackCode == BossCogGlobals.BossCogSpreadBookDirectedAttack else 1
            xRanges = [0, -10, 10]
            for i in range(timesToDo):
                for j in range(4):
                    node = gearRoot.attachNewNode(str(i))
                    node.hide()
                    node.setPos(0, 5.85, 4.0)
                    gearModel.instanceTo(node)
                    x = xRanges[i] + random.uniform(-5, 5)
                    z = random.uniform(-3, 3)
                    mult = 1
                    if self.dna.dept == 'l':
                        mult = 2
                    h = random.uniform(-720, 720)
                    gearTrack.append(Sequence(Wait(j * 0.15), Func(node.show), Parallel(node.posInterval(1, Point3(x, 50, z), fluid=1), node.hprInterval(1, VBase3(h*mult, 0, 0), fluid=1)), Func(node.detachNode)))
            gearTrack = Sequence(gearTrack)
            if not self.raised:
                neutral1Anim = self.getAnim('down2Up')
                self.raised = 1
            else:
                neutral1Anim = ActorInterval(self, neutral, startFrame=48)
            throwAnim = self.getAnim('throw')
            neutral2Anim = ActorInterval(self, neutral)
            extraAnim = Sequence()
            if attackCode in (BossCogGlobals.BossCogSlowDirectedAttack, BossCogGlobals.BossCogSlowCoinDirectedAttack):
                extraAnim = ActorInterval(self, neutral)
            seq = Sequence(ParallelEndTogether(self.pelvis.hprInterval(1, VBase3(toToonH, 0, 0)), neutral1Anim), extraAnim, Parallel(Sequence(Wait(0.19), gearTrack, Func(gearRoot.detachNode), self.pelvis.hprInterval(0.2, VBase3(0, 0, 0))), Sequence(throwAnim, neutral2Anim)))
            self.doAnimate(seq, now=1, raised=1)

    def announceAreaAttack(self):
        if not getattr(localAvatar.controlManager.currentControls, 'isAirborne', 0):
            self.zapLocalToon(BossCogGlobals.BossCogAreaAttack)

    def loadEnvironment(self):
        self.elevatorMusic = 'vp_elevator'
        self.stingMusic = 'vp_cage_toon_skelecogs'
        self.battleOneMusic = 'vp_battle_one'
        self.battleTwoMusic = 'vp_battle_two'
        self.battleThreeMusic = 'vp_battle_three'
        self.victoryMusic = 'vp_victory'
        self.epilogueMusic = 'vp_epilogue'

        self.acceptIntervals()

    def preloadFinalBattleMusic(self):
        # Preloaded variant to work with stun music
        self.preloadedFinalBattleMusic = base.musicMgr.loadMusic(self.unDizzyMusic)
        self.preloadedFinalBattleDizzyMusic = base.musicMgr.loadMusic(self.dizzyMusic)

    def unloadEnvironment(self):
        self.preloadedFinalBattleMusic = None
        self.preloadedFinalBattleDizzyMusic = None

    def enterOff(self):
        self.cleanupIntervals()
        self.hide()
        self.clearChat()
        self.toWalkMode()

    def exitOff(self):
        self.show()

    def enterWaitForToons(self):
        self.cleanupIntervals()
        self.hide()
        if self.gotAllToons:
            self.__doneWaitForToons()
        else:
            self.accept('gotAllToons', self.__doneWaitForToons)

        base.transitions.fadeScreen(1.0, t=0)
        NametagGlobals.setMasterArrowsOn(0)

    def __doneWaitForToons(self):
        self.doneBarrier('WaitForToons')

    def exitWaitForToons(self):
        self.show()
        NametagGlobals.setMasterArrowsOn(1)

        # Ensure that the Toons have correct laff meters.
        messenger.send(OldLaffMeter.globalUpdateEvent())

    def enterElevator(self):
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
        camera.reparentTo(self.elevatorModel)
        camera.setPosHpr(0, 30, 8, 180, 0, 0)
        base.musicMgr.playMusic(self.elevatorMusic, looping=1, volume=1.0)
        base.transitions.fadeIn(0.8)
        ival = Sequence(ElevatorUtils.getRideElevatorInterval(self.elevatorType), ElevatorUtils.getRideElevatorInterval(self.elevatorType), self.openDoors, Func(camera.wrtReparentTo, render), Func(self.__doneElevator))
        intervalName = 'ElevatorMovie'
        ival.start()
        self.storeInterval(ival, intervalName)

    def __doneElevator(self):
        self.doneBarrier('Elevator')

    def exitElevator(self):
        intervalName = 'ElevatorMovie'
        self.clearInterval(intervalName)
        ElevatorUtils.closeDoors(self.leftDoor, self.rightDoor, self.elevatorType)

    def enterIntroduction(self):
        self.controlToons()
        ElevatorUtils.openDoors(self.leftDoor, self.rightDoor, self.elevatorType)
        NametagGlobals.setMasterArrowsOn(0)
        intervalName = 'IntroductionMovie'
        delayDeletes = []
        seq = Sequence(self.makeIntroductionMovie(delayDeletes), Func(self.__beginBattleOne), name=intervalName)
        seq.delayDeletes = delayDeletes
        seq.start()
        self.storeInterval(seq, intervalName)

    def __beginBattleOne(self):
        intervalName = 'IntroductionMovie'
        self.clearInterval(intervalName)
        self.doneBarrier('Introduction')

    def exitIntroduction(self):
        self.notify.debug('DistributedBossCog.exitIntroduction:')
        intervalName = 'IntroductionMovie'
        self.clearInterval(intervalName)
        self.unstickToons()
        self.releaseToons()
        NametagGlobals.setMasterArrowsOn(1)
        ElevatorUtils.closeDoors(self.leftDoor, self.rightDoor, self.elevatorType)

    def enterBattleOne(self):
        self.setBattleCreditMult()
        self.cleanupIntervals()
        self.toonsToBattlePosition(self.toonsA, self.battleANode)
        self.toonsToBattlePosition(self.toonsB, self.battleBNode)
        self.releaseToons()
        base.musicMgr.playMusic(self.battleOneMusic, looping=1, volume=0.9)

    def exitBattleOne(self):
        self.cleanupBattles()
        # localAvatar.inventory.setBattleCreditMult(1)

    def enterBattleTwo(self):
        self.setBattleCreditMult()
        self.cleanupIntervals()
        self.toonsToBattlePosition(self.toonsA, self.battleANode)
        self.toonsToBattlePosition(self.toonsB, self.battleBNode)
        self.releaseToons()
        base.musicMgr.playMusic(self.battleTwoMusic, looping=1, volume=0.9)

    def exitBattleTwo(self):
        self.cleanupBattles()

    def enterBattleThree(self):
        self.cleanupIntervals()
        self.releaseToons(finalBattle=1)
        self.accept('clickedNametag', self.__clickedNameTag)
        self.accept('friendAvatar', self.__handleFriendAvatar)
        self.accept('avatarDetails', self.__handleAvatarDetails)
        self.setPickable(0)
        NametagGlobals.setMasterArrowsOn(0)
        NametagGlobals.setMasterNametagsActive(1)

    def exitBattleThree(self):
        self.ignore('clickedNameTag')
        self.ignore('friendAvatar')
        self.ignore('avatarDetails')
        self.cleanupIntervals()

    def __clickedNameTag(self, avatar):
        self.notify.debug('__clickedNameTag')
        if not (self.state == 'BattleThree' or self.state == 'BattleFour'):
            return
        if not self.allowClickedNameTag:
            return
        if self.cr:
            place = self.cr.playGame.getPlace()
            if place and hasattr(place, 'fsm'):
                FriendsListManager.FriendsListManager._FriendsListManager__handleClickedNametag(place, avatar)

    def __handleFriendAvatar(self, avId, avName, avDisableName):
        self.notify.debug('__handleFriendAvatar')
        if not (self.state == 'BattleThree' or self.state == 'BattleFour'):
            return
        if not self.allowClickedNameTag:
            return
        if self.cr:
            place = self.cr.playGame.getPlace()
            if place and hasattr(place, 'fsm'):
                FriendsListManager.FriendsListManager._FriendsListManager__handleFriendAvatar(place, avId, avName, avDisableName)

    def __handleAvatarDetails(self, avId, avName, playerId = None):
        self.notify.debug('__handleAvatarDetails')
        if not (self.state == 'BattleThree' or self.state == 'BattleFour'):
            return
        if not self.allowClickedNameTag:
            return
        if self.cr:
            place = self.cr.playGame.getPlace()
            if place and hasattr(place, 'fsm'):
                FriendsListManager.FriendsListManager._FriendsListManager__handleAvatarDetails(place, avId, avName)

    def enterBattleFour(self):
        self.cleanupIntervals()
        self.releaseToons(finalBattle=1)
        self.accept('clickedNametag', self.__clickedNameTag)
        self.accept('friendAvatar', self.__handleFriendAvatar)
        self.accept('avatarDetails', self.__handleAvatarDetails)
        NametagGlobals.setMasterArrowsOn(0)
        NametagGlobals.setMasterNametagsActive(1)
        self.setPickable(0)

    def exitBattleFour(self):
        self.ignore('clickedNameTag')
        self.ignore('friendAvatar')
        self.ignore('avatarDetails')
        self.cleanupIntervals()

    def hideToonsMeters(self):
        for toonId in self.involvedToons:
            toon = base.cr.doId2do.get(toonId)
            if toon:
                toon.obscureOverheadMeter(True)

    def showToonsMeters(self):
        for toonId in self.involvedToons:
            toon = base.cr.doId2do.get(toonId)
            if toon:
                toon.obscureOverheadMeter(False)

    def enterFrolic(self):
        self.cleanupIntervals()
        self.clearChat()
        self.reparentTo(render)
        self.stopAnimate()
        self.pose('Ff_neutral', 0)
        self.releaseToons()

    def exitFrolic(self):
        pass

    def setToonsToNeutral(self, toonIds):
        for i in range(len(toonIds)):
            toon = base.cr.doId2do.get(toonIds[i])
            if toon:
                if toon.isDisguised:
                    toon.suit.loop('neutral')
                toon.loop('neutral')
                toon.setGeomNodeH(0)

    def wearCogSuits(self, toons, battleNode, camLoc, arrayOfObjs = False, waiter = False):
        seq = Sequence()
        if not toons:
            return seq
        self.notify.debug('battleNode=%s camLoc=%s' % (battleNode, camLoc))
        if camLoc:
            seq.append(Func(camera.setPosHpr, battleNode, *camLoc))
        suitsOff = Parallel()
        if arrayOfObjs:
            toonArray = toons
        else:
            toonArray = []
            for toonId in toons:
                toon = base.cr.doId2do.get(toonId)
                if toon:
                    toonArray.append(toon)

        for toon in toonArray:
            dustCloud = DustCloud.DustCloud()
            dustCloud.setPos(0, 2, 3)
            dustCloud.setScale(0.5)
            dustCloud.setDepthWrite(0)
            dustCloud.setBin('fixed', 0)
            dustCloud.createTrack()
            makeWaiter = Sequence()
            if waiter:
                makeWaiter = Func(toon.makeWaiter)
            suitsOff.append(Sequence(Func(dustCloud.reparentTo, toon), Parallel(dustCloud.track, Sequence(Wait(0.3), Func(self.putToonInCogSuit, toon), makeWaiter, Wait(0.7))), Func(dustCloud.detachNode)))

        seq.append(suitsOff)
        return seq

    def setBattleCreditMult(self, battleNum = None):
        if battleNum is None:
            battleNum = self.battleNumber
        mult = BattleGlobals.getBossBattleCreditMultiplier(battleNum)
        base.localAvatar.inventory.setBattleCreditMult(mult)

    def setBonusUnites(self, avId, unites):
        self.bonusUnites[avId] = unites

    def setUniteRewardId(self, uniteRewardId):
        self.uniteRewardId = [UniteRegistry.get(uId) for uId in uniteRewardId]

    def d_applyUniteReward(self):
        self.sendUpdate('applyUniteReward', [])

    def getUniteRewardNames(self, rewardCount):
        # Take self.rewardId[0:], convert them to valid names
        # Make the reward set
        rewardSet = set()
        for reward in self.uniteRewardId[:rewardCount]:
            rewardSet.add(reward)
        # Convert them into strings in an array
        rewardArray = []
        lastWord = ' Unite'
        for uniqueReward in rewardSet:
            results = 0
            for check in self.uniteRewardId[:rewardCount]:
                if check == uniqueReward:
                    results += 1
            lastWord = ' Unites' if results >= 2 else ' Unite'
            start = 'a' if results == 1 else TTLocalizer.numberToWord(results)
            rewardArray.append(f"{start} {uniqueReward.getName()}")
        # Convert an array to a full string
        rewardString = rewardArray[0]
        if len(rewardArray) == 2:
            rewardString = rewardString + ' and ' + rewardArray[1]
        elif len(rewardArray) > 2:
            for rewardId in rewardArray[1:]:
                if rewardId == rewardArray[len(rewardArray) - 1]:
                    rewardString = rewardString + ', and ' + rewardId
                else:
                    rewardString = rewardString + ', ' + rewardId
        return rewardString + lastWord

    def getUniteZeroChatPhrase(self):
        text = self.uniteRewardId[0].getChatText()

        return text

    def handleUniteSpeech(self, speech):
        self.localUniteEffectPageNumber = speech.count('\x07') + 2
        if self.bonusUnites.get(base.localAvatar.doId, None):
            extraStr = TTLocalizer.ToonBonusUnites % self.getUniteRewardNames(
                self.bonusUnites[base.localAvatar.doId])
            speech += extraStr.format(self.getUniteZeroChatPhrase())

        return speech

    @property
    def uniteResistanceToon(self):
        raise NotImplementedError("Please define a resistance toon to use the unite effect from.")

    def handleLocalUniteEffect(self):
        self.d_applyUniteReward()
        self.uniteRewardId[0].doEffect(self.uniteResistanceToon, self.involvedToons)
