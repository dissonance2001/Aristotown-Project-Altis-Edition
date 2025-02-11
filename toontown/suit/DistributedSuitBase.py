import copy
from direct.controls.ControlManager import CollisionHandlerRayStart
from direct.directnotify import DirectNotifyGlobal
from direct.directtools.DirectGeometry import CLAMP
from direct.distributed.ClockDelta import *
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.interval.IntervalGlobal import *
from direct.task import Task
import math
from pandac.PandaModules import *
from toontown.suit import DistributedSuitPlanner
from toontown.suit import Suit
from toontown.suit import SuitBase
from toontown.suit import SuitDNA
from toontown.suit import SuitDialog
from toontown.suit import SuitTimings
from otp.avatar import DistributedAvatar
from otp.otpbase import OTPGlobals
from toontown.battle import BattleProps
from toontown.battle import DistributedBattle
from toontown.chat.ChatGlobals import *
from toontown.nametag.NametagGlobals import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import ToontownGlobals

class DistributedSuitBase(DistributedAvatar.DistributedAvatar, Suit.Suit, SuitBase.SuitBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSuitBase')

    def __init__(self, cr):
        try:
            self.DistributedSuitBase_initialized
            return
        except:
            self.DistributedSuitBase_initialized = 1

        DistributedAvatar.DistributedAvatar.__init__(self, cr)
        Suit.Suit.__init__(self)
        SuitBase.SuitBase.__init__(self)
        self.activeShadow = 0
        self.virtual = 0
        self.immune = 0
        self.enraged = 0
        self.absorbing = 0
        self.soaked = 0
        self.isSkelecog = 0
        self.battleDetectName = None
        self.stars = BattleProps.globalPropPool.getProp('stun')
        self.stars.setPosHprScale(0, 0, .75, 0, 0, 0, 1, 1, 1)
        self.stars.loop('stun')
        self.stars.setBlend(frameBlend=base.wantSmoothAnims)
        self.stars.adjustAllPriorities(100)
        self.cRay = None
        self.cRayNode = None
        self.cRayNodePath = None
        self.cRayBitMask = None
        self.lifter = None
        self.cTrav = None
        self.sp = None
        self.cog = 0
        self.fsm = None
        self.prop = None
        self.propInSound = None
        self.propOutSound = None
        self.reparentTo(hidden)
        self.isOvercharged = 0
        self.loop('neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
        self.skeleRevives = 0
        self.dmgMult = 1.0
        self.maxSkeleRevives = 0
        self.executive = 0
        self.manager = 0
        self.dizzy = 0
        self.playRate = 1
        self.governaught = 0
        self.maxHP = 10
        self.currHP = 10
        self.sillySurgeText = False
        self.interactivePropTrackBonus = -1

    def setVirtual(self, flag, isVirtual = 1):
        SuitBase.SuitBase.setVirtual(self, flag)
        self.virtual = isVirtual
        if self.virtual:
            actorNode = self.find('**/__Actor_modelRoot')
            actorCollection = actorNode.findAllMatches('*')
            parts = ()
            for thingIndex in xrange(0, actorCollection.getNumPaths()):
                thing = actorCollection[thingIndex]
                if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag'):
                    thing.setColor(0, 1, 0.063, 1)
                    thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                    thing.setDepthWrite(False)
                    thing.setBin('fixed', 1)

    def getVirtual(self):
        return 0

    def setDamageMultiplier(self, mult):
        self.dmgMult = mult

    def getDamageMultiplier(self):
        return self.dmgMult

    def setDizzy(self, dizzy):
        head = self.find('**/to_head')
        #head = self.getHeadParts()[0]


        self.dizzy = dizzy
        if dizzy:
            self.stars.reparentTo(head)
        else:
            self.stars.detachNode()

    def getDizzy(self):
        return self.dizzy

    def setExecutive(self, executive):
        self.executive = executive
        if self.executive:
            self.processExecutive()

    def getExecutive(self):
        return self.executive

    def processExecutive(self):
        self.maxHP = self.getHP()
        #self.currHP = self.maxHP
        self.makeExecutive()
        nameInfo = self.createNameInfo()
        self.setDisplayName(nameInfo)

    def setCog(self, cog):
        self.cog = cog
        if self.cog:
            self.processCog()

    def getCog(self):
        return self.cog

    def processCog(self):
        self.maxHP = self.getHP()
        #self.currHP = self.maxHP

    def setGovernaught(self, governaught):
        self.governaught = governaught
        if self.governaught:
            self.processGovernaught()

    def getGovernaught(self):
        return self.governaught

    def processGovernaught(self):
        self.maxHP = self.getHP()
        #self.currHP = self.maxHP
        self.makeGovernaught()
        nameInfo = self.createNameInfo()
        self.setDisplayName(nameInfo)

    def setManager(self, manager):
        self.manager = manager
        if self.manager:
            self.processManager()

    def getManager(self):
        return self.manager

    def setPlayRate2(self, num):
        self.playRate = num

    def getPlayRate2(self):
        return self.playRate

    def processManager(self):
        self.maxHP = self.getHP()
        self.makeManager()
        nameInfo = self.createNameInfo()
        self.setDisplayName(nameInfo)

    def setSkeleRevives(self, num):
        if num == None:
            num = 0
        self.skeleRevives = num
        if num > self.maxSkeleRevives:
            self.maxSkeleRevives = num
        nameInfo = self.createNameInfo()
        self.setDisplayName(nameInfo)


    def createNameInfo(self):
        name = self.name
        dept = self.getStyleDept()
        level = str(self.getActualLevel())
        if self.getExecutive() and not self.getManager():
            level += TTLocalizer.ExecutivePostFix
        if self.getManager():
            level += TTLocalizer.ManagerPostFix
        if self.getGovernaught() and not self.getManager():
            level += TTLocalizer.GovernaughtPostFix
        if self.getSkeleRevives() > 0:
            level += TTLocalizer.SkeleRevivePostFix % (self.getSkeleRevives() + 1)
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoVirtual(self):
        name = self.name
        dept = self.getStyleDept()
        level = str(self.getActualLevel())
        if self.getExecutive():
            level += TTLocalizer.ExecutivePostFix
        if self.getManager():
            level += TTLocalizer.ManagerPostFix
        if self.getGovernaught():
            level += TTLocalizer.GovernaughtPostFix
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': 'Virtual Cog',
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoFired(self):
        name = self.name
        level = str(self.getActualLevel())
        nameInfo = TTLocalizer.SuitBaseNameWithLevelFired % {'name': name,
                                                        'level': level}
        return nameInfo

    def createNameInfoPurple(self):
        name = 'Purple Silhouette'
        dept = 'Cashbot'
        level = '25.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoLightBlue(self):
        name = 'Light Blue Silhouette'
        dept = 'Cashbot'
        level = '25.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoGreen(self):
        name = 'Green Silhouette'
        dept = 'Cashbot'
        level = '25.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoYellow(self):
        name = 'Yellow Silhouette'
        dept = 'Cashbot'
        level = '25.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoOrange(self):
        name = 'Orange Silhouette'
        dept = 'Cashbot'
        level = '25.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoRed(self):
        name = 'Red Silhouette'
        dept = 'Cashbot'
        level = '25.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoBlue(self):
        name = 'Blue Silhouette'
        dept = 'Cashbot'
        level = '25.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoPink(self):
        name = 'Pink Silhouette'
        dept = 'Cashbot'
        level = '25.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def setImmuneStatus(self, num):
        if num == None:
            num = 0
        if num == 0 and self.isImmune == 1:
            SuitBase.SuitBase.setImmuneStatus(self, num)
            self.removeImmune()
        self.isImmune = num
        if self.isImmune == 1:
            SuitBase.SuitBase.setImmuneStatus(self, self.isImmune)
            Suit.Suit.makeIntoImmune(self)
        return

    def getImmuneStatus(self):
        return self.isImmune

    def setEnragedStatus(self, num):
        if num == None:
            num = 0
        if num == 0 and self.isEnraged == 1:
            SuitBase.SuitBase.setEnragedStatus(self, num)
            self.removeEnraged()
        self.isEnraged = num
        if self.isEnraged == 1:
            SuitBase.SuitBase.setEnragedStatus(self, self.isEnraged)
            Suit.Suit.makeIntoEnraged(self)
        return

    def getEnragedStatus(self):
        return self.isEnraged

    def setAbsorbingStatus(self, num):
        if num == None:
            num = 0
        if num == 0 and self.isAbsorbing == 1:
            SuitBase.SuitBase.setAbsorbingStatus(self, num)
            self.removeAbsorbing()
        self.isAbsorbing = num
        if self.isAbsorbing == 1:
            SuitBase.SuitBase.setAbsorbingStatus(self, self.isAbsorbing)
            Suit.Suit.makeIntoAbsorbing(self)
        return

    def getAbsorbingStatus(self):
        return self.isAbsorbing

    def setSoakedStatus(self, num):
        if num == None:
            num = 0
        if num == 0:
            SuitBase.SuitBase.setSoakedStatus(self, num)
            self.removeSoaked()
        self.isSoaked = num
        if self.isSoaked == 1:
            SuitBase.SuitBase.setSoakedStatus(self, self.isSoaked)
            Suit.Suit.makeIntoSoaked(self)
        return

    def getSoakedStatus(self):
        return self.isSoaked

    def getSkeleRevives(self):
        return self.skeleRevives

    def getMaxSkeleRevives(self):
        return self.maxSkeleRevives

    def generate(self):
        DistributedAvatar.DistributedAvatar.generate(self)

    def disable(self):
        self.notify.debug('DistributedSuit %d: disabling' % self.getDoId())
        self.ignoreAll()
        self.__removeCollisionData()
        self.cleanupLoseActor()
        self.stop()
        taskMgr.remove(self.uniqueName('blink-task'))
        DistributedAvatar.DistributedAvatar.disable(self)

    def delete(self):
        try:
            self.DistributedSuitBase_deleted
            return
        except:
            self.DistributedSuitBase_deleted = 1
        
        self.notify.debug('DistributedSuit %d: deleting' % self.getDoId())
        del self.dna
        del self.sp
        DistributedAvatar.DistributedAvatar.delete(self)
        SuitBase.SuitBase.delete(self)

    def setDNAString(self, dnaString):
        Suit.Suit.setDNAString(self, dnaString)

    def setDNA(self, dna):
        Suit.Suit.setDNA(self, dna)

    def getHP(self):
        return self.currHP
		
    def getMaxHP(self):
        return self.maxHP

    def setHP(self, hp):
        if hp > self.maxHP * self.hardMaxHP:
            self.currHP = self.maxHP * self.hardMaxHP
        else:
            self.currHP = hp
        return None

    def setHealthForMe(self, health):
        self.hp = self.getHP() + health
        self.currHP = self.getHP() + health

    def setMHP(self, hitPoints):
        self.maxHP = hitPoints

    def getDialogueArray(self, *args):
        return Suit.Suit.getDialogueArray(self, *args)

    def __removeCollisionData(self):
        self.enableRaycast(0)
        self.cRay = None
        self.cRayNode = None
        self.cRayNodePath = None
        self.lifter = None
        self.cTrav = None

    def setHeight(self, height):
        Suit.Suit.setHeight(self, height)

    def getRadius(self):
        return Suit.Suit.getRadius(self)

    def setLevelDist(self, level):
        if self.notify.getDebug():
            self.notify.debug('Got level %d from server for suit %d' % (level, self.getDoId()))
        self.setLevel(level)

    def attachPropeller(self):
        if self.prop == None:
            self.prop = BattleProps.globalPropPool.getProp('propeller')
        if self.propInSound == None:
            self.propInSound = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_in.ogg')
        if self.propOutSound == None:
            self.propOutSound = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_out.ogg')
        if base.config.GetBool('want-new-cogs', 0):
            head = self.find('**/to_head')
            if head.isEmpty():
                head = self.find('**/joint_head')
        else:
            head = self.find('**/joint_head')
        
        self.prop.reparentTo(head)

    def detachPropeller(self):
        if self.prop:
            self.prop.cleanup()
            self.prop.removeNode()
            self.prop = None
        if self.propInSound:
            self.propInSound = None
        if self.propOutSound:
            self.propOutSound = None

    def beginSupaFlyMove(self, pos, moveIn, trackName, walkAfterLanding=True):
        skyPos = Point3(pos)
        if moveIn:
            skyPos.setZ(pos.getZ() + SuitTimings.fromSky * ToontownGlobals.SuitWalkSpeed)
        else:
            skyPos.setZ(pos.getZ() + SuitTimings.toSky * ToontownGlobals.SuitWalkSpeed)
        groundF = 28
        dur = self.getDuration('landing')
        fr = self.getFrameRate('landing')
        if fr:
            animTimeInAir = groundF / fr
        else:
            animTimeInAir = groundF
        impactLength = dur - animTimeInAir
        timeTillLanding = SuitTimings.fromSky - impactLength
        waitTime = timeTillLanding - animTimeInAir
        if self.prop == None:
            self.prop = BattleProps.globalPropPool.getProp('propeller')
        propDur = self.prop.getDuration('propeller')
        lastSpinFrame = 8
        fr = self.prop.getFrameRate('propeller')
        spinTime = lastSpinFrame / fr
        openTime = (lastSpinFrame + 1) / fr
        if moveIn:
            lerpPosTrack = Sequence(self.posInterval(timeTillLanding, pos, startPos=skyPos), Wait(impactLength))
            shadowScale = self.dropShadow.getScale()
            shadowTrack = Sequence(Func(self.dropShadow.reparentTo, render), Func(self.dropShadow.setPos, pos), self.dropShadow.scaleInterval(timeTillLanding, self.scale, startScale=Vec3(0.01, 0.01, 1.0)), Func(self.dropShadow.reparentTo, self.getShadowJoint()), Func(self.dropShadow.setPos, 0, 0, 0), Func(self.dropShadow.setScale, shadowScale))
            fadeInTrack = Sequence(Func(self.setTransparency, 1), self.colorScaleInterval(1, colorScale=VBase4(1, 1, 1, 1), startColorScale=VBase4(1, 1, 1, 0)), Func(self.clearColorScale), Func(self.clearTransparency))
            animTrack = Sequence(Func(self.pose, 'landing', 0), Wait(waitTime), ActorInterval(self, 'landing', duration=dur))
            if walkAfterLanding:
                animTrack.append(Func(self.loop, 'walk'))
            self.attachPropeller()
            propTrack = Parallel(SoundInterval(self.propInSound, duration=waitTime + dur, node=self), Sequence(ActorInterval(self.prop, 'propeller', constrainedLoop=1, duration=waitTime + spinTime, startTime=0.0, endTime=spinTime), ActorInterval(self.prop, 'propeller', duration=propDur - openTime, startTime=openTime), Func(self.detachPropeller)))
            return Parallel(lerpPosTrack, shadowTrack, fadeInTrack, animTrack, propTrack, name=self.taskName('trackName'))
        else:
            lerpPosTrack = Sequence(Wait(impactLength), LerpPosInterval(self, timeTillLanding, skyPos, startPos=pos))
            #shadowTrack = Sequence(Func(self.dropShadow.reparentTo, render), Func(self.dropShadow.setPos, pos), self.dropShadow.scaleInterval(timeTillLanding, Vec3(0.01, 0.01, 1.0), startScale=self.scale), Func(self.dropShadow.reparentTo, self.getShadowJoint()), Func(self.dropShadow.setPos, 0, 0, 0))
            fadeOutTrack = Sequence(Func(self.setTransparency, 1), self.colorScaleInterval(1, colorScale=VBase4(1, 1, 1, 0), startColorScale=VBase4(1, 1, 1, 1)), Func(self.clearColorScale), Func(self.clearTransparency), Func(self.reparentTo, hidden))
            actInt = ActorInterval(self, 'landing', loop=0, startTime=dur, endTime=0.0)
            self.attachPropeller()
            self.prop.hide()
            propTrack = Parallel(SoundInterval(self.propOutSound, duration=waitTime + dur, node=self), Sequence(Func(self.prop.show), ActorInterval(self.prop, 'propeller', endTime=openTime, startTime=propDur), ActorInterval(self.prop, 'propeller', constrainedLoop=1, duration=propDur - openTime, startTime=spinTime, endTime=0.0), Func(self.detachPropeller)))
            return Parallel(ParallelEndTogether(lerpPosTrack, fadeOutTrack), actInt, propTrack, name=self.taskName('trackName'))

    def enableBattleDetect(self, name, handler):
        if self.collTube:
            self.battleDetectName = self.taskName(name)
            self.collNode = CollisionNode(self.battleDetectName)
            self.collNode.addSolid(self.collTube)
            self.collNodePath = self.attachNewNode(self.collNode)
            self.collNode.setCollideMask(ToontownGlobals.WallBitmask)
            self.accept('enter' + self.battleDetectName, handler)
        
        return Task.done

    def disableBattleDetect(self):
        if self.battleDetectName:
            self.ignore('enter' + self.battleDetectName)
            self.battleDetectName = None
        if self.collNodePath:
            self.collNodePath.removeNode()
            self.collNodePath = None

    def enableRaycast(self, enable = 1):
        if not self.cTrav or not hasattr(self, 'cRayNode') or not self.cRayNode:
            return
        self.cTrav.removeCollider(self.cRayNodePath)
        if enable:
            if self.notify.getDebug():
                self.notify.debug('enabling raycast')
            self.cTrav.addCollider(self.cRayNodePath, self.lifter)
        elif self.notify.getDebug():
            self.notify.debug('disabling raycast')

    def b_setBrushOff(self, index):
        self.setBrushOff(index)
        self.d_setBrushOff(index)

    def d_setBrushOff(self, index):
        self.sendUpdate('setBrushOff', [index])

    def setBrushOff(self, index):
        self.setChatAbsolute(SuitDialog.getBrushOffText(self.getStyleName(), index), CFSpeech | CFTimeout)

    def initializeBodyCollisions(self, collIdStr):
        DistributedAvatar.DistributedAvatar.initializeBodyCollisions(self, collIdStr)
        if not self.ghostMode:
            self.collNode.setCollideMask(self.collNode.getIntoCollideMask() | ToontownGlobals.PieBitmask)
        self.cRay = CollisionRay(0.0, 0.0, CollisionHandlerRayStart, 0.0, 0.0, -1.0)
        self.cRayNode = CollisionNode(self.taskName('cRay'))
        self.cRayNode.addSolid(self.cRay)
        self.cRayNodePath = self.attachNewNode(self.cRayNode)
        self.cRayNodePath.hide()
        self.cRayBitMask = ToontownGlobals.FloorBitmask
        self.cRayNode.setFromCollideMask(self.cRayBitMask)
        self.cRayNode.setIntoCollideMask(BitMask32.allOff())
        self.lifter = CollisionHandlerFloor()
        self.lifter.setOffset(ToontownGlobals.FloorOffset)
        self.lifter.setReach(6.0)
        self.lifter.setMaxVelocity(8.0)
        self.lifter.addCollider(self.cRayNodePath, self)
        self.cTrav = base.cTrav

    def disableBodyCollisions(self):
        self.disableBattleDetect()
        self.enableRaycast(0)
        if self.cRayNodePath:
            self.cRayNodePath.removeNode()
        del self.cRayNode
        del self.cRay
        del self.lifter

    def denyBattle(self):
        self.notify.debug('denyBattle()')
        place = self.cr.playGame.getPlace()
        if place.fsm.getCurrentState().getName() == 'WaitForBattle':
            place.setState('walk')
        self.resumePath(self.pathState)

    def makePathTrack(self, nodePath, posPoints, velocity, name):
        track = Sequence(name=name)
        nodePath.setPos(posPoints[0])
        for pointIndex in xrange(len(posPoints) - 1):
            startPoint = posPoints[pointIndex]
            endPoint = posPoints[pointIndex + 1]
            track.append(Func(nodePath.headsUp, endPoint[0], endPoint[1], endPoint[2]))
            distance = Vec3(endPoint - startPoint).length()
            duration = distance / velocity
            track.append(LerpPosInterval(nodePath, duration=duration, pos=Point3(endPoint), startPos=Point3(startPoint)))
        
        return track

    def setState(self, state):
        if self.fsm == None:
            return 0
        if self.fsm.getCurrentState().getName() == state:
            return 0
        
        return self.fsm.request(state)

    def subclassManagesParent(self):
        return 0

    def enterOff(self, *args):
        self.hideNametag3d()
        self.hideNametag2d()
        if not self.subclassManagesParent():
            self.setParent(ToontownGlobals.SPHidden)

    def exitOff(self):
        if not self.subclassManagesParent():
            self.setParent(ToontownGlobals.SPRender)
        self.showNametag3d()
        self.showNametag2d()
        self.loop('neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',), 0)

    def enterBattle(self):
        self.loop('neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',), 0)
        self.disableBattleDetect()
        self.healthBar.show()
        self.corpMedallion.hide()
        if self.currHP < self.maxHP:
            self.updateHealthBar(0, 1)
        if self.currHP >= self.maxHP:
            self.updateHealthBar(0, 1)

    def exitBattle(self):
        if not self.virtual:
            self.healthBar.hide()
            self.corpMedallion.show()
        self.currHP = self.maxHP
        self.interactivePropTrackBonus = -1

    def enterWaitForBattle(self):
        self.loop('neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',), 0)

    def exitWaitForBattle(self):
        pass

    def setSkelecog2(self, flag):
        self.isSkelecog = flag
        SuitBase.SuitBase.setSkelecog(self, flag)
        self.processSkelecog()
        if flag:
            Suit.Suit.makeSkeleton2(self)

    def setSkelecog(self, flag):
        self.isSkelecog = flag
        SuitBase.SuitBase.setSkelecog(self, flag)
        self.processSkelecog()
        if flag:
            Suit.Suit.makeSkeleton(self)

    def processSkelecog(self):
        self.maxHP = self.getHP()

    def setWaiter(self, flag):
        SuitBase.SuitBase.setWaiter(self, flag)
        if flag:
            Suit.Suit.makeWaiter(self)
			
    def setElite(self, flag):
        SuitBase.SuitBase.setElite(self, flag)
        if flag:
            #self.resetNameForElite()
            self.setMaxHP(self.maxHP * 1.0)
			
    def setMaxHP(self, hp):
        self.maxHP = int(hp)
        self.currHP = int(hp)
			
    def resetNameForElite(self):
        name = self.name
        dept = self.getStyleDept()
        level = str(self.getActualLevel())
        if self.getExecutive():
            level += TTLocalizer.ExecutivePostFix
        if self.getManager():
            level += TTLocalizer.ManagerPostFix
        if self.getGovernaught():
            level += TTLocalizer.GovernaughtPostFix
        if self.getSkeleRevives() > 0:
            level += TTLocalizer.SkeleRevivePostFix % (self.getSkeleRevives() + 1)
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': 'Skelecog',
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def showHpText(self, number, bonus = 0, scale = 1, attackTrack = -1):
        if self.HpTextEnabled and not self.ghostMode:
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText(str(number))
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        self.sillySurgeText = True
                        if attackTrack in TTLocalizer.InteractivePropTrackBonusTerms:
                            self.HpTextGenerator.setText(str(number) + '\n' + TTLocalizer.InteractivePropTrackBonusTerms[attackTrack])
                elif type(number) in [int, float]:
                    self.HpTextGenerator.setText('+' + str(number))
                else:
                    self.HpTextGenerator.setText(str(number))
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 1.0
                    b = 0
                    a = 1
                elif bonus == 2:
                    r = 1.0
                    g = 0.5
                    b = 0
                    a = 1
                elif bonus == 3:
                    r = 1
                    g = 0
                    b = 0.984
                    a = 1
                elif bonus == 4:
                    r = 0.466
                    g = 0.474
                    b = 1
                    a = 1
                elif number < 0:
                    r = 0.9
                    g = 0
                    b = 0
                    a = 1
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        r = 0
                        g = 0
                        b = 1
                        a = 1
                else:
                    r = 0
                    g = 0.9
                    b = 0
                    a = 1
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardPointEye()
                self.hpText.setBin('fixed', 100)
                if self.sillySurgeText:
                    self.nametag3d.setDepthTest(0)
                    self.nametag3d.setBin('fixed', 99)
                self.hpText.setPos(0, 0, self.height / 2)
                seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                seq.start()

    def showHpText2(self, number, bonus = 0, scale = 1, attackTrack = -1):
        if self.HpTextEnabled and not self.ghostMode:
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText(str(number))
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        self.sillySurgeText = True
                        if attackTrack in TTLocalizer.InteractivePropTrackBonusTerms:
                            self.HpTextGenerator.setText(str(number) + '\n' + TTLocalizer.InteractivePropTrackBonusTerms[attackTrack])
                elif type(number) in [int, float]:
                    self.HpTextGenerator.setText('+' + str(number))
                else:
                    self.HpTextGenerator.setText(str(number))
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 1.0
                    b = 0
                    a = 1
                elif bonus == 2:
                    r = 1.0
                    g = 0.5
                    b = 0
                    a = 1
                elif bonus == 3:
                    r = 1
                    g = 0
                    b = 0.984
                    a = 1
                elif bonus == 4:
                    r = 0.466
                    g = 0.474
                    b = 1
                    a = 1
                elif number < 0:
                    r = 0.9
                    g = 0
                    b = 0
                    a = 1
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        r = 0
                        g = 0
                        b = 1
                        a = 1
                else:
                    r = 0
                    g = 0.9
                    b = 0
                    a = 1
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardPointEye()
                self.hpText.setBin('fixed', 100)
                if self.sillySurgeText:
                    self.nametag3d.setDepthTest(0)
                    self.nametag3d.setBin('fixed', 99)
                self.hpText.setPos(0, 0, self.height / 2)
                seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 3.5), blendType='easeOut'), Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                seq.start()

    def showHpTextCheat(self, number, bonus = 0, scale = 1, attackTrack = -1):
        if self.HpTextEnabled and not self.ghostMode:
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText(str(number))
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        self.sillySurgeText = True
                        if attackTrack in TTLocalizer.InteractivePropTrackBonusTerms:
                            self.HpTextGenerator.setText(str(number) + '\n' + TTLocalizer.InteractivePropTrackBonusTerms[attackTrack])
                elif type(number) in [int, float]:
                    self.HpTextGenerator.setText('+' + str(number))
                else:
                    self.HpTextGenerator.setText(str(number))
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 1.0
                    b = 0
                    a = 1
                elif bonus == 2:
                    r = 1.0
                    g = 0.5
                    b = 0
                    a = 1
                elif bonus == 3:
                    r = 1
                    g = 0
                    b = 0.984
                    a = 1
                elif bonus == 4:
                    r = 0.466
                    g = 0.474
                    b = 1
                    a = 1
                elif number < 0:
                    r = 0.9
                    g = 0
                    b = 0
                    a = 1
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        r = 0
                        g = 0
                        b = 1
                        a = 1
                else:
                    r = 0
                    g = 0.9
                    b = 0
                    a = 1
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardPointEye()
                self.hpText.setBin('fixed', 100)
                if self.sillySurgeText:
                    self.nametag3d.setDepthTest(0)
                    self.nametag3d.setBin('fixed', 99)
                self.hpText.setPos(0, 0, self.height / 2)
                seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                seq.start()

    def showHpTextLureInfo(self, number, bonus = 0, scale = 1, attackTrack = -1):
        if self.HpTextEnabled and not self.ghostMode:
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText(str(number))
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        self.sillySurgeText = True
                        if attackTrack in TTLocalizer.InteractivePropTrackBonusTerms:
                            self.HpTextGenerator.setText(str(number) + '\n' + TTLocalizer.InteractivePropTrackBonusTerms[attackTrack])
                elif type(number) in [int, float]:
                    self.HpTextGenerator.setText('+' + str(number))
                else:
                    self.HpTextGenerator.setText(str(number))
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 0
                    b = 0
                    a = 1
                elif bonus == 2:
                    r = 0.871
                    g = 0.827
                    b = 1
                    a = 1
                elif bonus == 3:
                    r = 1
                    g = 0
                    b = 0.984
                    a = 1
                elif bonus == 4:
                    r = 0.466
                    g = 0.474
                    b = 1
                    a = 1
                elif bonus == 5:
                    r = 1
                    g = 0.757
                    b = 0
                    a = 1
                elif number < 0:
                    r = 0.9
                    g = 0
                    b = 0
                    a = 1
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        r = 0
                        g = 0
                        b = 1
                        a = 1
                else:
                    r = 0
                    g = 0.9
                    b = 0
                    a = 1
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardPointEye()
                self.hpText.setBin('fixed', 100)
                if self.sillySurgeText:
                    self.nametag3d.setDepthTest(0)
                    self.nametag3d.setBin('fixed', 99)
                self.hpText.setPos(0, 0, self.height / 2)
                seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                seq.start()

    def showHpTextSquirt(self, level, number, bonus = 0, scale = 1, attackTrack = -1):
        if self.HpTextEnabled and not self.ghostMode:
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText(str(number))
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        self.sillySurgeText = True
                        if attackTrack in TTLocalizer.InteractivePropTrackBonusTerms:
                            self.HpTextGenerator.setText(str(number) + '\n' + TTLocalizer.InteractivePropTrackBonusTerms[attackTrack])
                elif type(number) in [int, float]:
                    self.HpTextGenerator.setText('+' + str(number))
                else:
                    self.HpTextGenerator.setText(str(number))
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 1.0
                    b = 0
                    a = 1
                elif bonus == 2:
                    r = 1.0
                    g = 0.5
                    b = 0
                    a = 1
                elif bonus == 3:
                    r = 0.6
                    g = 0.2
                    b = 0.8
                    a = 1.0
                    scale = 0.9
                elif bonus == 4:
                    r = 0.93
                    g = 0.51
                    b = 0.93
                    a = 1.0
                    scale = 0.9
                elif number < 0:
                    r = 0.9
                    g = 0
                    b = 0
                    a = 1
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        r = 0
                        g = 0
                        b = 1
                        a = 1
                else:
                    r = 0
                    g = 0.9
                    b = 0
                    a = 1
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardPointEye()
                self.hpText.setBin('fixed', 100)
                if self.sillySurgeText:
                    self.nametag3d.setDepthTest(0)
                    self.nametag3d.setBin('fixed', 99)
                self.hpText.setPos(0, 0, self.height / 2)
                seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                seq.start()

    def showHpTextAbsorb(self, number, bonus = 0, scale = 1, attackTrack = -1):
        if self.HpTextEnabled and not self.ghostMode:
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText(str(number))
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        self.sillySurgeText = True
                        if attackTrack in TTLocalizer.InteractivePropTrackBonusTerms:
                            self.HpTextGenerator.setText(
                                str(number) + '\n' + TTLocalizer.InteractivePropTrackBonusTerms[attackTrack])
                elif type(number) in [int, float]:
                    self.HpTextGenerator.setText('+' + str(number))
                else:
                    self.HpTextGenerator.setText(str(number))
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 1.0
                    b = 0
                    a = 1
                elif bonus == 2:
                    r = 1.0
                    g = 0.5
                    b = 0
                    a = 1
                elif bonus == 3:
                    r = 0.6
                    g = 0.2
                    b = 0.8
                    a = 1.0
                    scale = 0.9
                elif bonus == 4:
                    r = 0.93
                    g = 0.51
                    b = 0.93
                    a = 1.0
                    scale = 0.9
                elif number < 0:
                    r = 0.9
                    g = 0
                    b = 0
                    a = 1
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        r = 0
                        g = 0
                        b = 1
                        a = 1
                else:
                    r = 0
                    g = 0.9
                    b = 0
                    a = 1
                self.HpTextGenerator.setTextColor(1, 0, 0, 1)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardPointEye()
                self.hpText.setBin('fixed', 100)
                if self.sillySurgeText:
                    self.nametag3d.setDepthTest(0)
                    self.nametag3d.setBin('fixed', 99)
                self.hpText.setPos(0, 0, self.height / 2)
                seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'),
                               Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)),
                               Func(self.hideHpText))
                seq.start()

    def showHpTextThrow(self, number, bonus = 0, scale = 1, attackTrack = -1):
        if self.HpTextEnabled and not self.ghostMode:
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText(str(number))
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        self.sillySurgeText = True
                        if attackTrack in TTLocalizer.InteractivePropTrackBonusTerms:
                            self.HpTextGenerator.setText(str(number) + '\n' + TTLocalizer.InteractivePropTrackBonusTerms[attackTrack])
                elif type(number) in [int, float]:
                    self.HpTextGenerator.setText('+' + str(number))
                else:
                    self.HpTextGenerator.setText(str(number))
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 1.0
                    b = 0
                    a = 1
                elif bonus == 2:
                    r = 1.0
                    g = 0.5
                    b = 0
                    a = 1
                elif bonus == 3:
                    r = 0.6
                    g = 0.2
                    b = 0.8
                    a = 1.0
                    scale = 0.9
                elif bonus == 4:
                    r = 0.93
                    g = 0.51
                    b = 0.93
                    a = 1.0
                    scale = 0.9
                elif number < 0:
                    r = 0.9
                    g = 0
                    b = 0
                    a = 1
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        r = 0
                        g = 0
                        b = 1
                        a = 1
                else:
                    r = 0
                    g = 0.9
                    b = 0
                    a = 1
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardPointEye()
                self.hpText.setBin('fixed', 100)
                if self.sillySurgeText:
                    self.nametag3d.setDepthTest(0)
                    self.nametag3d.setBin('fixed', 99)
                self.hpText.setPos(0, 0, self.height / 2)
                seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                seq.start()

    def showHpTextWhite(self, number, bonus = 0, scale = 1, attackTrack = -1):
        if self.HpTextEnabled and not self.ghostMode:
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText('INSURANCE!')
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        self.sillySurgeText = True
                        if attackTrack in TTLocalizer.InteractivePropTrackBonusTerms:
                            self.HpTextGenerator.setText(str(number) + '\n' + TTLocalizer.InteractivePropTrackBonusTerms[attackTrack])
                elif type(number) in [int, float]:
                    self.HpTextGenerator.setText('+' + str(number))
                else:
                    self.HpTextGenerator.setText(str(number))
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 1.0
                    b = 0
                    a = 1
                elif bonus == 2:
                    r = 1.0
                    g = 0.5
                    b = 0
                    a = 1
                elif bonus == 3:
                    r = 0.6
                    g = 0.2
                    b = 0.8
                    a = 1.0
                    scale = 0.9
                elif bonus == 4:
                    r = 0.93
                    g = 0.51
                    b = 0.93
                    a = 1.0
                    scale = 0.9
                elif number < 0:
                    r = 0.9
                    g = 0
                    b = 0
                    a = 1
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        r = 0
                        g = 0
                        b = 1
                        a = 1
                else:
                    r = 0
                    g = 0.9
                    b = 0
                    a = 1
                self.HpTextGenerator.setTextColor(1, 1, 1, 1)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardPointEye()
                self.hpText.setBin('fixed', 100)
                if self.sillySurgeText:
                    self.nametag3d.setDepthTest(0)
                    self.nametag3d.setBin('fixed', 99)
                self.hpText.setPos(0, 0, self.height / 2)
                seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'),Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                seq.start()

    def showHpTextTrap(self, number, bonus = 0, scale = 1, attackTrack = -1):
        if self.HpTextEnabled and not self.ghostMode:
            if number != 0:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText(str(number))
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        self.sillySurgeText = True
                        if attackTrack in TTLocalizer.InteractivePropTrackBonusTerms:
                            self.HpTextGenerator.setText(str(number) + '\n' + TTLocalizer.InteractivePropTrackBonusTerms[attackTrack])
                elif type(number) in [int, float]:
                    self.HpTextGenerator.setText('+' + str(number))
                else:
                    self.HpTextGenerator.setText(str(number))
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 1.0
                    b = 0
                    a = 1
                elif bonus == 2:
                    r = 1.0
                    g = 0.5
                    b = 0
                    a = 1
                elif bonus == 3:
                    r = 0.6
                    g = 0.2
                    b = 0.8
                    a = 1.0
                    scale = 0.9
                elif bonus == 4:
                    r = 0.93
                    g = 0.51
                    b = 0.93
                    a = 1.0
                    scale = 0.9
                elif number < 0:
                    r = 0.9
                    g = 0
                    b = 0
                    a = 1
                    if self.interactivePropTrackBonus > -1 and self.interactivePropTrackBonus == attackTrack:
                        r = 0
                        g = 0
                        b = 1
                        a = 1
                else:
                    r = 0
                    g = 0.9
                    b = 0
                    a = 1
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setBillboardPointEye()
                self.hpText.setBin('fixed', 100)
                if self.sillySurgeText:
                    self.nametag3d.setDepthTest(0)
                    self.nametag3d.setBin('fixed', 99)
                self.hpText.setPos(0, 0, self.height / 2)
                seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                seq.start()


    def showHpString(self, text, duration = 0.85, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            self.HpTextGenerator.setText(text)
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            r = a = 1.0
            g = b = 0.0
            self.HpTextGenerator.setTextColor(0.871, 0.827, 1, 1)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(scale)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 100)
            self.hpText.setPos(0, 0, self.height / 2)
            seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            seq.start()

    def showHpStringLureOvercharged(self, text, duration = 0.85, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            self.HpTextGenerator.setText(text)
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            r = a = 1.0
            g = b = 0.0
            self.HpTextGenerator.setTextColor(1, 0, 0.969, 1)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(scale)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 100)
            self.hpText.setPos(0, 0, self.height / 2)
            seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            seq.start()

    def showHpStringLureManager(self, text, duration = 0.85, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            self.HpTextGenerator.setText(text)
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            r = a = 1.0
            g = b = 0.0
            self.HpTextGenerator.setTextColor(0.466, 0.474, 1.0, 1.0)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(scale)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 100)
            self.hpText.setPos(0, 0, self.height / 2)
            seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            seq.start()

    def showHpStringLureManager2(self, text, duration = 0.85, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            self.HpTextGenerator.setText(text)
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            r = a = 1.0
            g = b = 0.0
            self.HpTextGenerator.setTextColor(0.466, 0.474, 1.0, 1.0)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(scale)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 100)
            self.hpText.setPos(0, 0, self.height / 2)
            seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            seq.start()

    def showHpStringLureDesperation(self, text, duration = 0.85, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            self.HpTextGenerator.setText(text)
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            r = a = 1.0
            g = b = 0.0
            self.HpTextGenerator.setTextColor(1, 0.682, 0, 1)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(scale)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 100)
            self.hpText.setPos(0, 0, self.height / 2)
            seq = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            seq.start()


    def hideHpText(self):
        try:
            DistributedAvatar.DistributedAvatar.hideHpText(self)
            if self.sillySurgeText:
                self.nametag3d.clearDepthTest()
                self.nametag3d.clearBin()
                self.sillySurgeText = False
        except:
            pass

    def getAvIdName(self):
        try:
            level = self.getActualLevel()
        except:
            level = '???'

        return '%s\n%s\nLevel %s' % (self.getName(), self.doId, level)