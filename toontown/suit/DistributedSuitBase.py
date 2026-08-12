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
import random
from pandac.PandaModules import *
from toontown.suit import DistributedSuitPlanner
from toontown.chat.ChatGlobals import *
from toontown.suit import Suit
from toontown.suit import SuitBase
from toontown.suit import SuitDNA
from otp.otpbase import OTPLocalizer
from panda3d.core import TextureStage
from toontown.suit import SuitDialog
from toontown.suit import SuitTimings
from toontown.nametag.NametagGlobals import *
from toontown.battle import PlayByPlayText
from otp.avatar import DistributedAvatar
from toontown.battle import DistributedBattle
from toontown.battle import SuitBattleGlobals
from toontown.battle import MovieUtil
from otp.otpbase import OTPGlobals
from toontown.battle import BattleProps
from toontown.battle import DistributedBattle
from toontown.chat.ChatGlobals import *
from toontown.nametag import NametagGlobals
from otp.otpbase import OTPLocalizerEnglish
from toontown.nametag.NametagGlobals import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import ToontownGlobals
from toontown.battle import SuitBattleGlobals

SoakColor = Point4(0.737, 0.737, 1, 1.0)
DrenchColor = Point4(0.643, 0.643, 1, 1)
OilColor = Point4(0.302, 0.302, 0.302, 1)

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
        self.absorbDamage = 0
        self.fraudulentDamage = 0
        self.levelDamage = 0
        self.deadSuits = []
        self.playByPlayInterval = None
        self.damageInterval = None
        self.headInterval = None
        self.neutralInterval = None
        self.deathInterval = None
        self.luredInterval = None
        self.headInterval2 = None
        self.healInterval = None
        self.absorbInterval = None
        self.syphonHP = 0
        self._pendingQueuedDamage = 0
        self._pendingQueuedDeath = False
        self._pendingQueuedHealing = 0
        self.rpmIncrease2 = 0
        self._pendingQueuedRevive = False
        self.splashInterval = None
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
        #self.stars.loop('stun')
        self.stars.setBlend(frameBlend=base.wantSmoothAnims)
        self.stars.adjustAllPriorities(100)
        self.stars3 = BattleProps.globalPropPool.getProp('stun')
        self.stars3.setPosHprScale(0, 0, .75, 0, 0, 0, 1, 1, 1)
        #self.stars.loop('stun')
        self.stars3.setBlend(frameBlend=base.wantSmoothAnims)
        self.stars3.adjustAllPriorities(100)
        texture = loader.loadTexture('phase_5/maps/battle/ttcc_fx_battleParticles_palette_2.png')
        self.suedstars = BattleProps.globalPropPool.getProp('stun')
        self.suedstars.setPosHprScale(0, 0, .75, 0, 0, 0, 1, 1, 1)
        self.suedstars.setScale(1.5)
        #self.suedstars.loop('stun')
        self.suedstars.setTexture(texture, 1)
        self.suedstars.setBlend(frameBlend=base.wantSmoothAnims)
        self.suedstars.adjustAllPriorities(100)
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
        #self.loop('neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
        self.skeleRevives = 0
        self.dmgMult = 1.0
        self.vulnerabilityMult = 1.0
        self.maxSkeleRevives = 0
        self.governaught = 0
        self.executive = 0
        self.manager = 0
        self.dizzy = 0
        self.dizzy2 = 0
        self.sued = 0
        self.playRate = 1
        self.actualLevel = 0
        self.maxHP = 10
        self.currHP = 10
        self.sillySurgeText = False
        self.interactivePropTrackBonus = -1
        self.hpTextInterval = None
        self.hpTextInterval2 = None
        self.soundSequenceList = []
        self.__currentDialogue = None

    def __createSuitResetPosTrack(self, battle):
        self.clearPendingQueuedLured()
        resetPos, resetHpr = battle.getActorPosHpr(self)
        moveDist = Vec3(self.getPos(battle) - resetPos).length()
        moveDuration = 0.5
        unluredTrack = Func(battle.unlureSuit, self)
        unlureSuit = Parallel(Func(self.setDizzy, 0), Func(self.makeUnLured))
        walkTrack = Sequence(Func(self.setHpr, battle, resetHpr), ActorInterval(self, 'walk', startTime=1, duration=moveDuration, endTime=0.0001), Func(self.setNeutralAnimationTrap))
        moveTrack = LerpPosInterval(self, moveDuration, resetPos, other=battle)
        return Parallel(unluredTrack, unlureSuit, walkTrack, moveTrack)

    def checkPlayByPlayText(self, pbpText, displayName, attackDuration):
        if self.playByPlayInterval != None:
            self.playByPlayInterval.finish()
          #  del self.playByPlayInterval
        pbpText = pbpText
        if float(self.currHP) > float(self.maxHP * 1.5):
            self.playByPlayInterval = pbpText.getShowIntervalOvercharged(displayName, attackDuration)
            self.playByPlayInterval.start()
        elif float(self.currHP) > float(self.maxHP):
            self.playByPlayInterval = pbpText.getShowIntervalOverhealed(displayName, attackDuration)
            self.playByPlayInterval.start()
        else:
            self.playByPlayInterval = pbpText.getShowInterval(displayName, attackDuration)
            self.playByPlayInterval.start()

    def checkPlayByPlayTextCheat(self, pbpText, displayName, attackDuration):
        if self.playByPlayInterval != None:
            self.playByPlayInterval.finish()
           # del self.playByPlayInterval
        pbpText = pbpText
        if float(self.currHP) > float(self.maxHP * 1.5):
            self.playByPlayInterval = pbpText.getShowIntervalCheatOvercharged(displayName, attackDuration)
            self.playByPlayInterval.start()
        elif float(self.currHP) > float(self.maxHP):
            self.playByPlayInterval = pbpText.getShowIntervalCheatOverhealed(displayName, attackDuration)
            self.playByPlayInterval.start()
        else:
            self.playByPlayInterval = pbpText.getShowIntervalCheatRed(displayName, attackDuration)
            self.playByPlayInterval.start()

    def checkPlayByPlayTextLegallyBound(self, pbpText, attackDuration):
        if self.playByPlayInterval != None:
            self.playByPlayInterval.finish()
            #del self.playByPlayInterval
        pbpText = pbpText
        if self.isDesperation:
            self.playByPlayInterval = pbpText.getShowIntervalDesc("Legally Bound Toons take 28 damage per round!", attackDuration)
            self.playByPlayInterval.start()
        else:
            self.playByPlayInterval = pbpText.getShowIntervalDesc("Legally Bound Toons take 20 damage per round!", attackDuration)
            self.playByPlayInterval.start()

    def checkPlayByPlayTextLiquidationEvent(self, pbpText, attackDuration):
        if self.playByPlayInterval != None:
            self.playByPlayInterval.finish()
           # del self.playByPlayInterval
        pbpText = pbpText
        if self.isDesperation:
            self.playByPlayInterval = pbpText.getShowIntervalDesc("Liquidated Toons take 42 extra damage per round!", attackDuration)
            self.playByPlayInterval.start()
        else:
            self.playByPlayInterval = pbpText.getShowIntervalDesc("Liquidated Toons take 30 extra damage per round!", attackDuration)
            self.playByPlayInterval.start()

    def checkPlayByPlayTextCourtRecord(self, pbpText, attackDuration):
        if self.playByPlayInterval != None:
            self.playByPlayInterval.finish()
            #del self.playByPlayInterval
        pbpText = pbpText
        if self.isDesperation:
            self.playByPlayInterval = pbpText.getShowIntervalDesc('Due to an illegal action, this toon takes 70 damage!', attackDuration)
            self.playByPlayInterval.start()
        else:
            self.playByPlayInterval = pbpText.getShowIntervalDesc('Due to an illegal action, this toon takes 50 damage!', attackDuration)
            self.playByPlayInterval.start()

    def checkPlayByPlayTextBurned(self, pbpText, attackDuration):
        if self.playByPlayInterval != None:
            self.playByPlayInterval.finish()
           # del self.playByPlayInterval
        pbpText = pbpText
        if self.isDesperation:
            self.playByPlayInterval = pbpText.getShowIntervalDesc('Burned Toons take 42 extra damage per round!', attackDuration)
            self.playByPlayInterval.start()
        else:
            self.playByPlayInterval = pbpText.getShowIntervalDesc('Burned Toons take 30 extra damage per round!', attackDuration)
            self.playByPlayInterval.start()

    def checkPlayByPlayTextInflation(self, pbpText, attackDuration):
        if self.playByPlayInterval != None:
            self.playByPlayInterval.finish()
            #del self.playByPlayInterval
        pbpText = pbpText
        if self.isDesperation:
            self.playByPlayInterval = pbpText.getShowIntervalDesc("Due to an overinflated budget this toon takes 70 damage!", attackDuration)
            self.playByPlayInterval.start()
        else:
            self.playByPlayInterval = pbpText.getShowIntervalDesc("Due to an overinflated budget this toon takes 50 damage!", attackDuration)
            self.playByPlayInterval.start()

    def checkPlayByPlayTextBusted(self, pbpText, attackDuration):
        if self.playByPlayInterval != None:
            self.playByPlayInterval.finish()
           # del self.playByPlayInterval
        pbpText = pbpText
        if self.isDesperation:
            self.playByPlayInterval = pbpText.getShowIntervalDesc('Employed Toons are forced to take 35 damage every round!', attackDuration)
            self.playByPlayInterval.start()
        else:
            self.playByPlayInterval = pbpText.getShowIntervalDesc('Employed Toons are forced to take 25 damage every round!', attackDuration)
            self.playByPlayInterval.start()

    def checkCogHP(self, battle):
        if self.deathInterval != None:
            self.deathInterval = None
        elif self.getHP() <= 0 and self.deathInterval == None:
            self.deathInterval = Sequence(MovieUtil.createSuitDeathTrack(self, battle), Func(battle.unlureSuit, self))
            self.deathInterval.start()
        else:
            pass

    def checkCogDeath(self, battle):
        if self.deathInterval != None:
            self.deathInterval.finish()
          #  del self.deathInterval
        if self.getHP() <= 0:
            self.deadSuits.append(self)
        else:
            pass

    def checkHealingPhrases(self, num):
        if self.deathInterval != None:
            self.deathInterval = None
        if self.getHP() > 0 and num == 0:
            self.deathInterval = Sequence(Func(self.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout))
            self.deathInterval.start()
        elif self.getHP() > 0 and num == 1:
            self.deathInterval = Sequence(Func(self.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitMarkedPhrases), CFSpeech | CFTimeout))
            self.deathInterval.start()
        elif self.getHP() > 0 and num == 2:
            self.deathInterval = Sequence(Func(self.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitContractedPhrases), CFSpeech | CFTimeout))
            self.deathInterval.start()
        elif self.getHP() > 0 and num == 3 and (not self.getDizzy() or self.getLuredRounds() == 0):
            self.deathInterval = Sequence(Func(self.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitSyphonPhrases), CFSpeech | CFTimeout))
            self.deathInterval.start()
        else:
            pass

    def checkCogHPDrop(self, battle):
        if self.deathInterval != None:
            self.deathInterval = None
        elif self.getHP() <= 0 and self.deathInterval == None:
            self.deathInterval = Sequence(MovieUtil.createSuitCrashTrack(self, battle, 7))
            self.deathInterval.start()
        else:
            pass

    def checkAbsorbHP(self, battle):
        if self.deathInterval != None:
            self.deathInterval = None
        elif self.getHP() <= 0:
            self.deathInterval = Sequence(Func(self.makeDead))
            self.deathInterval.start()
        else:
            pass

    def checkCogHPBomb(self, battle):
        if self.deathInterval != None:
            self.deathInterval = None
        elif self.getHP() <= 0 and self.deathInterval == None and not self.isDead:
            self.deathInterval = Sequence(MovieUtil.shortCircuitTrack(self, battle), Func(battle.unlureSuit, self))
            self.deathInterval.start()
        else:
            pass

    def checkCogHPZap(self, battle):
        if self.getHP() <= 0:
            self.deathInterval = Sequence(MovieUtil.shortCircuitTrack(self, battle), Func(battle.unlureSuit, self))
            self.deathInterval.start()
        else:
            pass

    def checkCogHPLaserRevive(self, battle):
        if self.deathInterval != None:
            self.deathInterval = None
        elif self.getHP() <= 0 and self.deathInterval == None:
            self.deathInterval = Sequence(MovieUtil.createSuitReviveTrackVirtual(self, battle), Func(battle.unlureSuit, self))
            self.deathInterval.start()
        else:
            pass

    def checkCogHPLaser(self, battle):
        if self.deathInterval != None:
            self.deathInterval = None
        elif self.getHP() <= 0 and self.deathInterval == None:
            self.deathInterval = Sequence(MovieUtil.createVirtualSuitDeathTrack(self, battle), Func(battle.unlureSuit, self))
            self.deathInterval.start()
        else:
            pass

    def checkCogHPRevive(self, battle):
        if self.deathInterval != None:
            self.deathInterval = None
        elif self.getHP() <= 0 and self.deathInterval == None:
            self.deathInterval = Sequence(MovieUtil.createSuitReviveTrack(self, battle), Func(battle.unlureSuit, self))
            self.deathInterval.start()
        else:
            pass

    def addAbsorbDamage(self, absorbingCog, damage):
        absorbingCog.absorbDamage += damage

    def removeAbsorbDamage(self):
        self.absorbDamage  = 0

    def addFraudulentDamage(self, absorbingCog, damage):
        absorbingCog.fraudulentDamage += damage

    def removeFraudulentDamage(self):
        self.fraudulentDamage  = 0

    def addSyphonHP(self, absorbingCog, damage):
        absorbingCog.syphonHP += damage

    def removeSyphonHP(self):
        self.syphonHP  = 0

    def checkSyphonHP(self, syphonHp):
        hpCap = int(self.maxHP * self.hardMaxHP)

        projectedHP = self.getQueuedProjectedHPFull()

        healAmount = min(syphonHp, max(0, hpCap - projectedHP))

        if healAmount > 0:
            self.addPendingQueuedHealing(healAmount)

        return Sequence(
            Parallel(
                Func(self.showHpTextNew, healAmount, text="SYPHONED!", colorCode=1),
                Func(self.setHealthForMe, healAmount),
                Func(self.updateHealthBar, 0)
            )
        )

    def personalTrainer(self):
        x = int(self.maxHP * .1)
        self.absorbInterval = Sequence(
                Parallel(Func(self.showHpTextNew, - x),
                         Func(self.setHealthForMe, - x),
                         Func(self.updateHealthBar, 0))).start()
        self.addPendingQueuedDamage(self.maxHP * .1)

    def checkSyphonHPErclaim(self, syphonHp):
        hpCap = int(self.maxHP * self.hardMaxHP)

        projectedHP = self.getQueuedProjectedHPFull()

        healAmount = min(syphonHp, max(0, hpCap - projectedHP))

        if healAmount > 0:
            self.addPendingQueuedHealing(healAmount)

        return Sequence(
            Parallel(
                Func(self.showHpTextNew, + healAmount),
                Func(self.setHealthForMe, + healAmount),
                Func(self.updateHealthBar, 0)
            )
        )

    def addLevelDamage(self, absorbingCog, damage):
        absorbingCog.levelDamage += damage

    def removeLevelDamage(self):
        self.levelDamage = 0

    def addRPMIncrease(self, damage):
        self.rpmIncrease2 += damage

    def addRPM(self, dmg):
        self.damageInterval = Parallel(Func(self.setRPM, self.getRPM() + self.getRPMIncrease() + dmg)).start()

    def addRPMWhipsaw(self):
        self.damageInterval = Parallel(Func(self.setRPM, self.getRPM() + (self.getRPMIncrease() + 4))).start()

    def removeRPM(self, damage):
        self.damageInterval = Parallel(Func(self.setRPM, self.getRPM() - damage)).start()

    def addRageBuilding(self, damage):
        self.damageInterval = Parallel(Func(self.setRageBuilding, damage)).start()

    def removeRageBuilding(self):
        self.damageInterval = Parallel(Func(self.setRageBuilding, 0)).start()

    def addPowerhouseRotation(self, damage):
        self.damageInterval = Parallel(Func(self.setPowerhouseRotation, damage)).start()

    def addStormCellDamage(self):
        self.damageInterval = Parallel(Func(self.removeStormCellDamage, self.getStormCellDamage() - 6)).start()

    def addStormCellDamageReverse(self):
        self.damageInterval = Parallel(Func(self.removeStormCellDamage, 60)).start()

    def addHeavyRainDamage(self, damage):
        self.damageInterval = Parallel(Func(self.addHeavyRainDamageReal, self.getHeavyRainDamage() + int(damage))).start()

    def removeHeavyRainDamage(self):
        self.damageInterval = Parallel(Func(self.addHeavyRainDamage, 0)).start()

    def removePowerhouseRotation(self):
        self.damageInterval = Parallel(Func(self.setPowerhouseRotation, 0)).start()


    def checkAbsorbDamage(self, absorbDamage):
        if self.dna.name == 'sgoat':
            self.absorbInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'),
                                         Func(self.showHpTextNew, - absorbDamage, text="ABSORBED!", colorCode=1), Func(self.setHealthForMe, - absorbDamage),
                                         Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimationDrop), Func(self.addRageBuilding, int(absorbDamage)),
                                           Func(self.removeAbsorbDamage)).start()
        else:
            self.absorbInterval = Sequence(
                Parallel(ActorInterval(self, 'pie-small-react'), 
                         Func(self.showHpTextNew, - absorbDamage, text="ABSORBED!", colorCode=1),
                         Func(self.setHealthForMe, - absorbDamage),
                         Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimationDrop),
                Func(self.removeAbsorbDamage)).start()

    def checkFraudulentDamage(self):
        self.absorbInterval = Sequence(
                Parallel(ActorInterval(self, 'pie-small-react'), 
                         Func(self.showHpTextNew, - 158),
                         Func(self.setHealthForMe, - 158),
                         Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimationDrop)).start()

    def checkLevelDamage(self, levelDamage):
        if self.dna.name == 'hroller':
            if float(self.currHP) < levelDamage:
                x = int(self.currHP - 1)
                self.absorbInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'),
                                         Func(self.showHpText, - x), Func(self.setHealthForMe, - x),
                                         Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimationDrop),
                                           Func(self.removeLevelDamage)).start()
            else:
                self.absorbInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'), 
                                                        Func(self.showHpText, - levelDamage), Func(self.setHealthForMe, - levelDamage),
                                                        Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimationDrop),
                                               Func(self.removeLevelDamage)).start()
        else:
            self.absorbInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'), 
                                                    Func(self.showHpText, - levelDamage), Func(self.setHealthForMe, - levelDamage),
                                                    Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimationDrop),
                                           Func(self.removeLevelDamage)).start()

    def checkDamage(self, levelDamage):
        if self.dna.name == 'safesupervis':
            self.absorbInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'),
                                         Func(self.showHpTextNew, - levelDamage, text="OVERHEATED!", colorCode=5), Func(self.setHealthForMe, - levelDamage),
                                         Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimationDrop),
                                           Func(self.removeLevelDamage)).start()
        else:
            self.absorbInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'),
                                                    Func(self.showHpText, - levelDamage), Func(self.setHealthForMe, - levelDamage),
                                                    Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimationDrop),
                                           Func(self.removeLevelDamage)).start()

    def checkDamage2(self, levelDamage):
        self.absorbInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'),
                                                    Func(self.showHpText, - levelDamage), Func(self.setHealthForMe, - levelDamage),
                                                    Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimationDrop),
                                           Func(self.removeLevelDamage)).start()

    def checkCogOvercharge(self):
        if float(self.currHP) > float(self.maxHP * 1.5):
            self.isOvercharged = 1
        else:
            self.isOvercharged = 0

    def checkAutoRepair(self):
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP >= (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="REPAIRED!", colorCode=1),
                                         Func(self.updateHealthBar, 0)).start()
        elif self.currHP + (self.maxHP * 0.35) > (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, x, text="REPAIRED!", colorCode=1),
                                         Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
            self.addPendingQueuedHealing(x)
        else:
            self.healInterval = Parallel(Func(self.showHpTextNew, int(self.maxHP * 0.35), text="REPAIRED!", colorCode=1),
                                         Func(self.setHealthForMe, int(self.maxHP * 0.35)), Func(self.updateHealthBar, 0)).start()
            self.addPendingQueuedHealing(self.maxHP * 0.35)

    def soakSuit(self, drench=0, oilRain=0):
        if oilRain:
            color = OilColor
        elif drench or self.hasSuitStatusEffect('drenched'):
            color = DrenchColor
        else:
            color = SoakColor
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        parts = ()
        for thingIndex in xrange(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_shadow', 'joint_nameTag', 'def_nameTag'):
                if not self.dna.name == 'cbutcher' and not self.isShadow:
                    thing.setColor(color)
        if not self.isSkeleton and not self.isShadow:
            hands = self.find('**/hands')
            handTint = Vec4(
                self.handColor[0] * color[0],
                self.handColor[1] * color[1],
                self.handColor[2] * color[2],
                self.handColor[3] * color[3]
            )
            hands.setColorScale(handTint)
        if self.dna.name == 'lgator' and not self.isSkeleton:
            self.makeWetLitigator()
        if self.dna.name == 'treasure' and not self.isSkeleton:
            self.makeWetTreasurer()
        if self.style.name == 'safesupervis' and not self.isSkeleton:
            self.makeWetFirestarter()
        if self.style.name == 'fires' and not self.isSkeleton:
            self.makeWetFirestarter()

    def __soakRemoval(self, remove=0):
        if remove:
            if self.style.name == 'hydra':
                color = Point4((0.729, 0.729, 0.729, 1))
            elif self.style.name == 'charon':
                color = Point4((0.51, 0.49, 0.467, 1))
            elif self.style.name == 'nix':
                color = Point4((0.6, 0.6, 0.6, 1))
            elif self.style.name == 'styx':
                color = Point4((0.671, 0.671, 0.671, 1))
            elif self.style.name == 'kerberos':
                color = Point4((0.62, 0.659, 0.624, 1))
            elif self.style.name == 'cbutcher':
                color = Point4((0, 0, 0, 1))
            else:
                color = Point4(1.0, 1.0, 1.0, 1.0)
        else:
            color = SoakColor
        suitInterval = Parallel()
        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
        parts = ()
        for thingIndex in xrange(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            if thing.getName() not in ('joint_attachMeter', 'joint_shadow', 'joint_nameTag', 'def_nameTag'):
                if not self.dna.name == 'cbutcher' and not self.isShadow:
                    suitInterval.append(Func(thing.setColor, Point4(1.0, 1.0, 1.0, 1.0)))
        if not self.isSkeleton and not self.isShadow:
            hands = self.find('**/hands')
            suitInterval.append(Func(hands.setColorScale, self.handColor))
        if self.dna.name == 'lgator' and not self.isSkeleton:
            suitInterval.append(Func(self.makeDryLitigator))
        if self.dna.name == 'treasure' and not self.isSkeleton:
            suitInterval.append(Func(self.makeDryTreasurer))
        if self.style.name == 'safesupervis' and not self.isSkeleton:
            suitInterval.append(Func(self.makeDryFirestarter))
        if self.style.name == 'fires' and not self.isSkeleton:
            suitInterval.append(Func(self.makeDryFirestarter))
        self.healInterval =  Parallel(suitInterval).start()

    def addPendingQueuedDamage(self, dmg):
        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        self._pendingQueuedDamage += int(dmg)
        if self._pendingQueuedDamage < 0:
            self._pendingQueuedDamage = 0

    def clearPendingQueuedDamageAll(self):
        self._pendingQueuedDamage = 0
        self._pendingQueuedDeath = False

    def clearPendingQueuedDamage(self, dmg):
        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        self._pendingQueuedDamage -= int(dmg)
        if self._pendingQueuedDamage < 0:
            self._pendingQueuedDamage = 0

    def getQueuedProjectedHP(self):
        pending = getattr(self, '_pendingQueuedDamage', 0)
        return self.currHP - pending

    def getPendingQueuedDeath(self):
        return getattr(self, '_pendingQueuedDeath', False)

    def setPendingQueuedDeath(self, value):
        self._pendingQueuedDeath = bool(value)

    def _appendQueuedDeathOrRevive(self, suitTrack, projectedHP, battle):
        if projectedHP > 0 or self.isDead:
            return

        revives = self.getSkeleRevives()
        #suitTrack.append(self.makeCogStepBackDeathInterval(battle))

        if self.dna.name == 'redd' and not self.isVirtual:
            suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            suitTrack.append(Func(self.makeDead))
        elif self.isVirtual:
            suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            suitTrack.append(Func(self.makeDead))
        elif not self.isSkeleton and revives >= 2:
            suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
        elif self.isSkeleton and revives >= 2:
            suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
        elif self.isSkeleton and revives >= 1 and not self.isRevive:
            suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
        elif not self.isSkeleton and revives >= 1:
            suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
        elif not self.isVirtual:
            suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
            suitTrack.append(Func(self.makeDead))

    def makeCommercialBreakInterval(self, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        if not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            suitTrack.append(MovieUtil.shortCircuitTrack(self, battle))
            suitTrack.append(Func(self.makeDead))
        return suitTrack

    def makeHighPressureDeathMovie(self, hp, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        dmg = int(math.ceil(hp))
        if dmg <= 0:
            return suitTrack

        # Build-time pending splash state
        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)
        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            suitTrack.append(MovieUtil.shortCircuitTrack(self, battle))
            suitTrack.append(Func(self.makeDead))
        return suitTrack
    
    def makeDeathCheckInterval(self, dmg, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        # Build-time pending splash state
        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)
        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            #suitTrack.append(self.makeCogStepBackDeathInterval(battle))

            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))

        return suitTrack


    def makeSplashAndDeathInterval(self, tContact, hp, battle, bonus, attackTrack, level, drench, 
                                   reactName='squirt-small-react'):
        suitTrack = Sequence()

        if int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) <= 0 or self.isDead and not self.getProjectedRevive():
            return suitTrack

        dmg = int(math.ceil(hp))
        if dmg <= 0:
            return suitTrack

        # Build-time pending splash state
        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)

        if drench:
            if self.dna.name == 'redd':
                soakText = "DRENCHED 2 ROUNDS"
                soakRounds = 2
            elif self.isVirtual:
                soakText = "DRENCHED 2 ROUNDS"
                soakRounds = 2
            elif self.isSkeleton:
                soakText = "DRENCHED 3 ROUNDS"
                soakRounds = 3
            else:
                soakText = "DRENCHED 4 ROUNDS"
                soakRounds = 4

            # if self.squirtRushJob:
            #     self.makeUnSquirtRushJob()
        
            showDamage = Parallel(
                Func(self.showHpTextNew, -dmg, text=soakText, attackTrack=attackTrack, colorCode=1),
                Func(self.setHealthForMe, -dmg),
                Func(self.updateHealthBar, 0),
                Func(self.setSuitStatusEffect, 'drenched', modifier=1, turns=soakRounds)
            )
        else:
            if self.dna.name == 'redd':
                soakText = "SOAKED 2 ROUNDS"
                soakRounds = 2
            elif self.isVirtual:
                soakText = "SOAKED 2 ROUNDS"
                soakRounds = 2
            elif self.isSkeleton:
                soakText = "SOAKED 3 ROUNDS"
                soakRounds = 3
            else:
                soakText = "SOAKED 4 ROUNDS"
                soakRounds = 4

            # if self.squirtRushJob:
            #     self.makeUnSquirtRushJob()
        
            showDamage = Parallel(
                Func(self.showHpTextNew, -dmg, text=soakText, attackTrack=attackTrack, colorCode=1),
                Func(self.setHealthForMe, -dmg),
                Func(self.updateHealthBar, 0),
                Func(self.setSuitStatusEffect, 'soaked', modifier=1, turns=soakRounds)
            )

        reactTrack = Parallel(
            ActorInterval(self, reactName),
        )

        suitTrack.append(showDamage)
        suitTrack.append(reactTrack)

        # if self.dna.name == 'sgoat' and self.isShielding:
        #     suitTrack.append(Func(self.addRageBuilding, dmg + 150))
        # if self.dna.name == 'phouse':
        #     suitTrack.append(Func(self.addPowerhouseRotation, dmg + 150))
        # if self.isSued:
        #     suitTrack.append(Func(self.makeSued, 3))

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead and not self.hasSuitStatusEffect('overpressured'):
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()

            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
        else:
            suitTrack.append(Func(self.setNeutralAnimationDrop))

        def _clearPendingSplash():
            if hasattr(self, '_pendingSplashDamage'):
                self._pendingSplashDamage -= dmg
                if self._pendingSplashDamage < 0:
                    self._pendingSplashDamage = 0

                if self._pendingSplashDamage == 0:
                    self._pendingSplashDeathQueued = False

        suitTrack.append(Func(_clearPendingSplash))

        return suitTrack


    def checkSplashDamage(self, tContact, hp, battle, bonus, attackTrack, level):
        if self.currHP > 0:
            if self.splashInterval:
                self.splashInterval.finish()
                self.splashInterval = None

            dmg = int(math.floor(hp))
            suitTrack = Sequence()
            updateHealthBar = Func(self.updateHealthBar, dmg)

            if self.dna.name == 'redd':
                showDamage = Parallel(
                    Func(self.showHpTextNew, -dmg, text="SOAKED 1 ROUND", attackTrack=attackTrack, colorCode=1),
                    Func(self.setHealthForMe, -dmg),
                    updateHealthBar
                )
                soakSuit = Func(self.makeSoaked, 1)
            elif self.isVirtual:
                showDamage = Parallel(
                    Func(self.showHpTextNew, -dmg, text="SOAKED 2 ROUNDS", attackTrack=attackTrack, colorCode=1),
                    Func(self.setHealthForMe, -dmg),
                    updateHealthBar
                )
                soakSuit = Func(self.makeSoaked, 1)
            elif self.isSkeleton:
                showDamage = Parallel(
                    Func(self.showHpTextNew, -dmg, text="SOAKED 3 ROUNDS", attackTrack=attackTrack, colorCode=1),
                    Func(self.setHealthForMe, -dmg),
                    updateHealthBar
                )
                soakSuit = Func(self.makeSoaked, 2)
            else:
                showDamage = Parallel(
                    Func(self.showHpTextNew, -dmg, text="SOAKED 4 ROUNDS", attackTrack=attackTrack, colorCode=1),
                    Func(self.setHealthForMe, -dmg),
                    updateHealthBar
                )
                soakSuit = Func(self.makeSoaked, 3)

            suitTrack.append(Func(self.setSoaked, 1))
            suitTrack.append(Parallel(showDamage, soakSuit))
            suitTrack.append(Func(self.setNeutralAnimationDrop))

            if self.dna.name == 'sgoat' and self.isShielding:
                suitTrack.append(Func(self.addRageBuilding, dmg + 150))
            if self.dna.name == 'phouse':
                suitTrack.append(Func(self.addPowerhouseRotation, dmg + 150))
            if self.isSued:
                suitTrack.append(Func(self.makeSued, 3))

            self.splashInterval = Sequence(suitTrack).start()

    def createStagelightInterval(self, show=False):
        hiddenParts = []
        for headPart in self.headParts:
            if not headPart.isHidden():
                headPart.hide()
                hiddenParts.append(headPart)
            if show == True:
                hiddenParts.show()

    def createSuitBellInterval(self):
        if self.style.name == 'liquid':
            for headPart in self.animatedHeadParts:
                headInterval = Sequence(ActorInterval(headPart, 'healing-bell'), Func(self.setNeutralAnimationHead))
                hasAnimatedHead = True
                Parallel(headInterval).start()

    def createSuitComeOnInterval(self):
        if self.style.name == 'hustle':
            for headPart in self.animatedHeadParts:
                headInterval = Sequence(ActorInterval(headPart, 'come-on'), Func(self.setNeutralAnimationHead))
                hasAnimatedHead = True
                Parallel(headInterval).start()

    def createSuitBellowInterval(self):
        if self.style.name == 'lgator' or self.style.name == 'treasure' or self.style.name == 'clubpres':
            suitInterval = Sequence(ActorInterval(self, 'bellow'), Func(self.setNeutralAnimation))
            for headPart in self.animatedHeadParts:
                headInterval = Sequence(ActorInterval(headPart, 'bellow'), Func(self.setNeutralAnimation))
                hasAnimatedHead = True
                Parallel(headInterval, suitInterval).start()

    def createSuitStunInterval(self):
        hasAnimatedHead = False
        # if self.headInterval:
        #     self.headInterval.finish()
        #     self.headInterval = None
        for headPart in self.animatedHeadParts:
            self.headInterval = Sequence(Func(headPart.loop, 'stun'))
            hasAnimatedHead = True
        if hasAnimatedHead:
            self.headInterval.start()
        else:
            pass

    def createSuitRevvingUpInterval(self):
        if self.style.name == 'cbutcher':
            suitInterval = Sequence(ActorInterval(self, 'revvedup'), Func(self.setNeutralAnimation))
            for headPart in self.animatedHeadParts:
                headInterval = Sequence(ActorInterval(headPart, 'revvedup'), Func(self.setNeutralAnimation))
                hasAnimatedHead = True
                Parallel(headInterval, suitInterval).start()

    def createSuitSparkPlugInterval(self):
        if self.style.name == 'cbutcher':
            suitInterval = Sequence(ActorInterval(self, 'sparkplug', Func(self.setNeutralAnimation)))
            for headPart in self.animatedHeadParts:
                headInterval = Sequence(ActorInterval(headPart, 'sparkplug'), Func(self.setNeutralAnimation))
                hasAnimatedHead = True
                Parallel(headInterval, suitInterval).start()

    def createSuitScabbardInterval(self):
        if self.style.name == 'cbutcher':
            suitInterval = Sequence(ActorInterval(self, 'scabbard'), Func(self.setNeutralAnimation))
            for headPart in self.animatedHeadParts:
                headInterval = Sequence(ActorInterval(headPart, 'scabbard'), Func(self.setNeutralAnimation))
                hasAnimatedHead = True
                Parallel(headInterval, suitInterval).start()

    def createSuitSnapInterval(self):
        if self.style.name == 'lgator' or self.style.name == 'treasure':
            suitInterval = Sequence(ActorInterval(self, 'snap2'), Func(self.setNeutralAnimationDrop))
            for headPart in self.animatedHeadParts:
                headInterval = Sequence(ActorInterval(headPart, 'gsnap'), Func(self.setNeutralAnimationHead))
                hasAnimatedHead = True
                Parallel(headInterval, suitInterval).start()

    def decrementDrenchRound(self):
        if self.splashInterval:
            self.splashInterval.finish()
            self.splashInterval = None
        self.splashInterval = Parallel(Func(self.setSuitStatusEffect, 'drenched', turns=self.getSuitStatusTurns('drenched') - 1)).start()

    def checkSoakRounds(self):
        if self.splashInterval:
            self.splashInterval.finish()
            self.splashInterval = None
        if (self.isSoaked == 0 and self.actuallySoaked and not self.isDead) or self.dna.name == 'phouse' and self.currHP > 0:
            if self.dna.name == 'safesupervis':
                self.splashInterval = Sequence(Parallel(Func(self.makeUnDamageDown), Func(self.checkDamageDown, - 25), ActorInterval(self, 'soak', startTime=3.5), Sequence(Wait(1.0), Func(self.__soakRemoval, 1))), Func(self.makeUnSoaked), Func(self.setNeutralAnimationDrop)).start()
            else:
                self.splashInterval = Sequence(Parallel(ActorInterval(self, 'soak', startTime=3.5),  Sequence(Wait(1.0), Func(self.__soakRemoval, 1))), Func(self.makeUnSoaked), Func(self.setNeutralAnimationDrop)).start()

    def checkMarkRounds(self):
        if self.splashInterval:
            self.splashInterval.finish()
            self.splashInterval = None
        if self.isMarked == 0 and self.actuallyMarked and not self.isDead and self.currHP > 0:
            self.splashInterval = Sequence(Parallel(ActorInterval(self, 'squirt-small-react', startTime=2.25), Sequence(Wait(1.0), Func(self.splatSuit, 0, 1)), Func(self.makeUnMarked)), Func(self.setNeutralAnimationDrop)).start()

    def checkContractEnforcement(self):
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        if self.currHP >= (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="CONTRACTED!", colorCode=1),
                                         Func(self.updateHealthBar, 0)).start()
        elif self.currHP + 95 > (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, x, text="CONTRACTED!", colorCode=1),
                                         Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
        else:
            self.healInterval = Parallel(Func(self.showHpTextNew, 95, text="CONTRACTED!", colorCode=1),
                                         Func(self.setHealthForMe, 95), Func(self.updateHealthBar, 0)).start()
            
    def checkPayrollProcessing(self):
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        if self.currHP >= (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, 0),
                                         Func(self.updateHealthBar, 0)).start()
        elif self.currHP + 95 > (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, x),
                                         Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
            self.addPendingQueuedHealing(x)
        else:
            self.healInterval = Parallel(Func(self.showHpTextNew, 95),
                                         Func(self.setHealthForMe, 95), Func(self.updateHealthBar, 0)).start()
            self.addPendingQueuedHealing(95)

    def checkPerformanceReview(self):
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        if not self.isManager:
            self.healInterval = Parallel(Func(self.showHpTextNew, x, text="OVERCHARGED!", colorCode=5),
                                         Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
        else:
            self.healInterval = Parallel(Func(self.showHpTextNew, 750, text="HEALED!", colorCode=1),
                                         Func(self.setHealthForMe, 750), Func(self.updateHealthBar, 0)).start()

    def checkContractEnforcementSafety(self):
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        if self.currHP >= (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="CONTRACTED!", colorCode=1),
                                         Func(self.updateHealthBar, 0)).start()
        elif self.currHP + 200 > (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, x, text="CONTRACTED!", colorCode=1),
                                         Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
        else:
            self.healInterval = Parallel(Func(self.showHpTextNew, 200, text="CONTRACTED!", colorCode=1),
                                         Func(self.setHealthForMe, 200), Func(self.updateHealthBar, 0)).start()

    def checkRefinement(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        if self.getManager():
            if self.currHP > 0:
                x = int((self.maxHP * self.hardMaxHP) - self.currHP)
                if self.currHP >= (self.maxHP * self.hardMaxHP):
                    self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="REFINED!", colorCode=1),
                                                 Func(self.updateHealthBar, 0)).start()
                elif self.currHP + 200 > (self.maxHP * self.hardMaxHP):
                    self.healInterval = Parallel(Func(self.showHpTextNew, x, text="REFINED!", colorCode=1),
                                                 Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
                else:
                    self.healInterval = Parallel(Func(self.showHpTextNew, 200, text="REFINED!", colorCode=1),
                                                 Func(self.setHealthForMe, 200), Func(self.updateHealthBar, 0)).start()
        else:
            if self.currHP > 0:
                x = int((self.maxHP * self.hardMaxHP) - self.currHP)
                if self.currHP >= (self.maxHP * self.hardMaxHP):
                    self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="REFINED!", colorCode=1),
                                                 Func(self.updateHealthBar, 0)).start()
                elif self.currHP + 175 > (self.maxHP * self.hardMaxHP):
                    self.healInterval = Parallel(Func(self.showHpTextNew, x, text="REFINED!", colorCode=1),
                                                 Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
                else:
                    self.healInterval = Parallel(Func(self.showHpTextNew, 175, text="REFINED!", colorCode=1),
                                                 Func(self.setHealthForMe, 175), Func(self.updateHealthBar, 0)).start()

    def checkRefinementManager(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP >= (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="REFINED!", colorCode=1),
                                         Func(self.updateHealthBar, 0)).start()
        elif self.currHP + 200 > (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, x, text="REFINED!", colorCode=1),
                                         Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
        else:
            self.healInterval = Parallel(Func(self.showHpTextNew, 200, text="REFINED!", colorCode=1),
                                         Func(self.setHealthForMe, 200), Func(self.updateHealthBar, 0)).start()

    def checkRefinementDerrickMan(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP >= (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="REFINED!", colorCode=1),
                                         Func(self.updateHealthBar, 0)).start()
        elif self.currHP + (self.maxHP * 0.4) > (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, x, text="REFINED!", colorCode=1),
                                         Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
        else:
            self.healInterval = Parallel(Func(self.showHpTextNew, int(math.ceil(self.maxHP * 0.4)), text="REFINED!", colorCode=1),
                                         Func(self.setHealthForMe, int(math.ceil(self.maxHP * 0.4))), Func(self.updateHealthBar, 0)).start()

    def checkRefinementPowerhouseManager(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP >= (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="REFINED!", colorCode=1),
                                         Func(self.updateHealthBar, 0)).start()
        elif self.currHP + 350 > (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, x, text="REFINED!", colorCode=1),
                                         Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
        else:
            self.healInterval = Parallel(Func(self.showHpTextNew, 350, text="REFINED!", colorCode=1),
                                         Func(self.setHealthForMe, 350), Func(self.updateHealthBar, 0)).start()

    def checkCameraRewind(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP < self.maxHP and not self.currHP <= 0:
            if self.currHP >= (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="REWIND!", colorCode=1),
                                             Func(self.updateHealthBar, 0)).start()
            elif self.currHP + 125 > (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, x, text="REWIND!", colorCode=1),
                                             Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
            else:
                self.healInterval = Parallel(Func(self.showHpTextNew, 125, text="REWIND!", colorCode=1),
                                             Func(self.setHealthForMe, 125), Func(self.updateHealthBar, 0)).start()
        else:
            self.healInterval = Sequence(Parallel(Func(self.showHpString, "+10% Damage!"), Func(self.setSuitStatusEffect, 'damageUp', modifier=10, mode='refreshModifier'))).start()

    def checkRefinementPowerhouse(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        if self.getManager():
            if self.healInterval:
                self.healInterval.finish()
                self.healInterval = None
            x = int((self.maxHP * self.hardMaxHP) - self.currHP)
            if self.currHP >= (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="REFINED!", colorCode=1),
                                             Func(self.updateHealthBar, 0)).start()
            elif self.currHP + 350 > (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, x, text="REFINED!", colorCode=1),
                                             Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
            else:
                self.healInterval = Parallel(Func(self.showHpTextNew, 350, text="REFINED!", colorCode=1),
                                             Func(self.setHealthForMe, 350), Func(self.updateHealthBar, 0)).start()
        else:
            x = int((self.maxHP * self.hardMaxHP) - self.currHP)
            if self.currHP >= (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="REFINED!", colorCode=1),
                                             Func(self.updateHealthBar, 0)).start()
            elif self.currHP + 275 > (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, x, text="REFINED!", colorCode=1),
                                             Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
            else:
                self.healInterval = Parallel(Func(self.showHpTextNew, 275, text="REFINED!", colorCode=1),
                                             Func(self.setHealthForMe, 275), Func(self.updateHealthBar, 0)).start()
                
    def checkTribute(self, racketeer, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        self.damageInterval = Sequence(Parallel(
                                                    Func(self.showHpTextNew, -int(math.ceil(self.currHP * .1))),
                                                  Func(self.setHealthForMe, -int(math.ceil(self.currHP * .1))),
                                                  Func(self.updateHealthBar, 0)),
                                         Func(self.setNeutralAnimationDrop)).start()
        self.healInterval = Sequence(Parallel(Func(racketeer.showHpTextNew, +int(math.ceil(self.currHP * .1) * 4)), 
                                                   Func(racketeer.setHealthForMe, +int(math.ceil(self.currHP * .1) * 4)),
                                                   Func(racketeer.updateHealthBar, 0)),
                               Func(racketeer.setNeutralAnimationDrop)).start()
        
    def checkUsury(self, racketeer, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        if self.currHP < int(math.ceil(self.maxHP / 3)):
            self.damageInterval = Sequence(Parallel(
                                                   Func(self.showHpTextNew, x),
                                                   Func(self.setHealthForMe, -x),
                                                   Func(self.updateHealthBar, 0)),
                               Func(self.setNeutralAnimationDrop)).start()
            self.healInterval = Sequence(Parallel(Func(racketeer.showHpTextNew, +x),
                                                  Func(racketeer.setHealthForMe, +x),
                                                  Func(racketeer.updateHealthBar, 0)),
                                         Func(racketeer.setNeutralAnimationDrop)).start()
        else:
            self.damageInterval = Sequence(Parallel(
                                                    Func(self.showHpTextNew, -int(math.ceil(self.maxHP / 3))),
                                                  Func(self.setHealthForMe, -int(math.ceil(self.maxHP / 3))),
                                                  Func(self.updateHealthBar, 0)),
                                         Func(self.setNeutralAnimationDrop)).start()
            self.healInterval = Sequence(Parallel(Func(racketeer.showHpTextNew, +int(math.ceil(self.maxHP / 3))), 
                                                   Func(racketeer.setHealthForMe, +int(math.ceil(self.maxHP / 3))),
                                                   Func(racketeer.updateHealthBar, 0)),
                               Func(racketeer.setNeutralAnimationDrop)).start()

    def checkProfiteering(self, racketeer, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        if self.currHP < int(math.ceil(self.maxHP / 2)):
            self.damageInterval = Sequence(Parallel(
                                                   Func(self.showHpTextNew, x),
                                                   Func(self.setHealthForMe, -x),
                                                   Func(self.updateHealthBar, 0)),
                               Func(self.setNeutralAnimationDrop)).start()
            self.healInterval = Sequence(Parallel(Func(racketeer.showHpTextNew, +x, text="SYPHONED!", colorCode=1),
                                                  Func(racketeer.setHealthForMe, +x),
                                                  Func(racketeer.updateHealthBar, 0)),
                                         Func(racketeer.setNeutralAnimationDrop)).start()
        else:
            self.damageInterval = Sequence(Parallel(
                                                    Func(self.showHpTextNew, -int(math.ceil(self.maxHP / 2))),
                                                  Func(self.setHealthForMe, -int(math.ceil(self.maxHP / 2))),
                                                  Func(self.updateHealthBar, 0)),
                                         Func(self.setNeutralAnimationDrop)).start()
            self.healInterval = Sequence(Parallel(Func(racketeer.showHpTextNew, +int(math.ceil(self.maxHP / 2)), text="SYPHONED!", colorCode=1), 
                                                   Func(racketeer.setHealthForMe, +int(math.ceil(self.maxHP / 2))),
                                                   Func(racketeer.updateHealthBar, 0)),
                               Func(racketeer.setNeutralAnimationDrop)).start()

    def checkProfiteering2(self, racketeer, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        if self.currHP < int(math.ceil(self.maxHP / 4)):
            self.damageInterval = Sequence(Parallel(
                                                   Func(self.showHpTextNew, x),
                                                   Func(self.setHealthForMe, -x),
                                                   Func(self.updateHealthBar, 0)),
                               Func(self.setNeutralAnimationDrop)).start()
            self.healInterval = Sequence(Parallel(Func(racketeer.showHpTextNew, +x, text="SYPHONED!", colorCode=1),
                                                  Func(racketeer.setHealthForMe, +x),
                                                  Func(racketeer.updateHealthBar, 0)),
                                         Func(racketeer.setNeutralAnimationDrop)).start()
        else:
            self.damageInterval = Sequence(Parallel(
                                                    Func(self.showHpTextNew, -int(math.ceil(self.maxHP / 4))),
                                                  Func(self.setHealthForMe, -int(math.ceil(self.maxHP / 4))),
                                                  Func(self.updateHealthBar, 0)),
                                         Func(self.setNeutralAnimationDrop)).start()
            self.healInterval = Sequence(Parallel(Func(racketeer.showHpTextNew, +int(math.ceil(self.maxHP / 4)), text="SYPHONED!", colorCode=1), 
                                                   Func(racketeer.setHealthForMe, +int(math.ceil(self.maxHP / 4))),
                                                   Func(racketeer.updateHealthBar, 0)),
                               Func(racketeer.setNeutralAnimationDrop)).start()

    def makeProfiteeringInterval(self, racketeer, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead and not self.getProjectedRevive():
            return suitTrack


        oldPending = self._pendingQueuedDamage

        projectedCurrentHP = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))

        x = projectedCurrentHP
        dmg = int(math.ceil(self.maxHP / 2))

        if projectedCurrentHP < dmg:
            dmg = x

        if dmg <= 0:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0
        if not crossedZeroThisCall:
            suitTrack.append(ActorInterval(self, 'flatten', startTime=0.55))
            suitTrack.append(Func(self.setNeutralAnimationDrop))

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            if self.dna.name == 'redd' and not self.isVirtual:
            #    suitTrack.append(self.makeCogStepBackDeathInterval(battle))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif self.isVirtual:
            #    suitTrack.append(self.makeCogStepBackDeathInterval(battle))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif not self.isSkeleton and revives >= 2:
                # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
            #    suitTrack.append(self.makeCogStepBackDeathInterval(battle))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitCrashTrack(self, battle, 7))
                suitTrack.append(Func(self.makeDead))

        return suitTrack

    def makeUsuryInterval(self, racketeer, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead and not self.getProjectedRevive():
            return suitTrack


        oldPending = self._pendingQueuedDamage

        projectedCurrentHP = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))

        x = projectedCurrentHP
        dmg = int(math.ceil(self.maxHP / 3))

        if projectedCurrentHP < dmg:
            dmg = x

        if dmg <= 0:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            if self.dna.name == 'redd' and not self.isVirtual:
                # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif self.isVirtual:
                # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif not self.isSkeleton and revives >= 2:
                # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))

        return suitTrack
    
    def makeProfiteeringInterval2(self, racketeer, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead and not self.getProjectedRevive():
            return suitTrack


        oldPending = self._pendingQueuedDamage

        projectedCurrentHP = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))

        x = projectedCurrentHP
        dmg = int(math.ceil(self.maxHP / 4))

        if projectedCurrentHP < dmg:
            dmg = x

        if dmg <= 0:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0
        if not crossedZeroThisCall:
            suitTrack.append(ActorInterval(self, 'flatten', startTime=0.55))
            suitTrack.append(Func(self.setNeutralAnimationDrop))

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            if self.dna.name == 'redd' and not self.isVirtual:
                # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif self.isVirtual:
                # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif not self.isSkeleton and revives >= 2:
                # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitCrashTrack(self, battle, 7))
                suitTrack.append(Func(self.makeDead))

        return suitTrack

    def makeUnionBustInterval(self, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead and not self.getProjectedRevive():
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage

        projectedCurrentHP = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))

        if projectedCurrentHP <= 0:
            return suitTrack

        dmg = int(projectedCurrentHP)

        newPending = oldPending + dmg

        self.addPendingQueuedDamage(dmg)

        showDamage = Sequence(Wait(2), Parallel(ActorInterval(self, 'flatten', duration = .55), MovieUtil.createSuitCrashTrack(self, battle, 7), Func(self.showHpTextNew, -dmg, text="BUSTED!", colorCode=3),
                                   Func(self.setHealthForMe, - self.currHP),
                                   Func(self.updateHealthBar, 0)))

        suitTrack.append(showDamage)
        return suitTrack

    def makeHeadRollerInterval(self, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        # HP this suit effectively has left after already-queued damage
        projectedCurrentHP = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))

        # If queued damage already reduces it to 0 or below, do not sacrifice it again
        if projectedCurrentHP <= 0:
            return suitTrack

        dmg = int(projectedCurrentHP)
        if dmg <= 0:
            return suitTrack

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)

        showDamage = Sequence(
            ActorInterval(self, 'soak', duration=2.0),
            Parallel(
                Func(self.makeUnTarget),
                Sequence(
                    Func(self.setChatAbsolute, "Ouch.", CFSpeech | CFTimeout),
                    ActorInterval(self, 'pie-small-react'),
                    Func(self.setNeutralAnimationDrop)
                ),
                MovieUtil.spawnHeadExplosion(self, battle),
                Func(self.showHpTextNew, -dmg, text="TERMINATED!", colorCode=4),
                Func(self.setHealthForMe, -dmg),
                Func(self.updateHealthBar, 0)
            )
        )

        suitTrack.append(showDamage)

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            suitTrack.append(MovieUtil.createSuitHeadlessDeathTrack(self, battle))
            suitTrack.append(Func(self.makeDead))

        return suitTrack

    def checkHeadRoller(self, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        if self.currHP > 0 and not self.isDead:
            self.damageInterval = Sequence(ActorInterval(self, 'soak', duration = 2.0), Sequence(Parallel(Func(self.makeUnTarget), MovieUtil.spawnHeadExplosion(self, battle), Func(self.showHpTextNew, -self.currHP, text="TERMINATED!", colorCode=4),
                                            Func(self.setHealthForMe, - self.currHP),
                               Func(self.updateHealthBar, 0)),
                                           Func(self.setChatAbsolute, "Ouch.", CFSpeech | CFTimeout), Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(self, battle),
                                          )).start()

    def checkBalanceOfTheLedger(self, battle, hp):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        if (self.currHP > 0) and (self.currHP < self.maxHP) and not self.getManager():
            self.damageInterval = Sequence(Wait(1.5), Sequence(Parallel(ActorInterval(self, 'pie-small-react'), MovieUtil.spawnHeadExplosion(self, battle), Func(self.showHpTextNew, -self.currHP),
                                            Func(self.setHealthForMe, - self.currHP),
                               Func(self.updateHealthBar, 0)), MovieUtil.createSuitHeadlessDeathTrack(self, battle),
                                          )).start()
        if self.getManager() and self.currHP > 0:
            self.damageInterval = Sequence(Wait(1.5), Parallel(Func(self.showHpTextNew, + hp),
                                                             Func(self.setHealthForMe, + hp),
                                                             Func(self.updateHealthBar, 0))).start()
            self.addPendingQueuedHealing(hp)

    def makeBalanceTheLedgerInterval(self, hp, battle, damageMult):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead and not self.getProjectedRevive():
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage

        # HP this suit effectively has left after already-queued damage
        projectedCurrentHP = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))

        # If queued damage already reduces it to 0 or below, do not sacrifice it again
        if projectedCurrentHP <= 0:
            return suitTrack

        hpBeforeThisCall = projectedCurrentHP

        showDamage = Sequence(Wait(1.5), Sequence(Parallel(ActorInterval(self, 'pie-small-react'), MovieUtil.spawnHeadExplosion(self, battle), Func(self.showHpTextNew, -projectedCurrentHP),
                                            Func(self.setHealthForMe, - projectedCurrentHP),
                               Func(self.updateHealthBar, 0)), MovieUtil.createSuitHeadlessDeathTrack(self, battle),
                                          ))
        if damageMult > 0:
            managerHealTrack = Sequence(Wait(1.5), Parallel(Func(self.showHpTextNew, + hp, text="+%s%% Damage!" % damageMult, colorCode=1),
                                                             Func(self.setHealthForMe, + hp),
                                                             Func(self.updateHealthBar, 0)))
        else:
            managerHealTrack = Sequence()
        if hpBeforeThisCall < self.maxHP and not self.getManager() and not self.getGovernaught():
            suitTrack.append(showDamage)
        if self.getManager():
            self.addPendingQueuedHealing(hp)
            suitTrack.append(managerHealTrack)
        # crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        # if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
        #     self._pendingQueuedDeath = True
            # revives = self.getSkeleRevives()
            # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            # if self.dna.name == 'redd' and not self.isVirtual:
            #     suitTrack.append(Func(self.makeDead))
            #     suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            # elif self.isVirtual:
            #     suitTrack.append(Func(self.makeDead))
            #     suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            # elif not self.isSkeleton and revives >= 2:
            #     suitTrack.append(Func(self.makeDead))
            #     suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            # elif self.isSkeleton and revives >= 2:
            #     suitTrack.append(Func(self.makeDead))
            #     suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            # elif self.isSkeleton and revives >= 1 and not self.isRevive:
            #     suitTrack.append(Func(self.makeDead))
            #     suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            # elif not self.isSkeleton and revives >= 1:
            #     suitTrack.append(Func(self.makeDead))
            #     suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            # elif not self.isVirtual:
            #     suitTrack.append(Func(self.makeDead))
            #     suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
        return suitTrack

    def checkUnionBust(self, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        if self.currHP > 0 and not self.getManager() and not self.isDead and not self.isContracted and not self.isContracted2:
            self.damageInterval = Sequence(Wait(2), Parallel(ActorInterval(self, 'flatten', duration = .55), MovieUtil.createSuitCrashTrack(self, battle, 7), Func(self.showHpTextNew, -self.currHP, text="BUSTED!", colorCode=3),
                                   Func(self.setHealthForMe, - self.currHP),
                                   Func(self.updateHealthBar, 0))).start()

    def checkSkelecogHP(self):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        self.damageInterval = Sequence(Func(self.setHealthForMe, 0), Func(self.updateHealthBar, 0)).start()

    def checkHeadRoller2(self, ambassador, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int(self.currHP)
        self.damageInterval = Sequence(Func(self.showHpTextNew, -self.currHP, text="GUILTY!", colorCode=4), Func(self.setHealthForMe, - self.currHP),
                               Func(self.updateHealthBar, 0)).start()
        ambassador.addPendingQueuedHealing(self.currHP)
        self.healInterval = Sequence(Parallel(Func(ambassador.showHpTextNew, +self.currHP, text="SYPHONED!", colorCode=1),
                                                   Func(ambassador.setHealthForMe, +self.currHP),
                                                   Func(ambassador.updateHealthBar, 0)),
                               Func(ambassador.setNeutralAnimation)).start()
        
    def checkHeadRollerUnionBust(self, ambassador, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int(self.currHP)
        self.damageInterval = Sequence(Func(self.showHpTextNew, -self.currHP, text="BUSTED!", colorCode=4), Func(self.setHealthForMe, - self.currHP),
                               Func(self.updateHealthBar, 0)).start()
        ambassador.addPendingQueuedHealing(self.currHP)
        self.healInterval = Sequence(Parallel(Func(ambassador.setSuitStatusEffect, 'damageUp', modifier=int(math.ceil(x * .05)), mode='refreshModifier')), 
                                     Parallel(Func(ambassador.showHpTextNew, +self.currHP, text="+%s%%" % int(math.ceil(x * .05)) + " Damage!", colorCode=1),
                                                   Func(ambassador.setHealthForMe, +self.currHP),
                                                   Func(ambassador.updateHealthBar, 0)),
                               Func(ambassador.setNeutralAnimation)).start()

    def checkHeadRollerChairman(self, ambassador, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int(self.currHP)
        self.damageInterval = Sequence(Func(self.showHpTextNew, -self.currHP, text="TERMINATED!", colorCode=4), Func(self.setHealthForMe, - self.currHP),
                               Func(self.updateHealthBar, 0)).start()
        self.healInterval = Sequence(Parallel(Func(ambassador.showHpTextNew, +self.currHP, text="SYPHONED!", colorCode=1),
                                                   Func(ambassador.setHealthForMe, +self.currHP),
                                                   Func(ambassador.updateHealthBar, 0)),
                               Func(ambassador.setNeutralAnimation)).start()
        ambassador.addPendingQueuedHealing(self.currHP)

    def _getSplatFilename2(self, level):
        splatDict = {
            0: 'tiny_splat_cake',
            1: 'tiny_splat_fruit',
            2: 'tiny_splat_cream',
            3: 'tiny_splat_cake',
            4: 'tiny_splat_fruit',
            5: 'tiny_splat_cream',
            6: 'tiny_splat_cake',
            7: 'tiny_splat_wedding'
        }
        return 'phase_5/maps/%s.png' % (
            splatDict[level]
        )

    def _getSplatFilename(self, level):
        splatDict = {
            0: 'splat_cake',
            1: 'splat_fruit',
            2: 'splat_cream',
            3: 'splat_cake',
            4: 'splat_fruit',
            5: 'splat_cream',
            6: 'splat_cake',
            7: 'splat_wedding'
        }
        return 'phase_5/maps/%s.png' % (
            splatDict[level]
        )

    def _getSplatParts(self):
        if hasattr(self, '_splatParts'):
            return self._splatParts

        actorNode = self.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        self._splatParts = []

        for i in xrange(actorCollection.getNumPaths()):
            thing = actorCollection[i]
            if thing.getName() not in ('joint_Rhold', 'joint_Lhold', 'joint_attachMeter', 'joint_shadow', 'joint_nameTag', 'def_nameTag'):
                self._splatParts.append(thing)

        return self._splatParts

    def _initCompositeSplat(self, sampleFilename):
        if hasattr(self, '_splatImage'):
            return

        sampleTex = loader.loadTexture(sampleFilename)
        if not sampleTex:
            print
            'Failed to load sample splat texture:', sampleFilename
            return

        sampleImage = PNMImage()
        sampleTex.store(sampleImage)

        if sampleImage.getNumChannels() < 1:
            print
            'Sample splat image invalid:', sampleFilename
            return

        x = sampleImage.getXSize()
        y = sampleImage.getYSize()

        self._splatImage = PNMImage(x, y, 4)

        # White RGB + zero alpha works well for decal-style overlays
        self._splatImage.fill(1.0, 1.0, 1.0)
        self._splatImage.alphaFill(0.0)

        self._splatTexture = Texture('composite-splat')
        self._splatTexture.load(self._splatImage)
        self._splatTexture.setWrapU(Texture.WMClamp)
        self._splatTexture.setWrapV(Texture.WMClamp)

        self._splatTexture.setMinfilter(Texture.FTNearest)
        self._splatTexture.setMagfilter(Texture.FTNearest)

        self._splatStage = TextureStage('compositeSplat')
        self._splatStage.setMode(TextureStage.MDecal)
        self._splatStage.setSavedResult(True)

        for thing in self._getSplatParts():
            #thing.setTransparency(TransparencyAttrib.MAlpha)
            thing.setTexture(self._splatStage, self._splatTexture, 1)

    def _addSplatToComposite(self, filename):
        self._initCompositeSplat(filename)

        if not hasattr(self, '_splatImage'):
            return

        splatTex = loader.loadTexture(filename)
        if not splatTex:
            print 'Failed to load splat texture:', filename
            return

        splatImage = PNMImage()
        splatTex.store(splatImage)

        if splatImage.getNumChannels() < 1:
            print 'Invalid splat image:', filename
            return

        compositeWidth = self._splatImage.getXSize()
        compositeHeight = self._splatImage.getYSize()

        if (
            splatImage.getXSize() != compositeWidth or
            splatImage.getYSize() != compositeHeight
        ):
            print 'Splat size mismatch:', filename
            return

        # Randomly shift the splat within the composite texture.
        #
        # Increase these values for more movement.
        # Decrease them if splats get clipped too heavily.
        maxShiftX = int(compositeWidth * 0.25)
        maxShiftY = int(compositeHeight * 0.25)

        offsetX = random.randint(-maxShiftX, maxShiftX)
        offsetY = random.randint(-maxShiftY, maxShiftY)

        # Determine the source and destination regions so that the shifted
        # image remains inside the composite texture.
        if offsetX >= 0:
            sourceX = 0
            destinationX = offsetX
            copyWidth = compositeWidth - offsetX
        else:
            sourceX = -offsetX
            destinationX = 0
            copyWidth = compositeWidth + offsetX

        if offsetY >= 0:
            sourceY = 0
            destinationY = offsetY
            copyHeight = compositeHeight - offsetY
        else:
            sourceY = -offsetY
            destinationY = 0
            copyHeight = compositeHeight + offsetY

        if copyWidth <= 0 or copyHeight <= 0:
            return

        self._splatImage.blendSubImage(
            splatImage,
            destinationX,
            destinationY,
            sourceX,
            sourceY,
            copyWidth,
            copyHeight
        )

        # Update the existing composite texture.
        self._splatTexture.load(self._splatImage)

    def _clearCompositeSplat(self):
        if not hasattr(self, '_splatImage'):
            return

        self._splatImage.fill(0.0, 0.0, 0.0)
        self._splatImage.alphaFill(0.0)
        self._splatTexture.load(self._splatImage)

    def splatSuit(self, level, clear=False):
        if clear:
            self._clearCompositeSplat()
            return

        # Add the normal splat.
        largeFilename = self._getSplatFilename(level)
        self._addSplatToComposite(largeFilename)

        # Add the tiny splat too.
        tinyFilename = self._getSplatFilename2(level)
        self._addSplatToComposite(tinyFilename)

    def splatClear(self):
        stages = self.findAllTextureStages()
        for stage in stages:
            actorNode = self.find('**/__Actor_modelRoot')
            actorCollection = actorNode.findAllMatches('*')
            parts = ()
            for thingIndex in xrange(0, actorCollection.getNumPaths()):
                thing = actorCollection[thingIndex]
                if thing.getName() not in ('joint_Rhold', 'joint_Lhold', 'joint_attachMeter', 'joint_nameTag', 'joint_shadow', 'def_nameTag'):
                    if stage.getName().startswith('splat_wedding'):
                        thing.clearTexture(stage)
                    if stage.getName().startswith('splat_cream'):
                        thing.clearTexture(stage)
                    if stage.getName().startswith('splat_fruit'):
                        thing.clearTexture(stage)
                    if stage.getName().startswith('splat_cake'):
                        thing.clearTexture(stage)
          #  for headPart in self.headParts:
               # if stage.getName().startswith('splat_wedding'):
                #    headPart.clearTexture(stage)
              #  if stage.getName().startswith('splat_cream'):
                #    headPart.clearTexture(stage)
               # if stage.getName().startswith('splat_fruit'):
                 #   headPart.clearTexture(stage)
               # if stage.getName().startswith('splat_cake'):
                  #  headPart.clearTexture(stage)

    def checkAmbassadorPhase2(self):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.setHP, self.currHP)).start()

    def checkDamageUp(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.setDamageUp, self.getDamageUp() + num)).start()

    def checkRippedUp(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.setRippedUp, self.getRippedUp() + num)).start()

    def checkCollectCall(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.setCollectCall, num), Func(self.makeCollectCall, num)).start()

    def checkDesperation(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.setDesperation, self.getDesperation() + num)).start()

    def checkExtraAttacks(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.makeExtraAttacks, self.getExtraAttacks() + num)).start()

    def checkExtraAbilities(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None

        newAmount = self.getExtraAbilities() + num

        # Higher abilities = shorter duration = faster chain
        duration = max(0.25, 2.0 - (newAmount * 0.2))

        self.damageInterval = Sequence(
            Func(self.makeExtraAbilities, newAmount),
            Func(self.setChainsawTexRoll, duration)
        )
        self.damageInterval.start()

    def checkDamageDown(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.setDamageDown, self.getDamageDown() + num)).start()

    def checkVulnerabilityUp(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.setVulnerability, self.getVulnerability() + num)).start()

    def checkBattleSpeed(self, attorney, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if attorney.battleSpeed < 1:
            self.damageInterval = Parallel(Func(self.makeBattleSpeed, 1.5)).start()
        else:
            self.damageInterval = Parallel(Func(self.makeBattleSpeed, attorney.getBattleSpeed() + num)).start()

    def checkBattleSpeed2(self, attorney, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if attorney.battleSpeed < 1:
            self.damageInterval = Parallel(Func(self.makeBattleSpeed, 1.25)).start()
        else:
            self.damageInterval = Parallel(Func(self.makeBattleSpeed, attorney.getBattleSpeed() + num)).start()

    def checkDamageReduction(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.setDamageReduction, self.getDamageReduction() + num)).start()

    def makeDeathCheckIntervalOLD(self, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 and not self.isDead:
            revives = self.getSkeleRevives()
            # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif self.isVirtual:
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))

        return suitTrack

    def checkDeathCheck(self, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.currHP <= 0 and not self.isDead:
            revives = self.getSkeleRevives()
            suitTrack = Sequence()
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif self.isVirtual:
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))
            self.damageInterval = Sequence(suitTrack).start()

    def checkDeathCheck2(self, suit, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.currHP <= 0 and not self.isDead:
            revives = self.getSkeleRevives()
            suitTrack = Sequence()
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
            self.damageInterval = Sequence(suitTrack).start()

    def checkSueDamage(self, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        if self.currHP > 0 and self.isSued:
            if self.currHP < (self.maxHP / 4):
                self.damageInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'),
                                                        Func(self.showHpTextNew, -x, text="SUED!", colorCode=1),
                                                        Func(self.setHealthForMe, -x),
                                                        Func(self.updateHealthBar, 0)), Func(self.setDizzy, 0),
                                               Func(self.setNeutralAnimation)).start()
            else:
                self.damageInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'),
                                                        Func(self.showHpTextNew, -(self.maxHP / 4), text="SUED!", colorCode=1),
                                                        Func(self.setHealthForMe, -(self.maxHP / 4)), Func(self.setDizzy, 0),
                                                        Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimation)
                                              ).start()

    def checkHeavyRainDamage(self, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        if self.currHP > 0 and self.isHeavyRain:
            if self.currHP < self.getHeavyRainDamage():
                self.damageInterval = Sequence(Parallel(Func(self.showHpTextNew, -x),
                                                        Func(self.setHealthForMe, -x),
                                                        Func(self.updateHealthBar, 0),  MovieUtil.shortCircuitTrack(self, battle), Func(self.removeHeavyRainDamage))).start()
            else:
                self.damageInterval = Sequence(Parallel(Func(self.showHpTextNew, -self.getHeavyRainDamage()),
                                                        Func(self.setHealthForMe, -self.getHeavyRainDamage()),
                                                        Func(self.updateHealthBar, 0)), Func(self.removeHeavyRainDamage)).start()

    def checkSueDamage2(self, suit, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        if self.currHP > 0 and not suit and self.isSued:
            if self.currHP < (self.maxHP / 4):
                self.damageInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'),
                                                        Func(self.showHpTextNew, -x, text="SUED!", colorCode=1),
                                                        Func(self.setHealthForMe, -x),
                                                        Func(self.updateHealthBar, 0)),
                                               Func(self.setNeutralAnimation)).start()
            else:
                self.damageInterval = Sequence(Parallel(ActorInterval(self, 'pie-small-react'),
                                                        Func(self.showHpTextNew, -(self.maxHP / 4), text="SUED!", colorCode=1),
                                                        Func(self.setHealthForMe, -(self.maxHP / 4)),
                                                        Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimation)
                                              ).start()

    def makeDamageLevelInterval(self, battle, levelDamage):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead and not self.getProjectedRevive():
            return suitTrack

        dmg = int(levelDamage)
        if dmg <= 0:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)

        if self.dna.name == 'hroller':
            if float(self.currHP) < levelDamage:
                x = int(self.currHP - 1)
                showDamage = Sequence(Parallel(ActorInterval(self, 'pie-small-react'),
                                         Func(self.showHpText, - x), Func(self.setHealthForMe, - x),
                                         Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimationDrop),
                                           Func(self.removeLevelDamage))
            else:
                showDamage = Sequence(
            Parallel(
                ActorInterval(self, 'pie-small-react'),
                Func(self.showHpTextNew, -dmg),
                Func(self.setHealthForMe, -dmg),
                Func(self.updateHealthBar, 0)
            ),
            Func(self.setNeutralAnimationDrop)
        )
        else:
            showDamage = Sequence(
            Parallel(
                ActorInterval(self, 'pie-small-react'),
                Func(self.showHpTextNew, -dmg),
                Func(self.setHealthForMe, -dmg),
                Func(self.updateHealthBar, 0)
            ),
            Func(self.setNeutralAnimationDrop)
        )

        suitTrack.append(showDamage)
        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead and not self.dna.name == 'hroller':
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
        return suitTrack

    def makeDamageInterval(self, battle, absorbDamage):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead and not self.getProjectedRevive():
            return suitTrack

        dmg = int(absorbDamage)
        if dmg <= 0:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)

        if self.dna.name == 'safesupervis':
            showDamage = Sequence(
                Parallel(
                    ActorInterval(self, 'pie-small-react'),
                    Func(self.showHpTextNew, -dmg, text="OVERHEATED!", colorCode=5),
                    Func(self.setHealthForMe, -dmg),
                    Func(self.updateHealthBar, 0)
                ),
                Func(self.setNeutralAnimationDrop)
            )
        else:
            showDamage = Sequence(
                Parallel(
                    ActorInterval(self, 'pie-small-react'),
                    Func(self.showHpText, -dmg),
                    Func(self.setHealthForMe, -dmg),
                    Func(self.updateHealthBar, 0)
                ),
                Func(self.setNeutralAnimationDrop)
            )

        suitTrack.append(showDamage)
        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead and not self.dna.name == 'videog':
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
        return suitTrack

    def makeDamageInterval2(self, battle, absorbDamage):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead and not self.getProjectedRevive():
            return suitTrack

        dmg = int(absorbDamage)
        if dmg <= 0:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)

        showDamage = Sequence(
                Parallel(
                    ActorInterval(self, 'pie-small-react'),
                    Func(self.showHpText, -dmg),
                    Func(self.setHealthForMe, -dmg),
                    Func(self.updateHealthBar, 0)
                ),
                Func(self.setNeutralAnimationDrop)
            )

        suitTrack.append(showDamage)
        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
        return suitTrack

    def makeAbsorbDamageInterval(self, battle, absorbDamage):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead and not self.getProjectedRevive():
            return suitTrack

        dmg = int(absorbDamage)
        if dmg <= 0:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)

        if self.dna.name == 'sgoat':
            showDamage = Sequence(
                Parallel(
                    ActorInterval(self, 'pie-small-react'),
                    Func(self.showHpTextNew, -dmg, text="ABSORBED!", colorCode=1),
                    Func(self.setHealthForMe, -dmg),
                    Func(self.updateHealthBar, 0)
                ),
                Func(self.setNeutralAnimationDrop),
                Func(self.addRageBuilding, int(dmg))
            )
        else:
            showDamage = Sequence(
                Parallel(
                    ActorInterval(self, 'pie-small-react'),
                    Func(self.showHpTextNew, -dmg, text="ABSORBED!", colorCode=1),
                    Func(self.setHealthForMe, -dmg),
                    Func(self.updateHealthBar, 0)
                ),
                Func(self.setNeutralAnimationDrop)
            )

        suitTrack.append(showDamage)
        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
        return suitTrack

    def makeBarInterval(self, battle, damage):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead and not self.getProjectedRevive():
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage

        # HP this suit effectively has left after already-queued damage
        projectedCurrentHP = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))

        # If queued damage already reduces it to 0 or below, do not sacrifice it again
        if projectedCurrentHP <= 0:
            return suitTrack

        dmg = damage
        if dmg <= 0:
            return suitTrack

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)

        showDamage = Sequence(
            Parallel(
                ActorInterval(self, 'flatten'),
                Func(self.showHpTextNew, -dmg),
                Func(self.setHealthForMe, -dmg),
                Func(self.updateHealthBar, 0)
            ),
            Func(self.setNeutralAnimationDrop)
        )

        suitTrack.append(showDamage)
        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
        return suitTrack

    def makeSueDamageInterval(self, battle, dmg):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead and not self.getProjectedRevive():
            return suitTrack
        if not self.hasSuitStatusEffect('sued'):
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage

        # HP this suit effectively has left after already-queued damage
        projectedCurrentHP = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))

        # If queued damage already reduces it to 0 or below, do not sacrifice it again
        if projectedCurrentHP <= 0:
            return suitTrack

        if dmg <= 0:
            return suitTrack
        if self.currHP < dmg:
            dmg = projectedCurrentHP

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)

        showDamage = Sequence(
            Parallel(
                ActorInterval(self, 'pie-small-react'),
                Func(self.showHpTextNew, -dmg, text="SUED!", colorCode=1),
                Func(self.setHealthForMe, -dmg),
                Func(self.updateHealthBar, 0)
            ),
            Func(self.setNeutralAnimationDrop)
        )

        suitTrack.append(showDamage)
        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
        return suitTrack

    def makeZapDamageInterval(self, battle, dmg):
        suitTrack = Sequence()

        if self.currHP <= 0 and not self.getProjectedRevive():
            return suitTrack
        # if not self.isZapped or self.freshlyZapped:
        #     return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage

        # HP this suit effectively has left after already-queued damage
        projectedCurrentHP = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))

        # If queued damage already reduces it to 0 or below, do not sacrifice it again
        # if projectedCurrentHP <= 0 and not self.getProjectedLured():
        #     return suitTrack

        if dmg <= 0:
            return suitTrack

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)

        showDamage = Parallel(
            ActorInterval(self, 'small-zap'),
            MovieUtil.createSuitStunInterval(self, 0, 2.0),
            Func(self.showHpTextNew, -dmg, text="AFTERSHOCK!", colorCode=3),
            Func(self.setHealthForMe, -dmg),
            Func(self.updateHealthBar, 0)
        )

        suitTrack.append(showDamage)
        suitTrack.append(Func(self.clearSuitStatusEffect, 'zapped'))
        suitTrack.append(Func(self.setNeutralAnimation))

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()

            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitHeadlessDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitHeadlessDeathTrack(self, battle))
        return suitTrack

    def checkZapDamage(self, battle):
        suitTrack = Sequence()
        x = int(self.currHP)
        if self.currHP > 0 and self.isZapped:
            if self.currHP < self.getZapCondition():
                damageInterval = Sequence(Parallel(ActorInterval(self, 'small-zap'), MovieUtil.createSuitStunInterval(self, 0, 2.0),
                                                        Func(self.showHpTextNew, -x, text="AFTERSHOCK!", colorCode=3),
                                                        Func(self.setHealthForMe, -x),
                                                        Func(self.updateHealthBar, 0)), Func(self.makeUnZapped),
                                               Func(self.setNeutralAnimation))
                suitTrack.append(damageInterval)
            else:
                damageInterval = Sequence(Parallel(ActorInterval(self, 'small-zap'), MovieUtil.createSuitStunInterval(self, 0, 2.0),
                                                        Func(self.showHpTextNew, -self.getZapCondition(), text="AFTERSHOCK!", colorCode=3),
                                                        Func(self.setHealthForMe, -self.getZapCondition()), Func(self.makeUnZapped),
                                                        Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimation),
                                              )
                suitTrack.append(damageInterval)
        return suitTrack

    def checkZapDamage2(self, suit, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        x = int(self.currHP)
        if self.currHP > 0 and not suit and self.isZapped:
            if self.currHP < self.getZapCondition():
                self.damageInterval = Sequence(Parallel(ActorInterval(self, 'small-zap'), MovieUtil.createSuitStunInterval(self, 0, 2.0),
                                                        Func(self.showHpTextNew, -x, text="AFTERSHOCK!", colorCode=3),
                                                        Func(self.setHealthForMe, -x),
                                                        Func(self.updateHealthBar, 0)),
                                               Func(self.setNeutralAnimation)).start()
            else:
                self.damageInterval = Sequence(Parallel(ActorInterval(self, 'small-zap'), MovieUtil.createSuitStunInterval(self, 0, 2.0),
                                                        Func(self.showHpTextNew, -self.getZapCondition(), text="AFTERSHOCK!", colorCode=3),
                                                        Func(self.setHealthForMe, -self.getZapCondition()),
                                                        Func(self.updateHealthBar, 0)), Func(self.setNeutralAnimation)
                                              ).start()

    def checkPhantomEntrySacrifice(self, videog):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int(self.currHP)
        self.damageInterval = Sequence(Func(self.showHpText, -x),
                                           Func(self.setHealthForMe, -x),
                                           Func(self.updateHealthBar, 0),
                                           Func(self.setNeutralAnimationDrop)).start()
        self.healInterval = Sequence(Func(videog.showHpText, +x),
                                         Func(videog.setHealthForMe, +x),
                                         Func(videog.updateHealthBar, 0),
                                         Func(videog.setNeutralAnimationDrop)).start()
        videog.addPendingQueuedHealing(x)

    def checkBroadcasterDonation(self, videog, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int(self.currHP)
        if self.currHP < 2222:
            self.damageInterval = Sequence(ActorInterval(self, 'mob-mentality', endTime=1), Wait(5.0),
                                                   Func(self.showHpText, -x),
                                                   Func(self.setHealthForMe, -x),
                                                   Func(self.updateHealthBar, 0), ActorInterval(self, 'mob-mentality', startTime=1, endTime=0),
                               Func(self.setNeutralAnimation)).start()
            self.healInterval = Sequence(ActorInterval(videog, 'mob-mentality', endTime=1), Wait(5.0),
                                                  Func(videog.showHpText, +x),
                                                  Func(videog.setHealthForMe, +x),
                                                  Func(videog.updateHealthBar, 0), ActorInterval(videog, 'mob-mentality', startTime=1, endTime=0),
                                         Func(videog.setNeutralAnimation)).start()
            videog.addPendingQueuedHealing(x)
        else:
            self.damageInterval = Sequence(ActorInterval(self, 'mob-mentality', endTime=1), Wait(5.0),
                                                  Func(self.showHpText, -2222),
                                                  Func(self.setHealthForMe, -2222),
                                                  Func(self.updateHealthBar, 0), ActorInterval(self, 'mob-mentality', startTime=1, endTime=0),
                                         Func(self.setNeutralAnimation)).start()
            self.healInterval = Sequence(ActorInterval(videog, 'mob-mentality', endTime=1), Wait(5.0), Func(videog.showHpText, +2222),
                                                   Func(videog.setHealthForMe, +2222),
                                                   Func(videog.updateHealthBar, 0), ActorInterval(videog, 'mob-mentality', startTime=1, endTime=0),
                               Func(videog.setNeutralAnimation)).start()
            videog.addPendingQueuedHealing(2222)

    def checkBroadcasterDonation2(self, videog, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int(self.currHP)
        if self.currHP < 222:
            self.damageInterval = Sequence(ActorInterval(self, 'mob-mentality', endTime=1),
                                                   Func(self.showHpText, -x),
                                                   Func(self.setHealthForMe, -x),
                                                   Func(self.updateHealthBar, 0), ActorInterval(self, 'slip-forward'),
                               Func(self.setNeutralAnimation)).start()
            self.healInterval = Sequence(ActorInterval(videog, 'mob-mentality', endTime=1),
                                                  Func(videog.showHpText, +x),
                                                  Func(videog.setHealthForMe, +x),
                                                  Func(videog.updateHealthBar, 0), ActorInterval(videog, 'pie-small-react'),
                                         Func(videog.setNeutralAnimation)).start()
            videog.addPendingQueuedHealing(x)
        else:
            self.damageInterval = Sequence(ActorInterval(self, 'mob-mentality', endTime=1),
                                                  Func(self.showHpText, -222),
                                                  Func(self.setHealthForMe, -222),
                                                  Func(self.updateHealthBar, 0), ActorInterval(self, 'slip-forward'),
                                         Func(self.setNeutralAnimation)).start()
            self.healInterval = Sequence(ActorInterval(videog, 'mob-mentality', endTime=1), Func(videog.showHpText, +222),
                                                   Func(videog.setHealthForMe, +222),
                                                   Func(videog.updateHealthBar, 0), ActorInterval(videog, 'pie-small-react'),
                               Func(videog.setNeutralAnimation)).start()
            videog.addPendingQueuedHealing(222)

    def makeBroadcasterDonationIntervalFail(self, videog, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        x = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        dmg = 222

        if self.currHP < 222:
            dmg = x

        if dmg <= 0:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)

        damageTrack = Sequence(ActorInterval(self, 'mob-mentality', endTime=1),
                                                   Func(self.showHpText, -dmg),
                                                   Func(self.setHealthForMe, -dmg),
                                                   Func(self.updateHealthBar, 0), ActorInterval(self, 'slip-forward'),
                               Func(self.setNeutralAnimation))

        healTrack = Sequence(ActorInterval(videog, 'mob-mentality', endTime=1), Func(videog.showHpText, +dmg),
                                                   Func(videog.setHealthForMe, +dmg),
                                                   Func(videog.updateHealthBar, 0), ActorInterval(videog, 'pie-small-react'),
                               Func(videog.setNeutralAnimation))
        videog.addPendingQueuedHealing(dmg)

        suitTrack.append(Parallel(damageTrack, healTrack))

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif self.isVirtual:
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))

        return suitTrack

    def makeBroadcasterDonationInterval(self, videog, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        x = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        dmg = 2222

        if self.currHP < 2222:
            dmg = x

        if dmg <= 0:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)

        damageTrack = Sequence(
            ActorInterval(self, 'mob-mentality', endTime=1),
            Wait(5.0),
            Func(self.showHpText, -dmg),
            Func(self.setHealthForMe, -dmg),
            Func(self.updateHealthBar, 0),
            ActorInterval(self, 'mob-mentality', startTime=1, endTime=0),
            Func(self.setNeutralAnimationDrop)
        )

        healTrack = Sequence(
            ActorInterval(videog, 'mob-mentality', endTime=1),
            Wait(5.0),
            Func(videog.showHpText, +dmg),
            Func(videog.setHealthForMe, +dmg),
            Func(videog.updateHealthBar, 0),
            ActorInterval(videog, 'mob-mentality', startTime=1, endTime=0),
            Func(videog.setNeutralAnimationDrop)
        )
        videog.addPendingQueuedHealing(dmg)

        suitTrack.append(Parallel(damageTrack, healTrack))

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif self.isVirtual:
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))

        return suitTrack

    def makeSilhouetteDonation(self, videog, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        x = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        dmg = 3000

        if int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) < 3000:
            dmg = x

        if dmg <= 0:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)

        # damageTrack = Sequence(Func(self.showHpText, -dmg),
        #     Func(self.setHealthForMe, -dmg),
        #     Func(self.updateHealthBar, 0), Func(self.setNeutralAnimationDrop)
        # )

        # healTrack = Sequence(Func(videog.showHpText, +dmg),
        #     Func(videog.setHealthForMe, +dmg),
        #     Func(videog.updateHealthBar, 0),
        #     Func(videog.setNeutralAnimationDrop)
        # )
        # videog.addPendingQueuedHealing(dmg)

        # suitTrack.append(Parallel(damageTrack, healTrack))

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            suitTrack.append(Wait(self.getDuration('walk') + 1))
            # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif self.isVirtual:
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))

        return suitTrack

    def makeRedundantAuthorityInterval(self, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead and not self.getProjectedRevive():
            return suitTrack

        dmg = 500
        if dmg <= 0:
            return suitTrack
        if self.currHP < dmg:
            dmg = int(self.currHP)

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)

        suitTrack.append(Func(self.setNeutralAnimationDrop))

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()

            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
            elif self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(Func(self.makeDead))
                suitTrack.append(MovieUtil.createSuitHeadlessDeathTrack(self, battle))
        return suitTrack

    def makeBroadcasterDonation2Interval(self, videog, battle):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead:
            return suitTrack

        x = int(self.currHP)
        dmg = 111

        if self.currHP < 111:
            dmg = x

        if dmg <= 0:
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage
        newPending = dmg

        hpBeforeThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))
        hpAfterThisCall = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)) - newPending

        self.addPendingQueuedDamage(dmg)

        damageTrack = Sequence(
            ActorInterval(self, 'mob-mentality', endTime=1),
            Func(self.showHpText, -dmg),
            Func(self.setHealthForMe, -dmg),
            Func(self.updateHealthBar, 0),
            ActorInterval(self, 'slip-forward'),
            Func(self.setNeutralAnimationDrop)
        )

        healTrack = Sequence(
            ActorInterval(videog, 'mob-mentality', endTime=1),
            Func(videog.showHpText, +dmg),
            Func(videog.setHealthForMe, +dmg),
            Func(videog.updateHealthBar, 0),
            ActorInterval(videog, 'pie-small-react'),
            Func(videog.setNeutralAnimationDrop)
        )
        videog.addPendingQueuedHealing(dmg)

        suitTrack.append(Parallel(damageTrack, healTrack))

        crossedZeroThisCall = hpBeforeThisCall > 0 and hpAfterThisCall <= 0

        if crossedZeroThisCall and not self._pendingQueuedDeath and not self.isDead:
            self._pendingQueuedDeath = True
            revives = self.getSkeleRevives()
            # suitTrack.append(self.makeCogStepBackDeathInterval(battle))
            if self.dna.name == 'redd' and not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitReviveRedd(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif self.isVirtual:
                suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))
            elif not self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif self.isSkeleton and revives >= 2:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif self.isSkeleton and revives >= 1 and not self.isRevive:
                suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(self, battle))
            elif not self.isSkeleton and revives >= 1:
                suitTrack.append(MovieUtil.createSuitReviveTrack(self, battle))
            elif not self.isVirtual:
                suitTrack.append(MovieUtil.createSuitDeathTrack(self, battle))
                suitTrack.append(Func(self.makeDead))

        return suitTrack

    def checkAmbassadorDamageUp(self, videog, battle):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        destroyedSuits = []
        for suit in battle.activeSuits:
            if not suit.dna.name in SuitBattleGlobals.SpecialCogDict and suit.isTarget and suit.currHP > 0:
                destroyedSuits.append(suit)
        videog.addPendingQueuedHealing((100 * len(destroyedSuits)))
        self.healInterval = Sequence(Func(videog.setSuitStatusEffect, 'damageUp', modifier=(5 * len(destroyedSuits)), mode='refreshModifier'),
                                     Func(videog.showHpTextNew, +(100 * len(destroyedSuits)), text="+%s" % (5 * len(destroyedSuits)) + "%" + " Damage!", colorCode=3),
                                     Func(videog.setHealthForMe, + (100 * len(destroyedSuits))), Func(videog.updateHealthBar, 0)).start()

    def checkHighRollerDonation(self, videog, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int(self.currHP)
        if self.currHP < 3000:
            self.damageInterval = Sequence(Parallel(Func(self.showHpText, -x),
                                                   Func(self.setHealthForMe, -x),
                                                   Func(self.updateHealthBar, 0)),
                               Func(self.setNeutralAnimation)).start()
            self.healInterval = Sequence(Parallel(Func(videog.showHpText, +x),
                                                  Func(videog.setHealthForMe, +x),
                                                  Func(videog.updateHealthBar, 0)),
                                         Func(videog.setNeutralAnimation)).start()
            videog.addPendingQueuedHealing(x)
        else:
            self.damageInterval = Sequence(Parallel(Func(self.showHpText, -3000),
                                                  Func(self.setHealthForMe, -3000),
                                                  Func(self.updateHealthBar, 0)),
                                         Func(self.setNeutralAnimation)).start()
            self.healInterval = Sequence(Parallel(Func(videog.showHpText, +3000),
                                                   Func(videog.setHealthForMe, +3000),
                                                   Func(videog.updateHealthBar, 0)),
                               Func(videog.setNeutralAnimation)).start()
            videog.addPendingQueuedHealing(3000)

    def erclaimSacrifice(self, videog, battle):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int(self.currHP)
        self.damageInterval = Sequence(Parallel(Func(self.showHpText, -x),
                                                Func(self.setHealthForMe, -x),
                                                Func(self.updateHealthBar, 0))).start()
        z = int((videog.maxHP * videog.hardMaxHP) - videog.currHP)
        if videog.currHP >= (videog.maxHP * videog.hardMaxHP):
            self.healInterval = Sequence(
                Parallel(Func(videog.showHpTextNew, 0),
                         Func(videog.setHealthForMe, + 0),
                         Func(videog.updateHealthBar, 0))).start()
        elif videog.currHP + x > (videog.maxHP * videog.hardMaxHP):
            self.healInterval = Sequence(
                Parallel(Func(videog.showHpTextNew, + z),
                         Func(videog.setHealthForMe, + z),
                         Func(videog.updateHealthBar, 0))).start()
            videog.addPendingQueuedHealing(z)
        else:
            self.healInterval = Sequence(
                Parallel(Func(videog.showHpTextNew, + x),
                         Func(videog.setHealthForMe, + x),
                         Func(videog.updateHealthBar, 0))).start()
            videog.addPendingQueuedHealing(x)
        # self.healInterval = Sequence(Parallel(Func(videog.showHpText, +x),
        #                                         Func(videog.setHealthForMe, +x),
        #                                         Func(videog.updateHealthBar, 0))).start()
        # videog.addPendingQueuedHealing(x)

    def checkProToonShake(self, dmg, battle):
        hpCap = int(self.maxHP * self.hardMaxHP)

        projectedHP = self.getQueuedProjectedHPFull()

        healAmount = min(dmg, max(0, hpCap - projectedHP))

        if healAmount > 0:
            self.addPendingQueuedHealing(healAmount)

        return Sequence(
            Parallel(
                Func(self.showHpTextNew, healAmount),
                Func(self.setHealthForMe, healAmount),
                Func(self.updateHealthBar, 0)
            )
        )

    def checkProToonShakeErfit(self, dmg, battle):
        hpCap = int(self.maxHP * self.hardMaxHP)

        projectedHP = self.getQueuedProjectedHPFull()

        healAmount = dmg

        if healAmount > 0:
            self.addPendingQueuedDamage(healAmount)

        return Sequence(
            Parallel(
                Func(self.showHpTextNew, - healAmount),
                Func(self.setHealthForMe, - healAmount),
                Func(self.updateHealthBar, 0)
            )
        )


    def makeSyphonInterval(self):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead and not self.getProjectedRevive():
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage

        # HP this suit effectively has left after already-queued damage
        projectedCurrentHP = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))

        # If queued damage already reduces it to 0 or below, do not sacrifice it again
        if projectedCurrentHP <= 0:
            return suitTrack

        showDamage = Sequence(Sequence(ActorInterval(self, 'effort', startTime=self.getDuration('effort'), endTime=max(0, self.getDuration('effort') - 1.0), playRate=-1.0),
                                                           ActorInterval(self, 'effort', startTime=max(0, self.getDuration('effort') - 1.0))), Func(self.setNeutralAnimationDrop))
        if not self.dna.name == 'phouse' and not self.getProjectedLured():
            suitTrack.append(showDamage)
        return suitTrack
    
    def checkCustomerRetention(self):
        hpCap = int(self.maxHP * self.hardMaxHP)

        projectedHP = self.getQueuedProjectedHPFull()

        healAmount = min(0, max(0, hpCap - projectedHP))

        if healAmount > 0:
            self.addPendingQueuedHealing(healAmount)

        return Sequence(
            Parallel(
                Func(self.showHpTextNew, healAmount),
                Func(self.setHealthForMe, healAmount),
                Func(self.updateHealthBar, 0)
            )
        )

    def makeCongestionInterval(self):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead and not self.getProjectedRevive():
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage

        # HP this suit effectively has left after already-queued damage
        projectedCurrentHP = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))

        # If queued damage already reduces it to 0 or below, do not sacrifice it again
        if projectedCurrentHP <= 0:
            return suitTrack

        hpBeforeThisCall = projectedCurrentHP

        if self.dna.name == 'hustle':
            showDamage = Sequence(Parallel(Func(self.showHpString, "+5% Defense!"),
                                                  Func(self.setSuitStatusEffect, 'shielding', modifier=5, mode='refreshModifier')), Func(self.setNeutralAnimationDrop))
        else:
            showDamage = Sequence(Parallel(Sequence(ActorInterval(self, 'effort', startTime=self.getDuration('effort'), endTime=max(0, self.getDuration('effort') - 1.0), playRate=-1.0),
                                                           ActorInterval(self, 'effort', startTime=max(0, self.getDuration('effort') - 1.0))),
                                                  Func(self.showHpString, "+5% Defense!"), 
                                                  Func(self.setSuitStatusEffect, 'shielding', modifier=5, mode='refreshModifier')), Func(self.setNeutralAnimationDrop))
        if hpBeforeThisCall < self.maxHP:
            suitTrack.append(showDamage)
        return suitTrack

    def makeCompensationInterval(self):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead and not self.getProjectedRevive():
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage

        # HP this suit effectively has left after already-queued damage
        projectedCurrentHP = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))

        # If queued damage already reduces it to 0 or below, do not sacrifice it again
        if projectedCurrentHP <= 0:
            return suitTrack

        hpBeforeThisCall = projectedCurrentHP

        showDamage = Sequence(Parallel(Sequence(ActorInterval(self, 'effort', startTime=self.getDuration('effort'), endTime=max(0, self.getDuration('effort') - 1.0), playRate=-1.0),
                                                           ActorInterval(self, 'effort', startTime=max(0, self.getDuration('effort') - 1.0))),
                                                  Func(self.showHpString, "+5% Damage!"), Func(self.setSuitStatusEffect, 'lureResist', modifier=1), Func(self.setSuitStatusEffect, 'damageUp', modifier=5, mode='refreshModifier')), Func(self.setNeutralAnimationDrop))
        if hpBeforeThisCall < self.maxHP and not self.dna.name == 'racket':
            suitTrack.append(showDamage)
        return suitTrack
    
    def makeCompensationInterval2(self):
        suitTrack = Sequence()

        if self.currHP <= 0 or self.isDead and not self.getProjectedRevive():
            return suitTrack

        if not hasattr(self, '_pendingQueuedDamage'):
            self._pendingQueuedDamage = 0
        if not hasattr(self, '_pendingQueuedDeath'):
            self._pendingQueuedDeath = False

        oldPending = self._pendingQueuedDamage

        # HP this suit effectively has left after already-queued damage
        projectedCurrentHP = int(self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage))

        # If queued damage already reduces it to 0 or below, do not sacrifice it again
        if projectedCurrentHP <= 0:
            return suitTrack

        hpBeforeThisCall = projectedCurrentHP

        showDamage = Sequence(Parallel(Sequence(ActorInterval(self, 'effort', startTime=self.getDuration('effort'), endTime=max(0, self.getDuration('effort') - 1.0), playRate=-1.0),
                                                           ActorInterval(self, 'effort', startTime=max(0, self.getDuration('effort') - 1.0))),
                                                  Func(self.showHpString, "+5% Damage!"), Func(self.setSuitStatusEffect, 'lureResist', modifier=1), Func(self.setSuitStatusEffect, 'damageUp', modifier=5, mode='refreshModifier')), Func(self.setNeutralAnimationDrop))
        suitTrack.append(showDamage)
        return suitTrack
    
    
    def checkPerformanceBonus(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        if not self.currHP <= 0 and not self.getManager():
            self.healInterval = Sequence(Parallel(Func(self.showHpString, "+10% Damage!"), Func(self.setSuitStatusEffect, 'damageUp', modifier=10, mode='refreshModifier'))).start()
        else:
            pass


    def checkCompensation(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        if self.currHP < self.maxHP and not self.currHP <= 0 and not self.dna.name == 'hustle':
            self.healInterval = Sequence(Func(self.showHpString, "+5% Damage!"), Func(self.setSuitStatusEffect, 'lureResist', modifier=1), Func(self.setSuitStatusEffect, 'damageUp', modifier=5, mode='refreshModifier')).start()
        else:
            pass

    def checkCompensation2(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        if self.currHP < self.maxHP and not self.currHP <= 0:
            self.healInterval = Sequence(Parallel(ActorInterval(self, 'mob-mentality'), Func(self.showHpString, "+15% Damage!"), Func(self.makeDamageUp), Func(self.makeLureResist), Func(self.checkDamageUp, + 15)), Func(self.setNeutralAnimation)).start()
        else:
            pass

    def checkScabbard(self):
        hpCap = int(self.maxHP * self.hardMaxHP)

        projectedHP = self.getQueuedProjectedHPFull()

        if not self.getManager():
            healAmount = min(self.maxHP, max(0, hpCap - projectedHP))
        else:
            healAmount = min(200, max(0, hpCap - projectedHP))

        if healAmount > 0:
            self.addPendingQueuedHealing(healAmount)

        return Sequence(
            Parallel(
                Func(self.showHpTextNew, healAmount),
                Func(self.setHealthForMe, healAmount),
                Func(self.updateHealthBar, 0)
            )
        )

    def checkLimitedTimeOffer(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        rushJobs = (
            self.trapRushJob,
            self.lureRushJob,
            self.throwRushJob,
            self.squirtRushJob,
            self.zapRushJob,
            self.soundRushJob,
            self.dropRushJob
        )
        if self.currHP > 0 and any(rushJobs):
            if not self.getManager():
                if self.currHP >= (self.maxHP * self.hardMaxHP):
                    self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="OFFER EXPIRED!", colorCode=5),
                                                 Func(self.updateHealthBar, 0)).start()
                elif self.currHP > self.maxHP:
                    self.healInterval = Parallel(Func(self.showHpTextNew, x, text="OFFER EXPIRED", colorCode=5),
                                                 Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
                    self.addPendingQueuedHealing(x)
                else:
                    self.healInterval = Parallel(Func(self.showHpTextNew, self.maxHP, text="OFFER EXPIRED!", colorCode=5),
                                                 Func(self.setHealthForMe, self.maxHP), Func(self.updateHealthBar, 0)).start()
                    self.addPendingQueuedHealing(self.maxHP)
            else:
                if self.currHP >= (self.maxHP * self.hardMaxHP):
                    self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="OFFER EXPIRED!", colorCode=5),
                                                 Func(self.updateHealthBar, 0)).start()
                elif self.currHP + 450 > (self.maxHP * self.hardMaxHP):
                    self.healInterval = Parallel(Func(self.showHpTextNew, x, text="OFFER EXPIRED!", colorCode=5),
                                                 Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
                    self.addPendingQueuedHealing(x)
                else:
                    self.healInterval = Parallel(Func(self.showHpTextNew, 450, text="OFFER EXPIRED!", colorCode=5),
                                                 Func(self.setHealthForMe, 450), Func(self.updateHealthBar, 0)).start()
                    self.addPendingQueuedHealing(450)

    def checkInsuranceRounds(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.addInsuranceRounds, self.getInsuranceRounds() + num)).start()

    def checkContractedRounds(self, num):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        self.damageInterval = Parallel(Func(self.addContractedRounds, self.getContractedRounds() + num)).start()

    def checkLayoffs(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, -self.currHP, text="FIRED!", colorCode=4),
                                         Func(self.setHealthForMe, -self.currHP), Func(self.updateHealthBar, 0)).start()

    def checkContracted(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP > 0:
            if self.currHP >= (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, 0),
                                             Func(self.updateHealthBar, 0)).start()
            elif self.currHP + 95 > (self.maxHP * self.hardMaxHP):
                self.healInterval = Parallel(Func(self.showHpTextNew, x),
                                             Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
                self.addPendingQueuedHealing(x)
            else:
                self.healInterval = Parallel(Func(self.showHpTextNew, 95),
                                             Func(self.setHealthForMe, 95), Func(self.updateHealthBar, 0)).start()
                self.addPendingQueuedHealing(95)

    def checkContracted2(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP >= (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, 0),
                                         Func(self.updateHealthBar, 0)).start()
        elif self.currHP + 95 > (self.maxHP * self.hardMaxHP):
            self.healInterval = Parallel(Func(self.showHpTextNew, x),
                                         Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
            self.addPendingQueuedHealing(x)
        else:
            self.healInterval = Parallel(Func(self.showHpTextNew, 95),
                                         Func(self.setHealthForMe, 95), Func(self.updateHealthBar, 0)).start()
            self.addPendingQueuedHealing(95)

    def checkInsuranceScapegoatHP(self):
        hpCap = int(self.maxHP * self.hardMaxHP)

        projectedHP = self.getQueuedProjectedHPFull()

        healAmount = min(85, max(0, hpCap - projectedHP))

        if healAmount > 0:
            self.addPendingQueuedHealing(healAmount)

        return Sequence(
            Parallel(
                Func(self.showHpTextNew, healAmount),
                Func(self.setHealthForMe, healAmount),
                Func(self.updateHealthBar, 0)
            )
        )

    def checkRedundant(self):
        hpCap = int(self.maxHP * self.hardMaxHP)

        projectedHP = self.getQueuedProjectedHPFull()

        healAmount = min(325, max(0, hpCap - projectedHP))

        if healAmount > 0:
            self.addPendingQueuedHealing(healAmount)

        return Sequence(
            Parallel(
                Func(self.showHpTextNew, healAmount),
                Func(self.setHealthForMe, healAmount),
                Func(self.updateHealthBar, 0)
            )
        )

    def checkOilRain(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        x = int((self.maxHP * self.hardMaxHP) - self.currHP)
        if self.currHP > 0:
            if self.currHP >= (self.maxHP * self.hardMaxHP) and not self.dna.name == 'foreman' and not self.dna.name == 'ovt' and not self.dna.name == 'supervis' and not self.dna.name == 'clerk' and not self.dna.name == 'foreman' and not self.dna.name == 'clubpres':
                self.healInterval = Parallel(Func(self.showHpTextNew, 0, colorCode=1),
                                             Func(self.updateHealthBar, 0)).start()
            elif self.currHP + 100 > (self.maxHP * self.hardMaxHP) and not self.dna.name == 'foreman' and not self.dna.name == 'ovt' and not self.dna.name == 'clerk' and not self.dna.name == 'supervis' and not self.dna.name == 'foreman' and not self.dna.name == 'clubpres':
                self.healInterval = Parallel(Func(self.showHpTextNew, x),
                                             Func(self.setHealthForMe, x), Func(self.updateHealthBar, 0)).start()
                self.addPendingQueuedHealing(x)
            else:
                self.healInterval = Parallel(Func(self.showHpTextNew, 100),
                                             Func(self.setHealthForMe, 100), Func(self.updateHealthBar, 0)).start()
                self.addPendingQueuedHealing(100)

    def checkInsuranceHP(self):
        hpCap = int(self.maxHP * self.hardMaxHP)

        projectedHP = self.getQueuedProjectedHPFull()

        healAmount = min(50, max(0, hpCap - projectedHP))

        if healAmount > 0:
            self.addPendingQueuedHealing(healAmount)

        return Sequence(
            Parallel(
                Func(self.showHpTextNew, healAmount),
                Func(self.setHealthForMe, healAmount),
                Func(self.updateHealthBar, 0)
            )
        )

    def checkExtraTip(self):
        hpCap = int(self.maxHP * self.hardMaxHP)

        projectedHP = self.getQueuedProjectedHPFull()

        healAmount = min(225, max(0, hpCap - projectedHP))

        if healAmount > 0:
            self.addPendingQueuedHealing(healAmount)

        return Sequence(
            Parallel(
                Func(self.showHpTextNew, healAmount, text="+10% Damage!", colorCode=1),
                Func(self.setHealthForMe, healAmount),
                Func(self.updateHealthBar, 0)
            )
        )


    def checkLifeInsurance(self):
        hpCap = int(self.maxHP * self.hardMaxHP)

        projectedHP = self.getQueuedProjectedHPFull()

        healAmount = min(225, max(0, hpCap - projectedHP))

        if healAmount > 0:
            self.addPendingQueuedHealing(healAmount)

        if self.getActualLevel() == 25:
            return Sequence(
                Parallel(Func(self.setSuitStatusEffect, 'damageUp', modifier=10, mode='refreshModifier'),
                    Func(self.showHpTextNew, healAmount, text="+10% Damage!", colorCode=1),
                    Func(self.setHealthForMe, healAmount),
                    Func(self.updateHealthBar, 0)
                )
            )
        else:
            return Sequence(
                Parallel(Func(self.setSuitStatusEffect, 'damageUp', modifier=5, mode='refreshModifier'),
                    Func(self.showHpTextNew, healAmount, text="+5% Damage!", colorCode=1),
                    Func(self.setHealthForMe, healAmount),
                    Func(self.updateHealthBar, 0)
                )
            )

    def checkCompensationDividend(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 0, text="+5% Damage!", colorCode=1), Func(self.setSuitStatusEffect, 'damageUp', modifier=5, mode='refreshModifier'), Func(self.updateHealthBar, 0)).start()

    def checkCompensationForeman(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 225, text="+35% Damage!", colorCode=1), Func(self.setSuitStatusEffect, 'damageUp', modifier=35, mode='refreshModifier'), Func(self.setHealthForMe, 225), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(225)

    def checkCompensation2(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 450, text="+70% Damage!", colorCode=1), Func(self.setSuitStatusEffect, 'damageUp', modifier=70, mode='refreshModifier'), Func(self.setHealthForMe, 450), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(450)

    def checkCompensation3(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 675, text="+105% Damage!", colorCode=1), Func(self.setSuitStatusEffect, 'damageUp', modifier=105, mode='refreshModifier'), Func(self.setHealthForMe, 675), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(675)

    def checkCompensation4(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 900, text="+140% Damage!", colorCode=1), Func(self.setHealthForMe, 900), Func(self.setSuitStatusEffect, 'damageUp', modifier=140, mode='refreshModifier'), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(900)

    def checkCompensation5(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 1125, text="+175% Damage!", colorCode=1), Func(self.setSuitStatusEffect, 'damageUp', modifier=175, mode='refreshModifier'), Func(self.setHealthForMe, 1125), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(1125)

    def checkCompensationDividendOLD(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 200, text="+5% Damage!", colorCode=1), Func(self.setSuitStatusEffect, 'damageUp', modifier=5, mode='refreshModifier'), Func(self.setHealthForMe, 200), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(200)

    def checkCompensationDividend2(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 400, text="+10% Damage!", colorCode=1), Func(self.setSuitStatusEffect, 'damageUp', modifier=10, mode='refreshModifier'), Func(self.setHealthForMe, 400), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(400)

    def checkCompensationDividend3(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 600, text="+15% Damage!", colorCode=1), Func(self.setSuitStatusEffect, 'damageUp', modifier=15, mode='refreshModifier'), Func(self.setHealthForMe, 600), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(600)

    def checkCompensationDividend4(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 800, text="+20% Damage!", colorCode=1), Func(self.setHealthForMe, 800), Func(self.setSuitStatusEffect, 'damageUp', modifier=20, mode='refreshModifier'), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(800)

    def checkCompensationDividend5(self):
        if self.healInterval:
            self.healInterval.finish()
            self.healInterval = None
        self.healInterval = Parallel(Func(self.showHpTextNew, 1000, text="+25% Damage!", colorCode=1), Func(self.setSuitStatusEffect, 'damageUp', modifier=25, mode='refreshModifier'), Func(self.setHealthForMe, 1000), Func(self.updateHealthBar, 0)).start()
        self.addPendingQueuedHealing(1000)

    def checkInsuranceCountdown(self):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.getInsuranceRounds() - 1 == 0:
            self.damageInterval = Parallel(Func(self.removeInsured))
        elif self.getInsuranceRounds() > 0:
            self.damageInterval = Parallel(Func(self.addInsuranceRounds, self.getInsuranceRounds() - 1)).start()
        else:
            pass

    def checkContractedCountdown(self):
        if self.damageInterval:
            self.damageInterval.finish()
            self.damageInterval = None
        if self.getContractedRounds() - 1 == 0:
            self.damageInterval = Parallel(Func(self.removeContracted))
        elif self.getContractedRounds() > 0:
            self.damageInterval = Parallel(Func(self.addContractedRounds, self.getContractedRounds() - 1)).start()
        else:
            pass

    def loopSyncedLuredAnimations(self):
        if self.currHP > 0:
            suitAnim = 'lured'
            suitRate = 1.0 + (self.battleSpeed * 0.1)

            suitDuration = self.getDuration(suitAnim)

            if suitDuration <= 0:
                suitDuration = 1.0

            adjustedSuitDuration = suitDuration / float(suitRate)

            self.setPlayRate(suitRate, suitAnim)
            self.loop(suitAnim)

            for headPart in self.animatedHeadParts:
                if not headPart or headPart.isEmpty():
                    continue

                headAnim = 'neutral-lured'

                if headAnim not in headPart.getAnimNames():
                    continue

                if self.dna.name in ('hroller', 'hrollers', 'hroller2'):
                    fromFrame = 0
                    toFrame = 22
                else:
                    fromFrame = 0
                    toFrame = headPart.getNumFrames(headAnim) - 1

                headFrameRate = headPart.getFrameRate(headAnim)

                if headFrameRate <= 0:
                    headFrameRate = 24.0

                frameCount = (toFrame - fromFrame) + 1

                headLoopDuration = (
                    frameCount / float(headFrameRate)
                )

                headRate = (
                    headLoopDuration /
                    adjustedSuitDuration
                )
                if not self.dna.name in ['erfit', 'erclaim'] and not SuitDNA.getSuitBodyType(self.dna.name) in ['b', 'c']:
                    headPart.setPlayRate(
                        (headRate * 2),
                        headAnim
                    )

                headPart.loop(
                    headAnim,
                    restart=1,
                    fromFrame=fromFrame,
                    toFrame=toFrame
                )
            else:
                pass

    def playSyncedLuredAnimations(self):
        suitAnim = 'lured'
        headAnim = 'neutral-lured'

        suitDuration = self.getDuration(suitAnim)

        if suitDuration <= 0:
            suitDuration = 1.0

        # Keep your normal battle-speed adjustment.
        suitRate = 1.0 + (self.battleSpeed * 0.1)
        adjustedSuitDuration = suitDuration / float(suitRate)

        track = Parallel()

        # Play the body animation once.
        bodyTrack = Sequence(
            Func(self.setPlayRate, suitRate, suitAnim),
            Func(self.play, suitAnim),
            Wait(adjustedSuitDuration),
            Func(self.loop, suitAnim)
        )

        track.append(bodyTrack)

        # Match every animated head to the body's adjusted duration.
        for headPart in self.animatedHeadParts:
            if headPart.isEmpty():
                continue

            if headAnim not in headPart.getAnimNames():
                continue

            headDuration = headPart.getDuration(headAnim)

            if headDuration <= 0:
                continue

            headRate = headDuration / float(adjustedSuitDuration)

            headTrack = Sequence(
                Func(headPart.setPlayRate, headRate, headAnim),
                Func(headPart.play, headAnim),
                Wait(adjustedSuitDuration),
                Func(headPart.loop, headAnim)
            )

            track.append(headTrack)

        track.start()

    def setNeutralAnimationHead(self):
        if self.getDizzy() or self.getDizzy3() or self.hasSuitStatusEffect('sleepy') or self.hasSuitStatusEffect('sued'):
            self.loopSyncedLuredAnimations()
        else:
            if self.dna.name == 'hroller' and (float(self.currHP) / float(self.maxHP) <= 0.25):
                for headPart in self.animatedHeadParts: Sequence(Func(headPart.loop, 'neutral-hurt', fromFrame=0,
                                                                      toFrame=22)
                                                                 ).start()
            elif self.dna.name == 'hroller2' and (float(self.currHP) / float(self.maxHP) <= 0.25):
                for headPart in self.animatedHeadParts: Sequence(Func(headPart.loop, 'neutral-hurt', fromFrame=0,
                                                                      toFrame=22)
                                                                 ).start()
            elif self.dna.name == 'hrollers' and (float(self.currHP) / float(self.maxHP) <= 0.25):
                for headPart in self.animatedHeadParts: Sequence(Func(headPart.loop, 'neutral-hurt', fromFrame=0,
                                                                      toFrame=22)
                                                                 ).start()
            else:
                for headPart in self.animatedHeadParts: Sequence(Func(headPart.loop, 'neutral%s' % (
                                                                 '-hurt' if float(self.currHP) / float(
                                                                     self.maxHP) <= 0.25 else '',))
                                                                 ).start()
            if self.dna.name == 'videog':
                for headPart in self.animatedHeadParts:
                    if float(self.currHP) / float(self.maxHP) <= 0.25:
                        texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer3.png')
                        Sequence(Func(headPart.setTexture, texture, 1)).start()
            if self.dna.name == 'bcaster':
                for headPart in self.animatedHeadParts:
                    if float(self.currHP) / float(self.maxHP) <= 0.25:
                        texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer3.png')
                        Sequence(Func(headPart.setTexture, texture, 1)).start()
            for headPart in self.animatedHeadParts: Sequence(
                Func(headPart.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()

    def setNeutralAnimationHeadTrap(self):
        if self.hasSuitStatusEffect('sleepy') or self.hasSuitStatusEffect('sued'):
            if self.hasSuitStatusEffect('sleepy'):
                Func(self.setChatAbsoluteSpecial, '. . . Z Z Z . . .', CFThought).start()
                self.loopSyncedLuredAnimations()
            else:
                self.loopSyncedLuredAnimations()
        elif self.dna.name == 'hroller' and (float(self.currHP) / float(self.maxHP) <= 0.25):
            for headPart in self.animatedHeadParts: Sequence(Func(headPart.loop, 'neutral-hurt', fromFrame=0,
                                                                      toFrame=22)
                                                                 ).start()
        elif self.dna.name == 'hroller2' and (float(self.currHP) / float(self.maxHP) <= 0.25):
            for headPart in self.animatedHeadParts: Sequence(Func(headPart.loop, 'neutral-hurt', fromFrame=0,
                                                                      toFrame=22)
                                                                 ).start()
        elif self.dna.name == 'hrollers' and (float(self.currHP) / float(self.maxHP) <= 0.25):
            for headPart in self.animatedHeadParts: Sequence(Func(headPart.loop, 'neutral-hurt', fromFrame=0,
                                                                      toFrame=22)
                                                                 ).start()
        else:
            for headPart in self.animatedHeadParts: Sequence(Func(headPart.loop, 'neutral%s' % (
                                                                 '-hurt' if float(self.currHP) / float(
                                                                     self.maxHP) <= 0.25 else '',))
                                                                 ).start()
        if self.dna.name == 'videog':
            for headPart in self.animatedHeadParts:
                if float(self.currHP) / float(self.maxHP) <= 0.25:
                        texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer3.png')
                        Sequence(Func(headPart.setTexture, texture, 1)).start()
        if self.dna.name == 'bcaster':
            for headPart in self.animatedHeadParts:
                    if float(self.currHP) / float(self.maxHP) <= 0.25:
                        texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer3.png')
                        Sequence(Func(headPart.setTexture, texture, 1)).start()
        for headPart in self.animatedHeadParts: Sequence(
                Func(headPart.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()
        Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',)), Func(self.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()
        
    def makeBlendInterval(self, blendAnim):
        projectedHP = (
            self.currHP
            + self._pendingQueuedHealing
            - self._pendingQueuedDamage
        )

        if projectedHP <= float(self.maxHP * 0.25):
            return Func(self.setNeutralAnimationDrop)

        elif (
                self.dna.name == 'clerk'
                and self.getActualLevel() in (24, 25)
        ):
            targetAnim = 'pace'
        elif (
                self.dna.name == 'psetter'
        ):
            targetAnim = 'pace'

        elif (
                self.dna.name == 'sgoat'
                and self.hasSuitStatusEffect('enraged')
        ):
            targetAnim = 'neutral-enraged'

        elif self.dna.name in (
                'hroller2',
                'hrollers',
                'videog',
                'director',
                'fmaker',
                'cinema',
                'choreo',
                'mplayer',
                'mh2',
                'cnd2',
                'mplayers',
                'std2',
                'bcaster'
        ):
            targetAnim = 'rolled'

        elif self.dna.name == 'hroller' and self.hasSuitStatusEffect('silhouetteShielding'):
            targetAnim = 'rolled'
        elif self.hasSuitStatusEffect('rolledNeutral'):
            targetAnim = 'rolled'
        elif projectedHP >= float(self.maxHP * 1.5):
            targetAnim = 'neutral-unstable'
        elif self.hasSuitStatusEffect('brokenConnection'):
            targetAnim = 'neutral-unstable'
        elif self.hasSuitStatusEffect('contingencyOverride'):
            targetAnim = 'neutral-override'
        elif self.hasSuitStatusEffect('contingencyOverrideBroken'):
            targetAnim = 'neutral-unstable'
        elif self.hasSuitStatusEffect('glitched'):
            targetAnim = 'neutral-override'
        elif self.hasSuitStatusEffect('semi-glitched'):
            targetAnim = 'neutral-unstable'

        else:
            return Func(self.setNeutralAnimationDrop)

        return Sequence(
            # Let the damage/reaction animation reach its ending pose.
            ActorInterval(
                self,
                blendAnim,
                endTime=0
            ),

            Func(self.enableBlend),

            # Both animations must be actively controlled during the blend.
            Func(self.loop, blendAnim),
            Func(self.loop, targetAnim),

            Parallel(LerpAnimInterval(
                self,
                duration=0.25,
                startAnim=blendAnim,
                endAnim=targetAnim,
                startWeight=0.0,
                endWeight=1.0,
                blendType='easeInOut'
            ), ActorInterval(
                self,
                targetAnim,
                startTime=0, endTime=0
            )),

            Func(self.disableBlend),

            # Ensure the intended neutral animation remains playing.
            Func(self.setNeutralAnimationDrop)
        )

    def setNeutralAnimationAttack(self):
        self.setNeutralAnimationDrop()

    def setNeutralAnimation(self):
        if self.getDizzy() or self.getDizzy3():
            self.loopSyncedLuredAnimations()
        elif self.dna.name == 'clerk' and (self.getActualLevel() in [24, 25]):
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'pace'), Func(self.loop, 'pace')
                     ).start()
        elif self.hasSuitStatusEffect('enraged') and self.dna.name == 'sgoat':
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'neutral-enraged'), Func(self.loop, 'neutral-enraged')
                     ).start()
        elif self.hasSuitStatusEffect('silhouetteImmune') and self.hasSuitStatusEffect('highRollerPhase3'):
            Sequence(Func(self.loop, 'highroller-neutral-levitate-loop')
                     ).start()
        elif self.hasSuitStatusEffect('rolledNeutral'):
            Sequence(Func(self.loop, 'rolled')
                     ).start()
        elif self.hasSuitStatusEffect('silhouetteShielding'):
            Sequence(Func(self.loop, 'rolled')
                                 ).start()
        elif self.hasSuitStatusEffect('glitched'):
            Sequence(Func(self.loop, 'neutral-override')
                                 ).start()
        elif self.hasSuitStatusEffect('semi-glitched'):
            Sequence(Func(self.loop, 'neutral-unstable')
                                 ).start()
        elif self.hasSuitStatusEffect('vulnerable') and self.dna.name == 'hroller':
            Sequence(Func(self.loop, 'neutral2%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                     ).start()
        elif self.hasSuitStatusEffect('brokenConnection'):
            Sequence(Func(self.loop, 'neutral-unstable')
                                 ).start()
        elif self.hasSuitStatusEffect('contingencyOverride'):
            Sequence(Func(self.loop, 'neutral-override')
                                 ).start()
        elif self.hasSuitStatusEffect('contingencyOverrideBroken'):
            Sequence(Func(self.loop, 'neutral-unstable')
                                 ).start()
        elif self.hasSuitStatusEffect('zapped') and not self.dna.name in ['mh2', 'std2', 'cnd2', 'videog', 'bcaster', 'hroller2', 'hroller', 'hrollers', 'psetter']:
            Sequence(Func(self.loop, 'neutral-unstable')
                     ).start()
        elif float(self.currHP) > float(self.maxHP * 1.5) and not self.dna.name in ['mh2', 'std2', 'cnd2', 'videog', 'bcaster', 'hroller2', 'hroller', 'hrollers']:
            Sequence(Func(self.loop, 'neutral-unstable', fromFrame=70, toFrame=80)
                     ).start()
        else:
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',)), Func(self.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()
        self.setNeutralAnimationHead()

    def setNeutralAnimationAdjustInterval(self):
        if self.getDizzy() or self.getDizzy3():
            self.loopSyncedLuredAnimations()
        elif self.style.name == 'mh2':
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.style.name == 'std2':
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.style.name == 'hrollers':
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.style.name == 'cinema':
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.style.name == 'choreo':
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.style.name == 'videog':
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.style.name == 'bcaster':
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.style.name == 'director':
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.style.name == 'fmaker':
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'rolled'), Func(self.loop, 'rolled')
                     ).start()
        elif self.dna.name == 'clerk' and (self.getActualLevel() in [24, 25]):
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'pace'), Func(self.loop, 'pace')
                     ).start()
        elif self.hasSuitStatusEffect('enraged') and self.dna.name == 'sgoat':
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'neutral-enraged'), Func(self.loop, 'neutral-enraged')
                     ).start()
        elif self.hasSuitStatusEffect('silhouetteImmune') and not self.dna.name == 'hroller' and not self.dna.name == 'wtapper' and not self.dna.name == 'videog' and self.hasSuitStatusEffect('highRollerPhase3'):
            Sequence(Func(self.loop, 'highroller-neutral-levitate-loop')
                     ).start()
        elif self.hasSuitStatusEffect('glitched'):
            Sequence(Func(self.loop, 'neutral-override')
                                 ).start()
        elif self.hasSuitStatusEffect('semi-glitched'):
            Sequence(Func(self.loop, 'neutral-unstable')
                                 ).start()
        elif self.isDanceSession:
            Sequence(Func(self.loop, 'rolled')
                     ).start()
        elif self.hasSuitStatusEffect('vulnerable') and self.dna.name == 'hroller':
            Sequence(Func(self.loop, 'neutral2%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                     ).start()
        elif self.hasSuitStatusEffect('contingencyOverride'):
            Sequence(Func(self.loop, 'neutral-override')
                                 ).start()
        elif self.hasSuitStatusEffect('silhouetteShielding'):
            Sequence(Func(self.loop, 'rolled')
                                 ).start()
        elif self.hasSuitStatusEffect('rolledNeutral'):
            Sequence(Func(self.loop, 'rolled')
                     ).start()
        elif self.hasSuitStatusEffect('contingencyOverrideBroken'):
            Sequence(Func(self.loop, 'neutral-unstable')
                                 ).start()
        elif self.hasSuitStatusEffect('zapped') and not self.dna.name in ['mh2', 'std2', 'cnd2', 'videog', 'bcaster', 'hroller2', 'hroller', 'hrollers', 'psetter']:
            Sequence(Func(self.loop, 'neutral-unstable')
                     ).start()
        elif self.hasSuitStatusEffect('brokenConnection'):
            Sequence(Func(self.loop, 'neutral-unstable')
                                         ).start()
        elif float(self.currHP) > float(self.maxHP * 1.5) and not self.dna.name in ['mh2', 'std2', 'cnd2', 'videog', 'bcaster', 'hroller2', 'hroller', 'hrollers']:
            Sequence(Func(self.loop, 'neutral-unstable', fromFrame=70, toFrame=80)
                     ).start()
        else:
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',)), Func(self.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()
        self.setNeutralAnimationHead()

    def setNeutralAnimationDrop(self):
        if self.hasSuitStatusEffect('sleepy'):
            if self.currHP > 0:
                Sequence(
                # Let the damage/reaction animation reach its ending pose.
                ActorInterval(
                    self,
                    'neutral2',
                    endTime=0
                ),

                Func(self.enableBlend),

                # Both animations must be actively controlled during the blend.
                Func(self.loop, 'neutral2'),
                Func(self.loop, 'lured'),

                Parallel(LerpAnimInterval(
                    self,
                    duration=0.25,
                    startAnim='neutral',
                    endAnim='lured',
                    startWeight=0.0,
                    endWeight=1.0,
                    blendType='easeInOut'
                ), ActorInterval(
                    self,
                    'lured',
                    startTime=0, endTime=0
                )),

                Func(self.disableBlend),

                # Ensure the intended neutral animation remains playing.
                Func(self.loopSyncedLuredAnimations)
            ).start()
        elif self.getDizzy() or self.getDizzy3():
            # if self.currHP > 0:
            #     Sequence(
            #     # Let the damage/reaction animation reach its ending pose.
            #     ActorInterval(
            #         self,
            #         'neutral',
            #         endTime=0
            #     ),

            #     Func(self.enableBlend),

            #     # Both animations must be actively controlled during the blend.
            #     Func(self.loop, 'neutral2'),
            #     Func(self.loop, 'lured'),

            #     Parallel(LerpAnimInterval(
            #         self,
            #         duration=0.25,
            #         startAnim='neutral2',
            #         endAnim='lured',
            #         startWeight=0.0,
            #         endWeight=1.0,
            #         blendType='easeInOut'
            #     ), ActorInterval(
            #         self,
            #         'lured',
            #         startTime=0, endTime=0
            #     )),

            #     Func(self.disableBlend),

            #     # Ensure the intended neutral animation remains playing.
            #     Func(self.loopSyncedLuredAnimations)
            # ).start()
            self.loopSyncedLuredAnimations()
        elif self.hasSuitStatusEffect('brokenConnection'):
            Sequence(Func(self.loop, 'neutral-unstable')
                                         ).start()
        elif self.dna.name == 'clerk' and (self.getActualLevel() in [24, 25]):
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'pace'), Func(self.loop, 'pace')
                     ).start()
        elif self.hasSuitStatusEffect('glitched'):
            Sequence(Func(self.loop, 'neutral-override')
                                 ).start()
        elif self.hasSuitStatusEffect('semi-glitched'):
            Sequence(Func(self.loop, 'neutral-unstable')
                                 ).start()
        elif self.hasSuitStatusEffect('enraged') and self.dna.name == 'sgoat':
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'neutral-enraged'), Func(self.loop, 'neutral-enraged')
                     ).start()
        elif self.hasSuitStatusEffect('silhouetteImmune') and not self.dna.name == 'hroller' and not self.dna.name == 'wtapper' and not self.dna.name == 'videog' and self.hasSuitStatusEffect('highRollerPhase3'):
            Sequence(Func(self.loop, 'highroller-neutral-levitate-loop')
                     ).start()
        elif self.hasSuitStatusEffect('vulnerable') and self.dna.name == 'hroller':
            Sequence(
                Func(self.loop, 'neutral2%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                ).start()
        elif float(self.currHP) > float(self.maxHP * 1.5) and not self.dna.name in ['mh2', 'std2', 'cnd2', 'videog', 'bcaster', 'hroller2', 'hroller', 'hrollers']:
            Sequence(Func(self.loop, 'neutral-unstable', fromFrame=70, toFrame=80)
                     ).start()
        elif float(self.currHP) > float(self.maxHP * 1.5) and self.hasSuitStatusEffect('rolledNeutral'):
            Sequence(Func(self.loop, 'rolled')
                                 ).start()
        elif not float(self.currHP) / float(self.maxHP) <= 0.25 and self.hasSuitStatusEffect('rolledNeutral'):
            Sequence(Func(self.loop, 'rolled')
                                 ).start()
        elif self.hasSuitStatusEffect('contingencyOverride'):
            Sequence(Func(self.loop, 'neutral-override')
                                 ).start()
        elif self.hasSuitStatusEffect('contingencyOverrideBroken'):
            Sequence(Func(self.loop, 'neutral-unstable')
                                 ).start()
        else:
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',)),
                     Func(self.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                     ).start()

    def setNeutralAnimationRolled(self):
        if self.getDizzy() or self.getDizzy3():
            self.loopSyncedLuredAnimations()
        else:
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'rolled'), Func(self.loop, 'rolled')
            ).start()
        self.setNeutralAnimationHead()

    def setNeutralAnimationTrap(self):
        if self.hasSuitStatusEffect('enraged') and self.dna.name == 'sgoat':
            Sequence(Func(self.setPlayRate, 1 + (self.battleSpeed * .1), 'neutral-enraged'), Func(self.loop, 'neutral-enraged')
                     ).start()
        elif self.hasSuitStatusEffect('glitched'):
            Sequence(Func(self.loop, 'neutral-override')
                                 ).start()
        elif self.hasSuitStatusEffect('silhouetteShielding'):
            Sequence(Func(self.loop, 'rolled')
                                 ).start()
        elif self.hasSuitStatusEffect('rolledNeutral'):
            Sequence(Func(self.loop, 'rolled')
                     ).start()
        elif self.hasSuitStatusEffect('semi-glitched'):
            Sequence(Func(self.loop, 'neutral-unstable')
                                 ).start()
        elif self.hasSuitStatusEffect('contingencyOverride'):
            Sequence(Func(self.loop, 'neutral-override')
                                 ).start()
        elif self.hasSuitStatusEffect('contingencyOverrideBroken'):
            Sequence(Func(self.loop, 'neutral-unstable')
                                 ).start()
        elif self.hasSuitStatusEffect('silhouetteImmune') and not self.dna.name == 'hroller' and not self.dna.name == 'wtapper' and not self.dna.name == 'videog' and self.hasSuitStatusEffect('highRollerPhase3'):
            Sequence(Func(self.loop, 'highroller-neutral-levitate-loop')
                     ).start()
        elif self.hasSuitStatusEffect('vulnerable') and self.dna.name == 'hroller':
            Sequence(Func(self.loop, 'neutral2%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
                     ).start()
        elif self.hasSuitStatusEffect('brokenConnection'):
            Sequence(Func(self.loop, 'neutral-unstable')
                                         ).start()
        elif self.hasSuitStatusEffect('zapped') and not self.dna.name in ['mh2', 'std2', 'cnd2', 'videog', 'bcaster', 'hroller2', 'hroller', 'hrollers', 'psetter']:
            Sequence(Func(self.loop, 'neutral-unstable')
                     ).start()
        elif float(self.currHP) > float(self.maxHP * 1.5) and not self.dna.name in ['mh2', 'std2', 'cnd2', 'videog', 'bcaster', 'hroller2', 'hroller', 'hrollers']:
            Sequence(Func(self.loop, 'neutral-unstable', fromFrame=70, toFrame=80)
                     ).start()
        else:
            Sequence(Func(self.loop, 'neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',))
            ).start()
        self.setNeutralAnimationHeadTrap()

    def addPendingQueuedHealing(self, amount):
        if not hasattr(self, '_pendingQueuedHealing'):
            self._pendingQueuedHealing = 0
        self._pendingQueuedHealing += int(amount)

    def clearPendingQueuedHealing(self, amount):
        if not hasattr(self, '_pendingQueuedHealing'):
            self._pendingQueuedHealing = 0
        self._pendingQueuedHealing -= int(amount)
        if self._pendingQueuedHealing < 0:
            self._pendingQueuedHealing = 0

    def getQueuedProjectedHPFull(self):
        damage = getattr(self, '_pendingQueuedDamage', 0)
        healing = getattr(self, '_pendingQueuedHealing', 0)
        return self.currHP - (damage + healing)

    def clearPendingQueuedHealingAll(self):
        self._pendingQueuedHealing = 0
        self._pendingQueuedDeath = False

    def setPendingQueuedDesperation(self, value):
        self._pendingQueuedDesperation = bool(value)

    def getProjectedDesperation(self):
        return getattr(self, '_pendingQueuedDesperation', False) or self.isDesperation

    def clearPendingQueuedDesperation(self):
        self._pendingQueuedDesperation = False

    def makePlayByPlayTextInterval(self, pbpText, displayName, attackDuration):
        pending = getattr(self, '_pendingQueuedDamage', 0)
        projectedHP = self.currHP + (self._pendingQueuedHealing - self._pendingQueuedDamage)

        if projectedHP > float(self.maxHP * 1.5):
            playByPlayInterval = pbpText.getShowIntervalOvercharged(displayName, attackDuration)
        elif projectedHP > float(self.maxHP):
            playByPlayInterval = pbpText.getShowIntervalOverhealed(displayName, attackDuration)
        else:
            playByPlayInterval = pbpText.getShowInterval(displayName, attackDuration)

        return playByPlayInterval

    def makePlayByPlayTextCheatInterval(self, pbpText, displayName, attackDuration):
        pending = getattr(self, '_pendingQueuedDamage', 0)
        projectedHP = float(self.getQueuedProjectedHPFull())

        if projectedHP > float(self.maxHP * 1.5):
            playByPlayInterval = pbpText.getShowIntervalCheatOvercharged(displayName, attackDuration)
        elif projectedHP > float(self.maxHP):
            playByPlayInterval = pbpText.getShowIntervalCheatOverhealed(displayName, attackDuration)
        else:
            playByPlayInterval = pbpText.getShowIntervalCheatRed(displayName, attackDuration)

        return playByPlayInterval

    def makePlayByPlayTextLegallyBoundInterval(self, pbpText, attackDuration):
        if self.getProjectedDesperation():
            playByPlayInterval = pbpText.getShowIntervalDesc(
                "Legally Bound Toons take 28 damage per round!", attackDuration)
        else:
            playByPlayInterval = pbpText.getShowIntervalDesc(
                "Legally Bound Toons take 20 damage per round!", attackDuration)

        return playByPlayInterval

    def makePlayByPlayTextLiquidationEventInterval(self, pbpText, attackDuration):
        if self.getProjectedDesperation():
            playByPlayInterval = pbpText.getShowIntervalDesc(
                "Liquidated Toons take 42 extra damage per round!", attackDuration)
        else:
            playByPlayInterval = pbpText.getShowIntervalDesc(
                "Liquidated Toons take 30 extra damage per round!", attackDuration)

        return playByPlayInterval

    def makePlayByPlayTextCourtRecordInterval(self, pbpText, attackDuration):
        if self.getProjectedDesperation():
            playByPlayInterval = pbpText.getShowIntervalDesc(
                'Due to an illegal action, this toon takes 70 damage!',
                attackDuration
            )
        else:
            playByPlayInterval = pbpText.getShowIntervalDesc(
                'Due to an illegal action, this toon takes 50 damage!',
                attackDuration
            )

        return playByPlayInterval

    def makePlayByPlayTextBurnedInterval(self, pbpText, attackDuration):
        if self.getProjectedDesperation():
            playByPlayInterval = pbpText.getShowIntervalDesc(
                'Surged Toons take 42 extra damage per round!',
                attackDuration
            )
        else:
            playByPlayInterval = pbpText.getShowIntervalDesc(
                'Surged Toons take 30 extra damage per round!',
                attackDuration
            )

        return playByPlayInterval

    def makePlayByPlayTextInflationInterval(self, pbpText, attackDuration):
        if self.getProjectedDesperation():
            playByPlayInterval = pbpText.getShowIntervalDesc(
                'Due to an overinflated budget this toon takes 70 damage!',
                attackDuration
            )
        else:
            playByPlayInterval = pbpText.getShowIntervalDesc(
                'Due to an overinflated budget this toon takes 50 damage!',
                attackDuration
            )

        return playByPlayInterval

    def makePlayByPlayTextBustedInterval(self, pbpText, attackDuration):
        if self.getProjectedDesperation():
            playByPlayInterval = pbpText.getShowIntervalDesc(
                'Employed Toons are forced to take 35 damage every round!',
                attackDuration
            )
        else:
            playByPlayInterval = pbpText.getShowIntervalDesc(
                'Employed Toons are forced to take 25 damage every round!',
                attackDuration
            )

        return playByPlayInterval

    def setPendingQueuedLured(self, value):
        self._pendingQueuedLured = bool(value)

    def getProjectedLured(self):
        return getattr(self, '_pendingQueuedLured', False)

    def clearPendingQueuedLured(self):
        self._pendingQueuedLured = False

    def setPendingQueuedRevive(self, value):
        self._pendingQueuedRevive = bool(value)

    def getProjectedRevive(self):
        return getattr(self, '_pendingQueuedRevive', False)

    def clearPendingQueuedRevive(self):
        self._pendingQueuedRevive = False

    def makeCogStepBackInterval(self, battle):
        if self.getProjectedLured():
            return self.__createSuitResetPosTrack(battle)
        else:
            return Sequence(Func(self.setNeutralAnimationTrap))

    def makeCogStepBackDeathInterval(self, battle):
        if self.getProjectedLured():
            return self.__createSuitResetPosTrack(battle)
        else:
            return Sequence()

    def checkCogLured(self, battle):
        if self.luredInterval != None:
            self.luredInterval.finish()
           # del self.playByPlayInterval
        if self.getDizzy():
            self.luredInterval = self.__createSuitResetPosTrack(battle)
            self.luredInterval.start()
        else:
            self.luredInterval = Func(self.setNeutralAnimationTrap)
            self.luredInterval.start()

    def checkCogLuredDeath(self, battle):
        if self.luredInterval != None:
            self.luredInterval.finish()
         #   del self.playByPlayInterval
        if self.getDizzy():
            self.luredInterval = self.__createSuitResetPosTrack(battle)
            self.luredInterval.start()
        else:
            pass

    def makeCogLuredDeathInterval(self, battle):
        if self.luredInterval is not None:
            self.luredInterval.finish()
            self.luredInterval = None

        if self.getDizzy():
            self.luredInterval = self.__createSuitResetPosTrack(battle)
        else:
            self.luredInterval = Sequence()

        return self.luredInterval

    def generateHeadAnims(self, path, cActor, additionalAnims=[]):
        anims = ['neutral', 'death', 'grunt', 'murmur', 'question', 'statement', 'neutral-hurt', 'neutral-lured', 
                 'neutral_b', 'death_b', 'grunt_b', 'murmur_b', 'question_b', 'statement_b', 'neutral-hurt_b', 'neutral-lured_b', 'stun_b', 
                 'fusiondance-shot1', 'fusiondance-shot2', 'fusiondance-shot3', 'fusiondance-shot4', 'fusiondance-shot5', 'mouth-drop',
                 'stun', 'enraged', 'sacrifice-cog', 'summon-cog', 'insurance', 'bellow', 'ace-in-the-hole', 'wheelspin', 'healing-bell', 'revvedup',
                 'scabbard', 'sparkplug', 'throttle', 'throttle2', 'mouthdrop', 'dive', 'bust', 
                 'emergeHead', 'exitWater', 'underwaterHit', 'gamble', 'cigar-smoke', 'gsnap', 'overclocked',
                 'come-on', 'zero']
        for anim in additionalAnims:
            anims.append(anim)
        animList = {}
        for anim in anims:
            animList[anim] = path + anim + '.bam'
        cActor.loadAnims(animList)

    def setVirtual(self, flag, isVirtual = 1):
        SuitBase.SuitBase.setVirtual(self, flag)
        self.virtual = isVirtual
        if self.virtual:
            actorNode = self.find('**/__Actor_modelRoot')
            actorCollection = actorNode.findAllMatches('*')
            parts = ()
            for thingIndex in xrange(0, actorCollection.getNumPaths()):
                thing = actorCollection[thingIndex]
                if thing.getName() not in ('joint_attachMeter', 'joint_shadow', 'joint_nameTag', 'def_nameTag'):
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

    def setVulnerabilityMultiplier(self, vulnerability):
        self.vulnerabilityMult = vulnerability

    def getVulnerabilityMultiplier(self):
        return self.vulnerabilityMult

    def setDizzy3(self, dizzy):
        p1 = Point3(0)
        p2 = Point3(0)
        #head = self.find('**/to_head')
        self.dizzy = dizzy
        if dizzy:
            if self.isSkeleton:
                actorNode = self.find('**/__Actor_modelRoot')
                head = actorNode.find('**/joint_head')
                if self.style.body == 'a':
                    zVal = max(0.0, p2[2] + 0.8)
                else:
                    zVal = max(0.0, p2[2])
            else:
                head = self.find('**/joint_head')
                if self.style.body == 'c':
                    zVal = max(0.0, p2[2] + 0.4)
                else:
                    zVal = max(0.0, p2[2] + 0.8)
            head.calcTightBounds(p1, p2)
            self.stars3.reparentTo(head)
            self.stars3.loop('stun')
        else:
           self.stars3.detachNode()
           self.stars3.loop('nothing')

    def getDizzy3(self):
        return self.dizzy

    def setDizzy(self, dizzy):
        p1 = Point3(0)
        p2 = Point3(0)
        #head = self.find('**/to_head')
        self.dizzy = dizzy
        if dizzy:
            if self.isSkeleton:
                actorNode = self.find('**/__Actor_modelRoot')
                head = actorNode.find('**/joint_head')
                if self.style.body == 'a':
                    zVal = max(0.0, p2[2] + 0.8)
                else:
                    zVal = max(0.0, p2[2])
            else:
                head = self.find('**/joint_head')
                if self.style.body == 'c':
                    zVal = max(0.0, p2[2] + 0.4)
                else:
                    zVal = max(0.0, p2[2] + 0.8)
            head.calcTightBounds(p1, p2)
            self.stars.reparentTo(head)
            self.stars.loop('stun')
        else:
           self.stars.detachNode()
           self.stars.loop('nothing')

    def getDizzy(self):
        return self.dizzy

    def setDizzy2(self, dizzy2):
        p1 = Point3(0)
        p2 = Point3(0)
        #head = self.find('**/to_head')
        self.dizzy2 = dizzy2
        if self.dizzy:
            if self.isSkeleton:
                actorNode = self.find('**/__Actor_modelRoot')
                head = actorNode.find('**/joint_head')
                if self.style.body == 'a':
                    zVal = max(0.0, p2[2] + 0.8)
                else:
                    zVal = max(0.0, p2[2])
            else:
                head = self.find('**/joint_head')
                if self.style.body == 'c':
                    zVal = max(0.0, p2[2] + 0.4)
                else:
                    zVal = max(0.0, p2[2] + 0.8)
            head.calcTightBounds(p1, p2)
            self.stars.reparentTo(head)
            self.stars.loop('stun')
        elif dizzy2:
            if self.isSkeleton:
                actorNode = self.find('**/__Actor_modelRoot')
                head = actorNode.find('**/joint_head')
                if self.style.body == 'a':
                    zVal = max(0.0, p2[2] + 0.8)
                else:
                    zVal = max(0.0, p2[2])
            else:
                head = self.find('**/joint_head')
                if self.style.body == 'c':
                    zVal = max(0.0, p2[2] + 0.4)
                else:
                    zVal = max(0.0, p2[2] + 0.8)
            head.calcTightBounds(p1, p2)
            self.stars.reparentTo(head)
            self.stars.loop('stun')
        else:
            self.stars.detachNode()
            self.stars.loop('nothing')

    def getDizzy2(self):
        return self.dizzy2

    def setSued2(self, sued):
        p1 = Point3(0)
        p2 = Point3(0)
        #head = self.find('**/to_head')
        self.sued = sued
        if sued:
            if self.isSkeleton:
                actorNode = self.find('**/__Actor_modelRoot')
                head = actorNode.find('**/joint_head')
                if self.style.body == 'a':
                    zVal = max(0.0, p2[2] + 0.8)
                else:
                    zVal = max(0.0, p2[2])
            else:
                head = self.find('**/joint_head')
                if self.style.body == 'c':
                    zVal = max(0.0, p2[2] + 0.4)
                else:
                    zVal = max(0.0, p2[2] + 0.8)
            head.calcTightBounds(p1, p2)
            self.suedstars.reparentTo(head)
            self.suedstars.loop('stun')
        else:
            self.suedstars.detachNode()
            self.suedstars.loop('nothing')

    def getSued2(self):
        return self.sued

    def setSoaked(self, soaked):
        head = self.find('**/to_head')
        #head = self.getHeadParts()[0]


        self.soaked = soaked

    def getSoaked(self):
        return self.soaked

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

    def setGovernaught(self, governaught):
        self.governaught = governaught
        if self.governaught:
            self.processGovernaught()

    def getGovernaught(self):
        return self.governaught

    def processGovernaught(self):
        self.maxHP = int(self.getHP())
        #self.currHP = self.maxHP
        self.makeGovernaught()
        nameInfo = self.createNameInfo()
        self.setDisplayName(nameInfo)

    def setCog(self, cog):
        self.cog = cog
        if self.cog:
            self.processCog()

    def getCog(self):
        return self.cog

    def processCog(self):
        if self.isSkelecog:
            self.maxHP = int(self.getHP())
        #self.currHP = self.maxHP

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
        self.maxHP = int(self.getHP())
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

    def createNameInfoContracted(self):
        name = self.name
        dept = self.getStyleDept()
        level = str(self.getActualLevel())
        if self.getManager():
            level += TTLocalizer.ManagerPostFix
        if self.getExecutive() and not self.getManager():
            level += TTLocalizer.ExecutivePostFix
        if self.getGovernaught() and not self.getManager():
            level += TTLocalizer.GovernaughtPostFix
        if self.getSkeleRevives() > 0:
            level += TTLocalizer.SkeleRevivePostFix % (self.getSkeleRevives() + 1)
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': "Unionized\n%s" % name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoOverpressured(self):
        name = self.name
        dept = self.getStyleDept()
        level = str(self.getActualLevel())
        if self.getManager():
            level += TTLocalizer.ManagerPostFix
        if self.getExecutive() and not self.getManager():
            level += TTLocalizer.ExecutivePostFix
        if self.getGovernaught() and not self.getManager():
            level += TTLocalizer.GovernaughtPostFix
        if self.getSkeleRevives() > 0:
            level += TTLocalizer.SkeleRevivePostFix % (self.getSkeleRevives() + 1)
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': "Overpressured\n%s" % name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoShadow(self):
        name = self.name
        dept = self.getStyleDept()
        level = str(self.getActualLevel())
        if self.getSkeleRevives() > 0:
            level += TTLocalizer.SkeleRevivePostFix % (self.getSkeleRevives() + 1)
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': "Burned\n%s" % name,
                                                        'dept': dept,
                                                        'level': "30.mgr"}
        return nameInfo

    def createNameInfo(self):
        name = self.name
        dept = self.getStyleDept()
        if self.dna.name == 'hrollers':
            level = '25'
        else:
            level = str(self.getActualLevel())
        if self.getExecutive() and not self.getManager():
            level += TTLocalizer.ExecutivePostFix
        if self.getManager():
            level += TTLocalizer.ManagerPostFix
        if self.getGovernaught() and not self.getManager() and not self.dna.name in ['std2', 'mh2', 'cnd2']:
            level += TTLocalizer.GovernaughtPostFix
        if self.dna.name in ['std2', 'mh2', 'cnd2']:
            level += '.exe'
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
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': self.name,
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

    def createNameInfoShivering(self):
        name = 'Shivering Club President'
        dept = 'Bossbot'
        level = '25.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoHighStakes(self):
        name = 'High Stakes Club President'
        dept = 'Bossbot'
        level = '21.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoMulligan(self):
        name = 'Mulligan Club President'
        dept = 'Bossbot'
        level = '21.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoChipFan(self):
        name = 'Chip Fan Club President'
        dept = 'Bossbot'
        level = '23.mgr'
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

    def createNameInfoPuzzling(self):
        name = 'Puzzling Club President'
        dept = 'Bossbot'
        level = '24.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoAncient(self):
        name = 'Ancient Club President'
        dept = 'Bossbot'
        level = '22.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo
    
    def createNameInfoSensational(self):
        name = 'Sensational Club President'
        dept = 'Bossbot'
        level = '21.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoCommissioning(self):
        name = 'Commissioning Club President'
        dept = 'Bossbot'
        level = '21.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoSpongy(self):
        name = 'Spongy Mint Supervisor'
        dept = 'Cashbot'
        level = '28.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo
    
    def createNameInfoImmovable(self):
        name = 'Immovable Mint Supervisor'
        dept = 'Cashbot'
        level = '26.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo
    
    def createNameInfoLedgering(self):
        name = 'Ledgering Mint Supervisor'
        dept = 'Cashbot'
        level = '23.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo
    
    def createNameInfoAuditing(self):
        name = 'Auditing Mint Supervisor'
        dept = 'Cashbot'
        level = '24.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoScheming(self):
        name = 'Scheming Mint Supervisor'
        dept = 'Cashbot'
        level = '25.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo
    
    def createNameInfoUsurer(self):
        name = 'Usurer Mint Supervisor'
        dept = 'Cashbot'
        level = '27.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoFraudulent(self):
        name = 'Fraudulent Mint Supervisor'
        dept = 'Cashbot'
        level = '25.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoAccountant(self):
        name = 'Accountant Mint Supervisor'
        dept = 'Cashbot'
        level = '24.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoConfused(self):
        name = 'Compounding Mint Supervisor'
        dept = 'Cashbot'
        level = '22.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoConfusedReal(self):
        name = 'Confused Mint Supervisor'
        dept = 'Cashbot'
        level = '22.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoControlling(self):
        name = 'Controlling Mint Supervisor'
        dept = 'Cashbot'
        level = '21.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoAbacus(self):
        name = 'Abacus Mint Supervisor'
        dept = 'Cashbot'
        level = '20.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoLaborious(self):
        name = 'Laborious Head Attorney'
        dept = 'Lawbot'
        level = '26.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoChrono(self):
        name = 'Chrono Head Attorney'
        dept = 'Lawbot'
        level = '25.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoMonolithic(self):
        name = 'Monolithic Head Attorney'
        dept = 'Lawbot'
        level = '24.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoOmnipotent(self):
        name = 'Omnipotent Head Attorney'
        dept = 'Lawbot'
        level = '23.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo
    
    def createNameInfoDraining(self):
        name = 'Draining Head Attorney'
        dept = 'Lawbot'
        level = '26.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo
    
    def createNameInfoShaking(self):
        name = 'Shaking Head Attorney'
        dept = 'Lawbot'
        level = '24.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo
    
    def createNameInfoDizzy(self):
        name = 'Dizzy Head Attorney'
        dept = 'Lawbot'
        level = '21.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoOverseer(self):
        name = 'Overseer Head Attorney'
        dept = 'Lawbot'
        level = '22.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoSneaky(self):
        name = 'Sneaky Head Attorney'
        dept = 'Lawbot'
        level = '20.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoSniper(self):
        name = 'Sniper Factory Foreman'
        dept = 'Sellbot'
        level = '25.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoRedTape(self):
        name = 'Red Tape\nFactory Foreman'
        dept = 'Sellbot'
        level = '24.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoContractor(self):
        name = 'Contractor Factory Foreman'
        dept = 'Sellbot'
        level = '23.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoExplosive(self):
        name = 'Explosive Factory Foreman'
        dept = 'Sellbot'
        level = '22.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoBurning(self):
        name = 'Burning Factory Foreman'
        dept = 'Sellbot'
        level = '21.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo
    
    def createNameInfoUnionized(self):
        name = 'Unionized Factory Foreman'
        dept = 'Sellbot'
        level = '21.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo
    
    def createNameInfoContributing(self):
        name = 'Contributing Factory Foreman'
        dept = 'Sellbot'
        level = '25.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoPolishing(self):
        name = 'Polishing Factory Foreman'
        dept = 'Sellbot'
        level = '26.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept, 
                                                        'level': level}
        return nameInfo
    
    def createNameInfoExtortionist(self):
        name = 'Extortionist Factory Foreman'
        dept = 'Sellbot'
        level = '28.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoSleepy(self):
        name = 'Sleepy Factory Foreman'
        dept = 'Sellbot'
        level = '20.mgr'
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

    def createNameInfoWhite(self):
        name = 'White Silhouette'
        dept = 'Cashbot'
        level = '25.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo

    def createNameInfoMagenta(self):
        name = 'Magenta Silhouette'
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
    
    def createNameInfoTeal(self):
        name = 'Teal Silhouette'
        dept = 'Cashbot'
        level = '25.mgr'
        nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': name,
                                                        'dept': dept,
                                                        'level': level}
        return nameInfo
    
    def createNameInfoGold(self):
        name = 'Gold Silhouette'
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
        if hp > self.maxHP * self.hardMaxHP and not self.dna.name == 'foreman' and not self.dna.name == 'clubpres' and not self.dna.name == 'clerk' and not self.dna.name == 'supervis' and not self.dna.name == 'ovt':
            self.currHP = int(self.maxHP * self.hardMaxHP)
        else:
            self.currHP = int(hp)
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
            animTrack = Sequence(Func(self.updateHealthBar, 0), Func(self.pose, 'landing', 0), Wait(waitTime), ActorInterval(self, 'landing', duration=dur))
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
      #  def changeMusic(Task):
           # if self.dna.name in SuitBattleGlobals.SpecialCogDict and self.dna.name not in ToontownGlobals.noCustomMusicManagers:
            #    if base.localAvatar.isInBattle:
                 #   if self.dna.name == 'stenog':
                   #     base.musicManager.stopAllSounds()
                   #     music = base.loader.loadMusic(ToontownGlobals.managerMusic[self.dna.name])
                    #    music2 = base.loader.loadMusic("phase_11/audio/bgm/LB_litigation_base.ogg")
                    #    base.playMusic(music, looping=1, volume=0.9)
                    #    base.playMusic(music2, looping=1, volume=0.9)
                   # elif self.dna.name == 'sgoat':
                       # base.musicManager.stopAllSounds()
                      #  music = base.loader.loadMusic(ToontownGlobals.managerMusic[self.dna.name])
                      #  music2 = base.loader.loadMusic("phase_11/audio/bgm/LB_litigation_base.ogg")
                     #   base.playMusic(music, looping=1, volume=0.9)
                   #     base.playMusic(music2, looping=1, volume=0.9)
                   # e#lif self.dna.name == 'lgator':
                     #   base.musicManager.stopAllSounds()
                     #   music = base.loader.loadMusic(ToontownGlobals.managerMusic[self.dna.name])
                      #  music2 = base.loader.loadMusic("phase_11/audio/bgm/LB_litigation_base.ogg")
                     #   base.playMusic(music, looping=1, volume=0.9)
                     #   base.playMusic(music2, looping=1, volume=0.9)
                   # elif self.dna.name == 'caseman':
                      #  base.musicManager.stopAllSounds()
                      #  music = base.loader.loadMusic(ToontownGlobals.managerMusic[self.dna.name])
                      #  music2 = base.loader.loadMusic("phase_11/audio/bgm/LB_litigation_base.ogg")
                     #   base.playMusic(music, looping=1, volume=0.9)
                      #  base.playMusic(music2, looping=1, volume=0.9)

        #def changeMusicLater(Task):
          #  taskMgr.doMethodLater(0.2, changeMusic, 'changemusic')

       # changeMusicLater('changeMusic')
       # self.accept('toonEnteredBattle', changeMusicLater)
        self.loop('neutral%s' % ('-hurt' if float(self.currHP) / float(self.maxHP) <= 0.25 else '',), 0)
        self.disableBattleDetect()
        self.healthBar.show()
        self.corpMedallion.hide()
        if self.currHP < self.maxHP:
            self.updateHealthBar(0, 1)
        if self.currHP >= self.maxHP:
            self.updateHealthBar(0, 1)

    def exitBattle(self):
      #  base.musicManager.stopAllSounds()
        if not self.virtual:
            self.healthBar.hide()
            self.corpMedallion.show()
        self.currHP = self.maxHP
        self.interactivePropTrackBonus = -1
        self.ignore('toonEnteredBattle')

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

    def setMaxHP2(self, hp):
        self.maxHP = int(hp)
			
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

    def showHpTextNew(self, number, text=None, bonus=0, scale=1, attackTrack=-1, colorCode=0):
        if self.HpTextEnabled and not self.ghostMode:
            if self.hpText:
                self.hideHpText()
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            if number == 0:
                self.HpTextGenerator.setText("")
            elif number < 0:
                self.HpTextGenerator.setText(str(number))
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
            else:
                    r = 0
                    g = 0.9
                    b = 0
                    a = 1
            if self.hpTextInterval:
                self.hpTextInterval.finish()
                self.hpTextInterval = None
            if self.hpTextInterval2:
                self.hpTextInterval2.finish()
                self.hpTextInterval2 = None
            self.HpTextGenerator.setTextColor(r, g, b, a)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(scale)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 100)
            self.hpText.setPos(0, 0, self.height / 2)
        if text != None:
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()
        else:
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.0),
                                           LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

        if text != None:
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            self.HpTextGenerator.setText(text)
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            r = a = 1.0
            g = b = 0.0
            if colorCode == 0:
                self.HpTextGenerator.setTextColor(1, 0, 0, 1) # Red
            if colorCode == 1:
                self.HpTextGenerator.setTextColor(0.871, 0.827, 1, 1) # Default Cheat Color
            if colorCode == 3:
                self.HpTextGenerator.setTextColor(1, 0.953, 0, 1) # Yellow
            if colorCode == 4:
                self.HpTextGenerator.setTextColor(1, 0.561, 0, 1) # Orange
            if colorCode == 5:
                self.HpTextGenerator.setTextColor(0.851, 0, 1, 1) # Purple
            if colorCode == 6:
                self.HpTextGenerator.setTextColor(0.012, 1, 0, 1) # Green
            self.hpTextNode2 = self.HpTextGenerator.generate()
            self.hpText2 = self.hpText.attachNewNode(self.hpTextNode2)
            self.hpText2.setScale(scale)
            self.hpText2.setBillboardPointEye()
            self.hpText2.setBin('fixed', 99)
            self.hpText2.setPos(0, 0, -1)
            #self.hpTextInterval2 = Sequence(self.hpText2.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText2, .25, Vec4(0, 0, 0, 0)),
                              #             Func(self.hideHpText))
            #self.hpTextInterval2.start()

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
                if self.hpTextInterval:
                    self.hpTextInterval.finish()
                    self.hpTextInterval = None
                if self.hpTextInterval2:
                    self.hpTextInterval2.finish()
                    self.hpTextInterval2 = None
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
                self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                self.hpTextInterval.start()

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
                if self.hpTextInterval:
                    self.hpTextInterval.finish()
                    self.hpTextInterval = None
                if self.hpTextInterval2:
                    self.hpTextInterval2.finish()
                    self.hpTextInterval2 = None
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
                self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 3.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                self.hpTextInterval.start()

    def showHpTextRed(self, number, bonus = 0, scale = 1, attackTrack = -1):
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
                if self.hpTextInterval:
                    self.hpTextInterval.finish()
                    self.hpTextInterval = None
                if self.hpTextInterval2:
                    self.hpTextInterval2.finish()
                    self.hpTextInterval2 = None
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
                self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 3.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                self.hpTextInterval.start()

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
                if self.hpTextInterval:
                    self.hpTextInterval.finish()
                    self.hpTextInterval = None
                if self.hpTextInterval2:
                    self.hpTextInterval2.finish()
                    self.hpTextInterval2 = None
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
                self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                self.hpTextInterval.start()

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
                if self.hpTextInterval:
                    self.hpTextInterval.finish()
                    self.hpTextInterval = None
                if self.hpTextInterval2:
                    self.hpTextInterval2.finish()
                    self.hpTextInterval2 = None
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
                self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                self.hpTextInterval.start()

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
                if self.hpTextInterval:
                    self.hpTextInterval.finish()
                    self.hpTextInterval = None
                if self.hpTextInterval2:
                    self.hpTextInterval2.finish()
                    self.hpTextInterval2 = None
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
                self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                self.hpTextInterval.start()

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
                if self.hpTextInterval:
                    self.hpTextInterval.finish()
                    self.hpTextInterval = None
                if self.hpTextInterval2:
                    self.hpTextInterval2.finish()
                    self.hpTextInterval2 = None
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
                self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'),
                               Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)),
                               Func(self.hideHpText))
                self.hpTextInterval.start()

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
                if self.hpTextInterval:
                    self.hpTextInterval.finish()
                    self.hpTextInterval = None
                if self.hpTextInterval2:
                    self.hpTextInterval2.finish()
                    self.hpTextInterval2 = None
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
                self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                self.hpTextInterval.start()

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
                if self.hpTextInterval:
                    self.hpTextInterval.finish()
                    self.hpTextInterval = None
                if self.hpTextInterval2:
                    self.hpTextInterval2.finish()
                    self.hpTextInterval2 = None
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
                self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'),Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                self.hpTextInterval.start()

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
                if self.hpTextInterval:
                    self.hpTextInterval.finish()
                    self.hpTextInterval = None
                if self.hpTextInterval2:
                    self.hpTextInterval2.finish()
                    self.hpTextInterval2 = None
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
                self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
                self.hpTextInterval.start()


    def showHpString(self, text, duration = 0.85, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            if self.hpTextInterval:
                self.hpTextInterval.finish()
                self.hpTextInterval = None
            if self.hpTextInterval2:
                self.hpTextInterval2.finish()
                self.hpTextInterval2 = None
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
            self.hpText.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

    def showHpStringRed(self, text, duration = 0.85, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            if self.hpTextInterval:
                self.hpTextInterval.finish()
                self.hpTextInterval = None
            if self.hpTextInterval2:
                self.hpTextInterval2.finish()
                self.hpTextInterval2 = None
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            self.HpTextGenerator.setText(text)
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            r = a = 1.0
            g = b = 0.0
            self.HpTextGenerator.setTextColor(1, 0, 0, 1)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(scale)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

    def showHpStringGreen(self, text, duration = 0.85, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            if self.hpTextInterval:
                self.hpTextInterval.finish()
                self.hpTextInterval = None
            if self.hpTextInterval2:
                self.hpTextInterval2.finish()
                self.hpTextInterval2 = None
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            self.HpTextGenerator.setText(text)
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            r = a = 1.0
            g = b = 0.0
            self.HpTextGenerator.setTextColor(0.059, 1, 0, 1)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(scale)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

    def showHpStringDesperation2(self, text, duration = 0.85, scale = 1): # lure string
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
            self.hpText.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

    def showHpStringSkeletonReviveOverpressured(self): # damage string
        if self.HpTextEnabled and not self.ghostMode:
            self.HpTextGenerator.setText("Overworked!")
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            if self.hpTextInterval:
                self.hpTextInterval.finish()
                self.hpTextInterval = None
            if self.hpTextInterval2:
                self.hpTextInterval2.finish()
                self.hpTextInterval2 = None
            self.HpTextGenerator.setTextColor(1, 0.561, 0, 1)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(0.75)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 100)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.0),
                                                   LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

        self.HpTextGenerator.setTextColor(0.871, 0.827, 1, 1)
        self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
        self.HpTextGenerator.setText("+50% Damage!")
        self.HpTextGenerator.clearShadow()
        self.HpTextGenerator.setAlign(TextNode.ACenter)
        self.hpTextNode2 = self.HpTextGenerator.generate()
        self.hpText2 = self.hpText.attachNewNode(self.hpTextNode2)
        self.HpTextGenerator.setTextColor(1, 0.518, 0, 1)
        self.hpText2.setScale(.7)
        self.hpText2.setBillboardPointEye()
        self.hpText2.setBin('fixed', 99)
        self.hpText2.setPos(0, 0, -1.5)
        self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
        self.HpTextGenerator.setText("+50% Vulnerable!")
        self.HpTextGenerator.clearShadow()
        self.HpTextGenerator.setAlign(TextNode.ACenter)
        self.hpTextNode3 = self.HpTextGenerator.generate()
        self.hpText3 = self.hpText.attachNewNode(self.hpTextNode3)
        self.HpTextGenerator.setTextColor(0, 1, 0.047, 1)
        self.hpText3.setScale(.7)
        self.hpText3.setBillboardPointEye()
        self.hpText3.setBin('fixed', 99)
        self.hpText3.setPos(0, 0, -0.75)
            # self.hpTextInterval2 = Sequence(self.hpText2.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText2, .25, Vec4(0, 0, 0, 0)),
            #             Func(self.hideHpText))
            # self.hpTextInterval2.start()

    def showHpStringSkeletonRevive(self): # damage string
        if self.HpTextEnabled and not self.ghostMode:
            self.HpTextGenerator.setText("Revived!")
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            if self.hpTextInterval:
                self.hpTextInterval.finish()
                self.hpTextInterval = None
            if self.hpTextInterval2:
                self.hpTextInterval2.finish()
                self.hpTextInterval2 = None
            self.HpTextGenerator.setTextColor(0.871, 0.827, 1, 1)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(0.75)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 100)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.0),
                                                   LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

        self.HpTextGenerator.setTextColor(0, 1, 0.047, 1)
        self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
        self.HpTextGenerator.setText("-50% Health!")
        self.HpTextGenerator.clearShadow()
        self.HpTextGenerator.setAlign(TextNode.ACenter)
        self.hpTextNode2 = self.HpTextGenerator.generate()
        self.hpText2 = self.hpText.attachNewNode(self.hpTextNode2)
        self.HpTextGenerator.setTextColor(1, 0.518, 0, 1)
        self.hpText2.setScale(.7)
        self.hpText2.setBillboardPointEye()
        self.hpText2.setBin('fixed', 99)
        self.hpText2.setPos(0, 0, -0.75)
        self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
        self.HpTextGenerator.setText("+50% Damage!")
        self.HpTextGenerator.clearShadow()
        self.HpTextGenerator.setAlign(TextNode.ACenter)
        self.hpTextNode3 = self.HpTextGenerator.generate()
        self.hpText3 = self.hpText.attachNewNode(self.hpTextNode3)
        self.HpTextGenerator.setTextColor(1, 0.518, 0, 1)
        self.hpText3.setScale(.7)
        self.hpText3.setBillboardPointEye()
        self.hpText3.setBin('fixed', 99)
        self.hpText3.setPos(0, 0, -1.5)
            # self.hpTextInterval2 = Sequence(self.hpText2.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText2, .25, Vec4(0, 0, 0, 0)),
            #             Func(self.hideHpText))
            # self.hpTextInterval2.start()

    def showHpStringDesperation(self): # damage string
        if self.HpTextEnabled and not self.ghostMode:
            self.HpTextGenerator.setText("Desperation!")
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            if self.hpTextInterval:
                self.hpTextInterval.finish()
                self.hpTextInterval = None
            if self.hpTextInterval2:
                self.hpTextInterval2.finish()
                self.hpTextInterval2 = None
            self.HpTextGenerator.setTextColor(1, 0.561, 0, 1)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(0.75)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 100)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.0),
                                                   LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

        self.HpTextGenerator.setTextColor(0.871, 0.827, 1, 1)
        self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
        self.HpTextGenerator.setText("+1 Lure Resistance")
        self.HpTextGenerator.clearShadow()
        self.HpTextGenerator.setAlign(TextNode.ACenter)
        self.hpTextNode2 = self.HpTextGenerator.generate()
        self.hpText2 = self.hpText.attachNewNode(self.hpTextNode2)
        self.HpTextGenerator.setTextColor(0.871, 0.827, 1, 1)
        self.hpText2.setScale(.7)
        self.hpText2.setBillboardPointEye()
        self.hpText2.setBin('fixed', 99)
        self.hpText2.setPos(0, 0, -0.75)
        self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
        self.HpTextGenerator.setText("+40% Damage!")
        self.HpTextGenerator.clearShadow()
        self.HpTextGenerator.setAlign(TextNode.ACenter)
        self.hpTextNode3 = self.HpTextGenerator.generate()
        self.hpText3 = self.hpText.attachNewNode(self.hpTextNode3)
        self.HpTextGenerator.setTextColor(0.871, 0.827, 1, 1)
        self.hpText3.setScale(.7)
        self.hpText3.setBillboardPointEye()
        self.hpText3.setBin('fixed', 99)
        self.hpText3.setPos(0, 0, -1.5)
            # self.hpTextInterval2 = Sequence(self.hpText2.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText2, .25, Vec4(0, 0, 0, 0)),
            #             Func(self.hideHpText))
            # self.hpTextInterval2.start()

    def showHpStringDesperationDamage(self): # damage string
        if self.HpTextEnabled and not self.ghostMode:
            self.HpTextGenerator.setText("Desperation!")
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            if self.hpTextInterval:
                self.hpTextInterval.finish()
                self.hpTextInterval = None
            if self.hpTextInterval2:
                self.hpTextInterval2.finish()
                self.hpTextInterval2 = None
            self.HpTextGenerator.setTextColor(1, 0.561, 0, 1)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(0.75)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 100)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2), blendType='easeOut'), Wait(1.0),
                                                   LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

        self.HpTextGenerator.setTextColor(0.871, 0.827, 1, 1)
        self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
        self.HpTextGenerator.setText("+40% Damage!")
        self.HpTextGenerator.clearShadow()
        self.HpTextGenerator.setAlign(TextNode.ACenter)
        self.hpTextNode2 = self.HpTextGenerator.generate()
        self.hpText2 = self.hpText.attachNewNode(self.hpTextNode2)
        self.HpTextGenerator.setTextColor(0.871, 0.827, 1, 1)
        self.hpText2.setScale(.7)
        self.hpText2.setBillboardPointEye()
        self.hpText2.setBin('fixed', 99)
        self.hpText2.setPos(0, 0, -0.75)

    def showHpStringVideographer5(self): # damage string
        if self.HpTextEnabled and not self.ghostMode:
            self.HpTextGenerator.setText("Video Buffering!")
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            if self.hpTextInterval:
                self.hpTextInterval.finish()
                self.hpTextInterval = None
            if self.hpTextInterval2:
                self.hpTextInterval2.finish()
                self.hpTextInterval2 = None
            self.HpTextGenerator.setTextColor(0, 0.706, 1, 1)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(0.75)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 100)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.0),
                                           LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

        self.HpTextGenerator.setTextColor(0, 1, 0.031, 1)
        self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
        self.HpTextGenerator.setText("+5% Vulnerable")
        self.HpTextGenerator.clearShadow()
        self.HpTextGenerator.setAlign(TextNode.ACenter)
        self.hpTextNode2 = self.HpTextGenerator.generate()
        self.hpText2 = self.hpText.attachNewNode(self.hpTextNode2)
        self.HpTextGenerator.setTextColor(1, 0.518, 0, 1)
        self.hpText2.setScale(.7)
        self.hpText2.setBillboardPointEye()
        self.hpText2.setBin('fixed', 99)
        self.hpText2.setPos(0, 0, -0.75)
        self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
        self.HpTextGenerator.setText("+5% Damage!")
        self.HpTextGenerator.clearShadow()
        self.HpTextGenerator.setAlign(TextNode.ACenter)
        self.hpTextNode3 = self.HpTextGenerator.generate()
        self.hpText3 = self.hpText.attachNewNode(self.hpTextNode3)
        self.HpTextGenerator.setTextColor(1, 0.518, 0, 1)
        self.hpText3.setScale(.7)
        self.hpText3.setBillboardPointEye()
        self.hpText3.setBin('fixed', 99)
        self.hpText3.setPos(0, 0, -1.5)

    def showHpStringVideographer20(self): # damage string
        if self.HpTextEnabled and not self.ghostMode:
            self.HpTextGenerator.setText("Video Buffering!")
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            if self.hpTextInterval:
                self.hpTextInterval.finish()
                self.hpTextInterval = None
            if self.hpTextInterval2:
                self.hpTextInterval2.finish()
                self.hpTextInterval2 = None
            self.HpTextGenerator.setTextColor(0, 0.706, 1, 1)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(0.75)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 100)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.0),
                                           LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

        self.HpTextGenerator.setTextColor(0, 1, 0.031, 1)
        self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
        self.HpTextGenerator.setText("+20% Vulnerable")
        self.HpTextGenerator.clearShadow()
        self.HpTextGenerator.setAlign(TextNode.ACenter)
        self.hpTextNode2 = self.HpTextGenerator.generate()
        self.hpText2 = self.hpText.attachNewNode(self.hpTextNode2)
        self.HpTextGenerator.setTextColor(1, 0.518, 0, 1)
        self.hpText2.setScale(.7)
        self.hpText2.setBillboardPointEye()
        self.hpText2.setBin('fixed', 99)
        self.hpText2.setPos(0, 0, -0.75)
        self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
        self.HpTextGenerator.setText("+20% Damage!")
        self.HpTextGenerator.clearShadow()
        self.HpTextGenerator.setAlign(TextNode.ACenter)
        self.hpTextNode3 = self.HpTextGenerator.generate()
        self.hpText3 = self.hpText.attachNewNode(self.hpTextNode3)
        self.HpTextGenerator.setTextColor(1, 0.518, 0, 1)
        self.hpText3.setScale(.7)
        self.hpText3.setBillboardPointEye()
        self.hpText3.setBin('fixed', 99)
        self.hpText3.setPos(0, 0, -1.5)

    def showHpStringAbility(self, text, duration = 0.85, scale = 0.75):
        if self.HpTextEnabled and not self.ghostMode:
            if self.hpTextInterval:
                self.hpTextInterval.finish()
                self.hpTextInterval = None
            if self.hpTextInterval2:
                self.hpTextInterval2.finish()
                self.hpTextInterval2 = None
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
            self.hpText.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(0.5), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

    def showHpStringSacrifice(self, text, duration = 0.85, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            self.HpTextGenerator.setText(text)
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            r = a = 1.0
            g = b = 0.0
            self.HpTextGenerator.setTextColor(1, 0.561, 0, 1)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(scale)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

    def showHpStringKnockback(self, text, duration = 0.85, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            self.HpTextGenerator.setText(text)
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            r = a = 1.0
            g = b = 0.0
            self.HpTextGenerator.setTextColor(0.071, 1, 0, 1)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(scale)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

    def showHpStringDamaged(self, text, duration = 0.85, scale = 1):
        if self.HpTextEnabled and not self.ghostMode:
            self.HpTextGenerator.setFont(OTPGlobals.getSignFont())
            self.HpTextGenerator.setText(text)
            self.HpTextGenerator.clearShadow()
            self.HpTextGenerator.setAlign(TextNode.ACenter)
            r = a = 1.0
            g = b = 0.0
            self.HpTextGenerator.setTextColor(1, 0.953, 0, 1)
            self.hpTextNode = self.HpTextGenerator.generate()
            self.hpText = self.attachNewNode(self.hpTextNode)
            self.hpText.setScale(scale)
            self.hpText.setBillboardPointEye()
            self.hpText.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

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
            self.hpText.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

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
            self.hpText.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

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
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 2.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()

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
            self.hpText.setBin('fixed', 99)
            self.hpText.setPos(0, 0, self.height / 2)
            self.hpTextInterval = Sequence(self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType='easeOut'), Wait(1.0), LerpColorScaleInterval(self.hpText, .25, Vec4(0, 0, 0, 0)), Func(self.hideHpText))
            self.hpTextInterval.start()


    def hideHpText(self):
        try:
            DistributedAvatar.DistributedAvatar.hideHpText(self)
            if self.sillySurgeText:
                self.nametag3d.clearDepthTest()
                self.nametag3d.clearBin()
                self.sillySurgeText = False
            if self.hpTextInterval:
                self.hpTextInterval.finish()
                self.hpTextInterval = None
                del self.hpTextInterval
        except:
            pass


    def getAvIdName(self):
        try:
            level = self.getActualLevel()
        except:
            level = '???'

        return '%s\n%s\nLevel %s' % (self.getName(), self.doId, level)