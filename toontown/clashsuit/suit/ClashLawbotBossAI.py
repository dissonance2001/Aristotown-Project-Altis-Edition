import random
import math
from operator import itemgetter
from typing import Optional

from direct.distributed.ClockDelta import *
from direct.showbase.PythonUtil import lerp

from toontown.inventory.enums.ItemEnums import BackgroundItemType, NameplateItemType, BoosterItemType, MaterialItemType
from toontown.clashsuit.suit import BossCogGlobals
from toontown.modifiers.contentsync.ContentSyncEnums import ContentSyncType
from toontown.clashsuit.suit.DistributedLawbotBossDefenseSpecialistAI import DistributedLawbotBossDefenseSpecialistAI
from direct.fsm import FSM
from direct.interval.IntervalGlobal import *

from otp.ai.AIBaseGlobal import *
from direct.showbase import PythonUtil
from toontown.clashbattle.battle.distributed import DistributedBattlePaintingAI
from toontown.clashbattle.battle.distributed import DistributedBattleVirtualAI
from toontown.clashbattle.battle import SuitBattleGlobals
from toontown.building import ClashSuitBuildingGlobals
from toontown.coghq import DistributedLawbotBossGavelAI
from toontown.coghq import DistributedLawbotBossTrapAI
from toontown.coghq import DistributedLawbotBossTreasureAI
from toontown.coghq import DistributedLawbotCannonAI
#from toontown.groups.GroupEnums import GroupType, Options
from toontown.instances import DistributedCutsceneSkipButtonAI
from toontown.quest3.context.CogBossContext import LawbotBossContext
from toontown.safezone.ChairConstants import ChairTypeEnum, MusicTypeEnum
from toontown.safezone.DistributedChairAI import DistributedChairAI
from toontown.clashsuit.suit import ClashBossCogAI
from toontown.clashsuit.suit import DistributedLawbotBossSecurityCameraAI
from toontown.clashsuit.suit import ClashLawbotBossSuitAI
from toontown.clashsuit.suit import SuitDNA
from toontown.toon.npc.NPCToonClassesAI import DistributedNPCBumpyAI
from toontown.toon.npc import NPCToons
from toontown.toonbase import ToontownGlobals
from toontown.toon.gui.ToonTipGlobals import TTE


class ClashLawbotBossAI(ClashBossCogAI.ClashBossCogAI, FSM.FSM):
   # groupType = GroupType.CLO
    WANT_TOONO = False
    ChairPositions = {
        (Vec3(-12.2595, 238.828, -66.576), Vec3(90, 0, 0)),
        (Vec3(-12.2148, 216.807, -66.576), Vec3(90, 0, 0)),
        (Vec3(-15.254, 194.805, -66.576), Vec3(90, 0, 0)),
        (Vec3(-16.1662, 172.79, -66.576), Vec3(90, 0, 0)),

        (Vec3(16.2401, 172.747, -66.576), Vec3(-90, 0, 0)),
        (Vec3(15.2375, 194.8, -66.576), Vec3(-90, 0, 0)),
        (Vec3(12.0395, 216.772, -66.576), Vec3(-90, 0, 0)),
        (Vec3(12.1348, 238.774, -66.576), Vec3(-90, 0, 0)),
    }

    def __init__(self, air):
        ClashBossCogAI.ClashBossCogAI.__init__(self, air, 'l')
        FSM.FSM.__init__(self, 'ClashLawbotBossAI')
        self.scene = NodePath('scene')
        self.reparentTo(self.scene)
        cn = CollisionNode('walls')
        cs = CollisionSphere(0, 0, 0, 13)
        cn.addSolid(cs)
        cs = CollisionInvSphere(0, 0, 0, 84)
        cn.addSolid(cs)
        self.attachNewNode(cn)
        self.lawyers = []
        self.nearbyLawyers = []
        self.lawyersPerPainting = {}
        self.cannons = None
        self.bossMaxDamage = BossCogGlobals.LawbotBossMaxDamage[0]
        self.battleOnePlanner = ClashSuitBuildingGlobals.SPE.CLO_HARD
        self.bossDamage = 0
        self.numSues = 1
        self.toonLevels = 0
        self.toonupValue = 1
        self.keyStates.append('BattleFour')
        self.battleFourTimeStarted = 0
        self.battleFourTimeInMin = 0
        self.numAreaAttacks = 0
        self.lastAreaAttackTime = 0
        self.movingToToon = False
        self.currToon = -1
        self.numMoveAttacks = 0
        self.toonDamagesDict = {}
        self.toonStunsDict = {}
        self.lawyerPositions = {}
        self.lawyerMaxLevel = 8
        self.bumpyNPC = None
        self.traps = None
        self.spotlights = None
        self.trackingSpotlights = None
        self.evidence = {}
        self.gavels = None
        self.numSound = 10
        self.soundTypes = {}
        self.battleTimeStarted = 0
        self.battleDuration = 1800
        self.desperationState = -1
        self.stunnedHits = 0
        self.maxStunnedHits = 0
        self.trapIndex = -1
        self.moveTrack = None
        self.treasures = {}
        self.maxTreasures = 25
        self.soundDamage = 1
        self.toonsSoundDamageDealt = {}
        self.maxLawyersBattleTwo = 10
        self.maxLawyersBattleFour = 10
        self.timesBossStunned = 0
        self.toonsNumSuitsDefeated = {} # Final round
        self.toonsNumExeSuitsDefeated = {} # Final round
        self.toonsNumSuitsDestroyed = {} # Cannon round
        self.toonsNumExeSuitsDestroyed = {} # Cannon round
        self.chairs = [] # type: list[DistributedChairAI]
        self.lastDefenseThreshold = 0
        self.defenseSpecialists = []
    
    def setupChairs(self) -> None:
        for i, (pos, hpr) in enumerate(self.ChairPositions):
            # Create the chair and generate it.
            chair = DistributedChairAI(
                self.air, i, hopOnPos=[-0.1, -4.75, 1.0], hopOffPos=[-10, -0, -5],
                radius=6, chairType=ChairTypeEnum.COUCH, wantToono=self.WANT_TOONO, musicType=MusicTypeEnum.OCLO
            )
            chair.generateWithRequired(self.zoneId)
            self.chairs.append(chair)

            # Move the chair to the right pos.
            x, y, z = pos
            h, p, r = hpr
            chair.b_setPosHpr(x, y, z, h, p, r)
    
    def deleteChairs(self) -> None:
        for chair in self.chairs:
            chair.requestDelete()
        self.chairs = []
    
    def announceGenerate(self):
        super().announceGenerate()
        self.accept(self.taskName("cannon_destroyedSuit"), self.cannon_destroyedSuit)

    def delete(self):
        taskMgr.remove(self.uniqueName('trapHitBossDelay'))
        self.__deleteBattleFourObjects()
        self.__deleteBattleTwoObjects()

        self.deleteChairs()

        del self.lawyerPositions
        del self.lawyers
        return ClashBossCogAI.ClashBossCogAI.delete(self)

    def getContentSync(self) -> Optional[ContentSyncType]:
        return ContentSyncType.LBHQ

    def getHoodId(self):
        return ToontownGlobals.LawbotHQ

    def b_updateDamageDealt(self, avId, bossDamage):
        self.d_updateDamageDealt(avId, bossDamage)
        self.updateDamageDealt(avId, bossDamage)

    def d_updateDamageDealt(self, avId, damageDealt):
        self.sendUpdate('updateDamageDealt', [avId, damageDealt])

    def updateDamageDealt(self, avId, bossDamage):
        if avId in self.toonDamagesDict:
            self.toonDamagesDict[avId] += bossDamage
        else:
            self.toonDamagesDict[avId] = bossDamage

    def hitBoss(self):
        avId = self.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)
        if not self.validate(avId, avId in self.involvedToons, 'hitBoss from unknown avatar'):
            return
        # Just in case, extra fallback
        if not av:
            return
        soundType = av.soundType
        # The toon is not using the sound type given to them, therefore they are cheating.
        if soundType != self.soundTypes[avId]:
            self.notify.warning('avId %s should have soundType %s but hit with type %s' % (avId, self.soundTypes[avId], soundType))
            return
        currState = self.getCurrentOrNextState()
        if currState != 'BattleFour':
            return
        if self.attackCode == BossCogGlobals.BossCogDizzyNow:
            self.__recordHit(avId)
        else:
            # How to Stun CLO Tip
            av.showToonTip(TTE.TIP_STUN_CLO_TUTORIAL)

    def __recordHit(self, avId):
        if self.stunnedHits < self.maxStunnedHits:
            self.stunnedHits += self.soundDamage
            # Add this toon to the running dictionary of sound damage dealt for each toon.
            self.addToonsSoundDamageDealt(avId, self.soundDamage)
            # If the CLO is close enough to the trap, check if there is a skelecog.
            # If there is a skelecog, make it fly away. It doesn't wanna get run over!
            if self.maxStunnedHits - self.stunnedHits <= 15:
                if self.trapIndex != -1:
                    trap = self.traps[self.trapIndex]
                    if trap.getSuitId():
                        suit = simbase.air.doId2do.get(trap.suitId)
                        if suit:
                            suit.bossNear(self.trapIndex)
            # Stop the CLO attacking while she is falling through a trap.
            if self.stunnedHits >= self.maxStunnedHits:
                self.stopNextAttack()

            self.b_updateBossDamageMovie()

    def addToonsSoundDamageDealt(self, avId, amount):
        # Add to the running total of sound damage dealt by each toon.
        damageDealt = self.toonsSoundDamageDealt.get(avId, 0)
        damageDealt += amount
        self.toonsSoundDamageDealt[avId] = damageDealt

    def b_updateBossDamageMovie(self):
        self.d_updateBossDamageMovie()
        self.updateBossDamageMovie()

    def d_updateBossDamageMovie(self):
        self.sendUpdate("updateBossDamageMovie", [self.stunnedHits, self.maxStunnedHits])

    def updateBossDamageMovie(self):
        if self.stunnedHits >= self.maxStunnedHits:
            self.bossDamageMovie.resumeUntil(self.bossDamageMovie.getDuration())
        else:
            self.bossDamageMovie.resumeUntil(self.stunnedHits * self.bossDamageToMovie)

    def d_createBossTrapMovie(self):
        if self.attackCode != BossCogGlobals.BossCogDizzyNow:
            return
        trap = self.traps[self.trapIndex]
        # Once again, ensure skelecogs fly away from the trap if they are targeting it
        # while the CLO falls through it.
        if trap.getSuitId():
            suit = simbase.air.doId2do.get(trap.suitId)
            if suit:
                suit.bossNear(self.trapIndex)
        # Inform both the trap itself and Bumpy that the CLO is falling through this trap.
        if trap.getStatus() != 1:
            if trap.getStatus() == -1:
                trap.startLandBroken()
                self.bumpyNPC.bossLandBroken()
            self.b_setAttackCode(BossCogGlobals.BossCogRecoverDizzyAttack)
            return
        trap.setDuringActivation(1)
        trap.startActivate()
        avIdDict = {}
        # Create a percentage of knockback dealt for each toon that dealt some.
        if self.toonsSoundDamageDealt:
            totalKnockBackDealt = sum(self.toonsSoundDamageDealt.values())
            for avId, knockBackDealt in self.toonsSoundDamageDealt.items():
                avIdDict[avId] = knockBackDealt / totalKnockBackDealt
        else:
            # If no toons dealt damage (she was already in damage position when she was stunned),
            # Then evenly split the credit amongst all toons.
            knockBackDealt = 1.0 / len(self.involvedToons)
            for avId in self.involvedToons:
                avIdDict[avId] = knockBackDealt

        # Get trap damage to check if CLO will die
        if trap.getPrestiged():
            # 135 if quicksand, 210 if trapdoor.
            trapDamage = BossCogGlobals.LawbotBossPrestigedTrapsDamage[trap.trapLevel]
        else:
            # 90 if quicksand, 140 if trapdoor.
            trapDamage = BossCogGlobals.LawbotBossTrapsDamage[trap.trapLevel]

        # Don't do forced area attack or spawn defense cogs if trap will kill
        healthLeft = self.bossMaxDamage - self.bossDamage - trapDamage
        if self.checkIfTrapKills(healthLeft):
            self.sendUpdate("setRandomFallPosition", [0, 220, 0])
            self.sendUpdate("createBossTrapMovie", [self.trapIndex, False])
        else:
            # Conditional for making defense specialists, also doesn't spawn if this trap would kill CLO
            self.setRandomFallPosHpr()
            self.makeDefenseSpecialists(healthLeft, trapDamage, self.shouldSpawnEmpoweredDefense(healthLeft))
            self.sendUpdate("createBossTrapMovie", [self.trapIndex, True])

        taskMgr.doMethodLater(3.5, self.trapHitBoss, self.uniqueName('trapHitBossDelay'), extraArgs=[avIdDict])

    def checkIfTrapKills(self, healthLeft):
        healthPercent = healthLeft / self.bossMaxDamage
        if healthPercent <= 0:
            return True
        else:
            return False

    def shouldSpawnEmpoweredDefense(self, healthLeft):
        healthPercent = healthLeft / self.bossMaxDamage
        if healthPercent <= 0:
            return False
        for i in range(len(BossCogGlobals.LawbotBossDefenseThresholds)):
            # If health is at the last threshold, return true, otherwise check if
            # defense has been spawned for the current threshold.
            if BossCogGlobals.LawbotBossDefenseThresholds[len(
                BossCogGlobals.LawbotBossDefenseThresholds) - 1] >= healthPercent:
                return True
            elif BossCogGlobals.LawbotBossDefenseThresholds[self.lastDefenseThreshold] > BossCogGlobals.LawbotBossDefenseThresholds[i] >= healthPercent:
                self.lastDefenseThreshold = i
                return True
        return False

    def d_resetBossDamageMovie(self, turnTime, rollTime, x, y, h):
        self.sendUpdate("resetBossDamageMovie", [self.stunnedHits, self.maxStunnedHits, turnTime, rollTime, x, y, h])

    def setRandomFallPosHpr(self):
        x = random.randint(BossCogGlobals.LawbotBossBattleFallXMin,
                           BossCogGlobals.LawbotBossBattleFallXMax)
        y = random.randint(BossCogGlobals.LawbotBossBattleFallYMin,
                           BossCogGlobals.LawbotBossBattleFallYMax)
        h = random.randint(-180, 180)
        self.setPosHpr(x, y, -71.601, h, 0, 0)
        self.sendUpdate("setRandomFallPosition", [x, y, h])

    def trapHitBoss(self, avIdDict):
        currState = self.getCurrentOrNextState()
        if currState != 'BattleFour':
            return
        trap = self.traps[self.trapIndex]
        if trap.getPrestiged():
            # 135 if quicksand, 210 if trapdoor.
            bossDamage = BossCogGlobals.LawbotBossPrestigedTrapsDamage[trap.trapLevel]
        else:
            # 90 if quicksand, 140 if trapdoor.
            bossDamage = BossCogGlobals.LawbotBossTrapsDamage[trap.trapLevel]
        # Ensure only up to her max health is dealt, not over.
        if self.bossDamage + bossDamage >= self.bossMaxDamage:
            bossDamage = self.bossMaxDamage - self.bossDamage
        for avId, knockBackPercentage in avIdDict.items():
            # If a toon isn't in the boss' toon list, we don't want to give them credit.
            if self.validate(avId, avId in self.involvedToons, f'hitBoss from unknown avatar {avId}'):
                self.b_updateDamageDealt(avId, math.ceil(bossDamage*knockBackPercentage))
                # Add dept exp for doing dmg
                av = simbase.air.doId2do.get(avId)
                if av:
                    mult = av.getDeptExpMult(ToontownGlobals.DEPARTMENT_LAWBOT)
                    av.addDepartmentExp(bossDamage * mult * knockBackPercentage * 1.5, ToontownGlobals.DEPARTMENT_LAWBOT)
        bossDamage = min(self.getBossDamage() + bossDamage, self.bossMaxDamage)
        self.b_setBossDamage(bossDamage)

        if self.bossDamage >= self.bossMaxDamage:
            self.b_setState('Victory')
        else:
            self.b_setAttackCode(BossCogGlobals.BossCogRecoverDizzyAttack)

    def suitHitBoss(self, suitId):
        avId = self.air.getAvatarIdFromSender()
        # If a toon isn't in the boss' toon list, we don't want to give them credit.
        if not self.validate(avId, avId in self.involvedToons, 'suitHitBoss from unknown avatar'):
            return
        currState = self.getCurrentOrNextState()
        if currState != 'BattleFour':
            return
        # Suits not near the CLO cannot stun/damage her.
        if suitId not in self.nearbyLawyers:
            return
        # CLO cannot be stunned if there are defense specialists alive.
        if len(self.defenseSpecialists) > 0:
            return
        # If the CLO is already stunned, we want the suit to deal small chip damage.
        if self.attackCode == BossCogGlobals.BossCogDizzyNow:
            suit = simbase.air.doId2do.get(suitId)
            if suit:
                dmg = suit.getActualLevel()
                dmg = min(self.getBossDamage() + dmg, self.bossMaxDamage - 1)
                self.b_updateDamageDealt(avId, dmg - self.bossDamage)
                self.b_setBossDamage(dmg)
            return
        toon = self.air.doId2do.get(avId)
        if toon:
            self.toonStunsDict.setdefault(avId, 0)
            self.toonStunsDict[avId] += 1
            self.d_updateStunCount(avId)
            self.timesBossStunned += 1

            # Give all toons dept exp
            for involvedAvId in self.involvedToons:
                involvedAv = self.air.doId2do.get(involvedAvId)
                if involvedAv:
                    mult = involvedAv.getDeptExpMult(ToontownGlobals.DEPARTMENT_LAWBOT)
                    # Give the one who started the stun double xp
                    if involvedAv is toon:
                        mult *= 2
                    xp = 80 * mult
                    diminished_exp = xp * (7 / (7 + .09 * self.timesBossStunned))
                    involvedAv.addDepartmentExp(math.ceil(diminished_exp), ToontownGlobals.DEPARTMENT_LAWBOT)

        self.b_setAttackCode(BossCogGlobals.BossCogDizzyNow)
        self.b_setBossDamage(self.getBossDamage())
        self.b_stopMoveTask(stopMove=True)
        self.chooseRandomTrap()
        # CLO is Stunned Tip
        for avId in self.involvedToons:
            toon = self.air.doId2do.get(avId)
            if toon:
                toon.showToonTip(TTE.TIP_CLO_STUNNED)

    def incrementSuitsDefeated(self, suit, avId, extraMult=1.0):
        av = self.air.doId2do.get(avId)

        if not av:
            self.notify.warning(f"Unknown av {avId} tried to defeat suit")
            return

        if avId in self.toonsNumSuitsDefeated:
            self.toonsNumSuitsDefeated[avId] += 1
        else:
            self.toonsNumSuitsDefeated[avId] = 1
        
        if suit.isElite:
            self.toonsNumExeSuitsDefeated.setdefault(avId, 0)
            self.toonsNumExeSuitsDefeated[avId] += 1

        # Give dept exp for defeating the suit
        mult = av.getDeptExpMult(ToontownGlobals.DEPARTMENT_LAWBOT)
        xp = 8 * suit.getActualLevel() * mult * extraMult
        if extraMult > 1.0:
            self.d_updateCogDestructionCount(avId, 5)
        else:
            self.d_updateCogDestructionCount(avId, 1)
        diminished_exp = xp * (18 / (18 + .16 * self.toonsNumSuitsDefeated[avId]))
        av.addDepartmentExp(math.ceil(diminished_exp), ToontownGlobals.DEPARTMENT_LAWBOT)

    def chooseRandomTrap(self):
        if self.traps is not None:
            # The trap pool for her to choose from is all active traps. Not disabled or broken.
            trapPool = self.getActiveBossTraps()

            # As a fallback, if there is no trap pool from the above then pick a random trap.
            if not trapPool:
                trapPool = self.traps

            currPos = self.getPos()
            currH = self.getH()

            # Force her speed to be the base speed, 2x.
            turnSpeed = self.getCurTurnSpeed(mult=2.5)
            rollSpeed = self.getCurRollSpeed(mult=2)

            # Set up a placeholder node used to determine HPR and distances.
            foo = NodePath("foo")
            foo.setPos(currPos)
            foo.setHpr(self.getHpr())

            traps = []
            for t in trapPool:
                trapPos = t.getPos()
                foo.lookAt(trapPos)

                # Figure out how much the CLO needs to turn to reach this trap.
                toHpr = foo.getHpr()
                trapH = round(PythonUtil.fitDestAngle2Src(currH, toHpr[0]))

                distance = Vec3(trapPos - currPos).length()

                rollTime = (distance / rollSpeed)
                turnTime = abs(trapH - currH) / turnSpeed

                # Create a dictionary keeping track of the attributes of this trap for calculations.
                traps.append({
                    "time": turnTime + rollTime,
                    "trapH": trapH,
                    "trapPos": trapPos,
                    "turnTime": turnTime,
                    "rollTime": rollTime,
                    "distance": distance,
                    "index": self.traps.index(t)
                })

            foo.removeNode()

            # Choose the trap that takes the least amount of time to reach.
            trap = sorted(traps, key=itemgetter("time"))[0]

            # Define some values to use for the chosen trap.
            self.trapIndex = trap["index"]
            trapPos = trap["trapPos"]
            trapH = trap["trapH"]
            turnTime = trap["turnTime"]
            rollTime = trap["rollTime"]
            distance = trap["distance"]

            self.maxStunnedHits = math.ceil(distance)
            self.stunnedHits = 0

            # If the distance is 0 (she is already on the trap), immediately make her fall through it.
            if self.maxStunnedHits == 0:
                self.d_createBossTrapMovie()
                return

            # Set up a placeholder version of the damage movie to use for timing purposes.
            self.bossDamageMovie = Sequence(
                self.hprInterval(turnTime, VBase3(trapH, 0, 0), self.getHpr()),
                self.posInterval(rollTime, trapPos, currPos),
                Func(self.d_createBossTrapMovie)
            )
            self.bossDamageToMovie = self.bossDamageMovie.getDuration() / self.maxStunnedHits
            self.bossDamageMovie.setT(self.stunnedHits * self.bossDamageToMovie)
            self.d_resetBossDamageMovie(turnTime, rollTime, trapPos[0], trapPos[1], trapH)

    def getDisabledBossTraps(self):
        # Return all disabled boss traps.
        if self.traps is not None:
            return [trap for trap in self.traps if trap.getStatus() == 0]
        else:
            return []

    def getBrokenBossTraps(self):
        # Return all broken boss traps.
        if self.traps is not None:
            return [trap for trap in self.traps if trap.getStatus() == -1] # Investigate nearLawyer Bubble Stuff, seems to make it so bumpy will never fix broken traps
        else:
            return []

    def getActiveBossTraps(self):
        # Return all active boss traps.
        if self.traps is not None:
            return [trap for trap in self.traps if trap.getStatus() == 1]
        else:
            return []

    def b_setAttackCode(self, attackCode, avId = 0):
        self.d_setAttackCode(attackCode, avId)
        self.setAttackCode(attackCode, avId)

    def setAttackCode(self, attackCode, avId = 0):
        self.attackCode = attackCode
        self.chatOnAttack(attackCode, avId)
        self.attackAvId = avId
        if attackCode == BossCogGlobals.BossCogDizzyNow:
            # If the CLO is dizzy, we want a variable stun time from 20 seconds to 10 seconds.
            delayTime = self.progressValue(20, 10)
        else:
            delayTime = BossCogGlobals.BossCogAttackTimes.get(attackCode)
            if attackCode == BossCogGlobals.BossCogFrontAttack:
                delayTime += 0.8
            if delayTime is None:
                return
        if attackCode == BossCogGlobals.BossCogRecoverDizzyAttack:
            # If she stops being stunned, clear out some values relevant to the stunned state.
            self.toonsSoundDamageDealt = {}
            self.stunnedHits = 0
            self.maxStunnedHits = 0
            self.trapIndex = -1
        self.waitForNextAttack(delayTime)

    def stopNextAttack(self):
        taskMgr.remove(self.uniqueName("NextAttack"))

    def waitForNextAttack(self, delayTime):
        currState = self.getCurrentOrNextState()
        if currState == 'BattleFour':
            taskName = self.uniqueName('NextAttack')
            taskMgr.remove(taskName)
            taskMgr.doMethodLater(delayTime, self.doNextAttack, taskName)

    def doNextAttack(self, task):
        if self.movingToToon:
            self.waitForNextAttack(3)
            return
        self.b_stopMoveTask()
        if self.attackCode == BossCogGlobals.BossCogDizzyNow:
            attackCode = BossCogGlobals.BossCogRecoverDizzyAttack
        else:
            attackChoices = [
                BossCogGlobals.BossCogAreaAttack,
                BossCogGlobals.BossCogBookDirectedAttack,
                BossCogGlobals.BossCogFrontAttack
            ]
            # Directed book attack is weighted as 4x more likely than the other 2 attacks.
            attackCode = random.choices(attackChoices, weights=[1, 4, 1])[0]
        if attackCode == BossCogGlobals.BossCogAreaAttack:
            self.__decideAreaAttack()
        elif attackCode == BossCogGlobals.BossCogBookDirectedAttack:
            self.__doDirectedAttack()
        else:
            self.b_setAttackCode(attackCode)

    def __decideAreaAttack(self):
        # If criteria is met, do a tornado area attack instead of a normal jump area attack.
        if random.randint(1, 10) > self.progressValue(14, 5):
            self.doTornadoAreaAttack()
        else:
            self.doAreaAttack()

    def doAreaAttack(self):
        self.b_setAttackCode(BossCogGlobals.BossCogAreaAttack)

    def doTornadoAreaAttack(self):
        self.b_setAttackCode(BossCogGlobals.BossCogFourWayTornadoAreaAttack)

    def __doDirectedAttack(self):
        if self.nearToons:
            toonId = random.choice(self.nearToons)
            # 70% chance, never move towards the same toon 2x in a row
            if random.random() >= 0.3 and self.currToon != toonId:
                self.currToon = toonId
                self.doMoveAttack(toonId)
            else:
                # Reset current toon value
                self.currToon = -1
                self.b_setAttackCode(BossCogGlobals.BossCogBookDirectedAttack, toonId)
        else:
            # 40% chance to do move attack, 60% chance to do one of 2 area attacks.
            if random.random() >= 0.6 and len(self.involvedToons) > 0:
                self.doMoveAttack(random.choice(self.involvedToons))
            else:
                self.__decideAreaAttack()

    def doMoveAttack(self, toonId):
        toon = self.air.doId2do.get(toonId)
        if toon:
            currPos = self.getPos()
            currH = self.getH()

            # Set up a placeholder node used to determine HPR and distances.
            foo = NodePath("foo")
            foo.setPos(currPos)
            foo.setHpr(self.getHpr())

            toPos = LPoint3f(toon.getX(), toon.getY(), -71.601)

            # If the toon targeted is outside of the CLO's move bounds, go to the "home" position (middle of room)
            if not (-105 <= toPos[0] <= 110 and 120 <= toPos[1] <= 320):
                toPos = LPoint3f(0, 220, -71.601)

            foo.lookAt(toPos)

            toHpr = foo.getHpr()
            toHpr.setX(toHpr.getX() - 180)
            foo.removeNode()

            # If the CLO is trying to move to a position she is already at, do an area attack instead.
            if toPos == currPos:
                self.__decideAreaAttack()
                return

            self.numMoveAttacks += 1
            self.movingToToon = True
            self.toonDest = toonId

            # Figure out the H rotation required.
            trapH = round(PythonUtil.fitDestAngle2Src(currH, toHpr[0]))

            # Figure out some speed values required for her movement.
            turnSpeed = self.getCurTurnSpeed()
            rollSpeed = self.getCurRollSpeed()

            distance = Vec3(toPos - currPos).length()
            rollTime = distance / rollSpeed

            turnTime = abs(trapH - currH) / turnSpeed

            # Create a serverside version of the movement movie for timing purposes.
            self.moveTrack = Sequence(
                self.hprInterval(turnTime, VBase3(trapH, 0, 0), self.getHpr()),
                self.posInterval(rollTime, toPos, currPos),
                Func(self.reachToon, toonId)
            )
            self.moveTrack.start()

            self.setAttackCode(BossCogGlobals.BossCogMoveAttack, toonId)
            self.sendUpdate("doMoveAttack", [toonId, turnTime, rollTime, toPos[0], toPos[1], trapH])
        else:
            self.b_setAttackCode(BossCogGlobals.BossCogNoAttack)

    def getCurTurnSpeed(self, mult=0):
        if mult == 0:
            mult = self.getDesperationSpeedMult()
        return (BossCogGlobals.LawbotBossTurnSpeedMax - (
                BossCogGlobals.LawbotBossTurnSpeedMax - BossCogGlobals.LawbotBossTurnSpeedMin)) * mult

    def getCurRollSpeed(self, mult=0):
        if mult == 0:
            mult = self.getDesperationSpeedMult()
        return (BossCogGlobals.LawbotBossRollSpeedMax - (
                BossCogGlobals.LawbotBossRollSpeedMax - BossCogGlobals.LawbotBossRollSpeedMin)) * mult

    def getDesperationSpeedMult(self):
        if self.state == 'BattleFour':
            if self.desperationState == 1:
                return 3.0
            elif self.desperationState == 0:
                return 2.4
            else:
                return 2.0
        return 1.0

    def reachToon(self, toonId):
        if self.movingToToon:
            self.b_stopMoveTask()
            self.toonDest = -1

    def b_stopMoveTask(self, stopMove=False):
        self.stopMoveTask()
        self.d_stopMoveTask(stopMove)

    def d_stopMoveTask(self, stopMove=False):
        # this lil chunk of code will ensure that int16/10 is enforced via astron updates
        # it might give slightly off results to the client on the small off-chance the get<COORD> gives some
        # extremely precise value, such as 16.000029012, but its better than crashing the server.
        x = round(self.getX(), 1)
        y = round(self.getY(), 1)
        h = round(self.getH(), 1)
        self.sendUpdate("stopMoveTask", [x, y, h, stopMove])

    def stopMoveTask(self):
        self.movingToToon = False
        if self.moveTrack and self.moveTrack.isPlaying():
            self.moveTrack.pause()
            self.moveTrack = None

    def d_updateStunCount(self, avId):
        self.sendUpdate('updateStunCount', [avId])

    def d_updateCogDestructionCount(self, avId, cogDestroy):
        self.sendUpdate('updateCogDestructionCount', [avId, cogDestroy])

    def b_setBossDamage(self, bossDamage):
        self.setBossDamage(bossDamage)
        self.d_setBossDamage(bossDamage)

    def setBossDamage(self, bossDamage):
        self.bossDamage = bossDamage
        # If the CLO reaches certain health thresholds, change her desperation state and increase spotlight values.
        if self.bossDamage >= self.bossMaxDamage * 0.75:
            self.setDesperationState(1)
            self.setSpotlightVelocityAccel(BossCogGlobals.LawbotBossSpotlightVelocity[1], BossCogGlobals.LawbotBossSpotlightAccel[1])
        elif self.bossDamage >= self.bossMaxDamage * 0.5:
            self.setDesperationState(0)
            self.setSpotlightVelocityAccel(BossCogGlobals.LawbotBossSpotlightVelocity[2], BossCogGlobals.LawbotBossSpotlightAccel[2])
        else:
            self.setDesperationState(-1)

    def setDesperationState(self, desperationState):
        # Ensure that the CLO's depseration state doesn't decrease
        if desperationState > self.desperationState:
            self.desperationState = desperationState

    def getBossDamage(self):
        return self.bossDamage

    def d_setBossDamage(self, bossDamage):
        self.sendUpdate('setBossDamage', [bossDamage, self.desperationState])

    def formatReward(self):
        return str(self.numSues) + ' c&ds'

    def makeBattleOneBattles(self):
        self.postBattleState = 'PrepareBattleTwo'
        self.initializeBattles(1, BossCogGlobals.LawbotBossBattleBackFromTablePosHpr)

    def generateSuits(self, battleNumber):
        if battleNumber == 1:
            return self.invokeSuitPlanner(self.battleOnePlanner, 0)
        else:
            return self.invokeSuitPlanner(self.battleThreePlanner, 1, virtual=True)

    def initializeBattles(self, battleNumber, bossCogPosHpr):
        self.resetBattles()
        if not self.involvedToons:
            self.notify.warning('initializeBattles: no toons!')
            return
        self.battleNumber = battleNumber
        suitHandles = self.generateSuits(battleNumber)
        self.suitsA = suitHandles['activeSuits']
        self.activeSuitsA = self.suitsA[:]
        self.reserveSuits = suitHandles['reserveSuits']
        suitHandles = self.generateSuits(battleNumber)
        self.suitsB = suitHandles['activeSuits']
        self.activeSuitsB = self.suitsB[:]
        self.reserveSuits += suitHandles['reserveSuits']
        if self.toonsA:
            if battleNumber == 1:
                self.battleA = self.makeBattle(bossCogPosHpr, BossCogGlobals.LawyerBattleAPosHpr, self.handleRoundADone, self.handleBattleADone, battleNumber, 0)
            else:
                self.battleA = self.makeBattle(BossCogGlobals.LawbotBossBattleTablePosHpr,
                                               BossCogGlobals.LawyerVirtualBattleAPosHpr, self.handleRoundADone, self.handleBattleADone, battleNumber, 0) # Test this
            self.battleAId = self.battleA.doId
        else:
            self.moveSuits(self.activeSuitsA)
            self.suitsA = []
            self.activeSuitsA = []
            if self.arenaSide is None:
                self.b_setArenaSide(0)
        if self.toonsB:
            if battleNumber == 1:
                self.battleB = self.makeBattle(bossCogPosHpr, BossCogGlobals.LawyerBattleBPosHpr, self.handleRoundBDone, self.handleBattleBDone, battleNumber, 1)
            else:
                self.battleB = self.makeBattle(BossCogGlobals.LawbotBossBattleTablePosHpr,
                                               BossCogGlobals.LawyerVirtualBattleBPosHpr, self.handleRoundBDone, self.handleBattleBDone, battleNumber, 1) # Test this
            self.battleBId = self.battleB.doId
        else:
            self.moveSuits(self.activeSuitsB)
            self.suitsB = []
            self.activeSuitsB = []
            if self.arenaSide is None:
                self.b_setArenaSide(1)
        self.sendBattleIds()

    def forceExitChairs(self, forceExit: bool=False) -> None:
        for chair in self.chairs:
            messenger.send(chair.uniqueName("forceExitChair"), sentArgs=[forceExit])
        
    def handleBattleADone(self, zoneId, toonIds):
        if isinstance(self.battleA, DistributedBattleVirtualAI.DistributedBattleVirtualAI):
            self.d_endCogRoundSpotlight(0)
        ClashBossCogAI.ClashBossCogAI.handleBattleADone(self, zoneId, toonIds)

    def handleBattleBDone(self, zoneId, toonIds):
        if isinstance(self.battleB, DistributedBattleVirtualAI.DistributedBattleVirtualAI):
            self.d_endCogRoundSpotlight(1)
        ClashBossCogAI.ClashBossCogAI.handleBattleBDone(self, zoneId, toonIds)

    def d_endCogRoundSpotlight(self, value):
        self.sendUpdate('endCogRoundSpotlight', [value])

    def makeBattle(self, bossCogPosHpr, battlePosHpr, roundCallback, finishCallback, battleNumber, battleSide):
        if battleNumber == 1:
            battle = DistributedBattlePaintingAI.DistributedBattlePaintingAI(
                self.air, self, roundCallback, finishCallback, battleSide)
        else:
            battle = DistributedBattleVirtualAI.DistributedBattleVirtualAI(
                self.air, self, roundCallback, finishCallback, battleSide)
        self.setBattlePos(battle, bossCogPosHpr, battlePosHpr)
        battle.suitsKilled = self.suitsKilled
        battle.battleCalc.toonSkillPtsGained = self.toonSkillPtsGained
        battle.toonExp = self.toonExp
        battle.toonOrigQuests = self.toonOrigQuests
        battle.toonOrigMerits = self.toonOrigMerits
        battle.toonMerits = self.toonMerits
        battle.toonParts = self.toonParts
        battle.helpfulToons = self.helpfulToons
        # mult = BattleGlobals.getBossBattleCreditMultiplier(battleNumber)
        # if self.air.holidayManager.isHolidayRunning(ToontownGlobals.GAG_EXPERIENCE_HOLIDAY) or self.air.holidayManager.isHolidayRunning(ToontownGlobals.SILLY_GAG):
        #     mult += 1
        # battle.battleCalc.calculateSkillCreditMultiplier(bossBattleNumber = battleNumber)

        battle.generateWithRequired(self.zoneId)
        if battleNumber == 1:
            self.accept(battle.uniqueName("battleFinalFinished"), self.forceExitChairs)
        return battle

    def removeToon(self, avId):
        toon = simbase.air.doId2do.get(avId)
        if toon:
            toon.b_setNumSound(0)
            # Ensure that lawyers are not trying to target dead toons.
            if self.lawyers:
                for lawyer in self.lawyers:
                    if toon.doId in lawyer.nearToons:
                        lawyer.nearToons.remove(toon.doId)
                    if lawyer.targetToon == toon.doId:
                        lawyer.targetToon = None
        ClashBossCogAI.ClashBossCogAI.removeToon(self, avId)

    def enterOff(self):
        self.__deleteBattleTwoObjects()
        self.__deleteBattleFourObjects()
        ClashBossCogAI.ClashBossCogAI.enterOff(self)

    def enterElevator(self):
        ClashBossCogAI.ClashBossCogAI.enterElevator(self)

    def enterIntroduction(self):
        self.calcAndSetBattleDifficulty()
        self.resetBattles()
        self.arenaSide = None
        self.makeBattleOneBattles()
        self.barrier = self.beginBarrier('Introduction', self.involvedToons, 150, self.doneIntroduction)
        self.skipButton = DistributedCutsceneSkipButtonAI.DistributedCutsceneSkipButtonAI(self.air, 'clo', self.involvedToons)
        self.skipButton.generateWithRequired(self.zoneId)
        # Add the CLO to each toon's encountered cogs for the cog gallery.
        typeList = []
        typeList.append({'type': 'clo'})
        for toon in self.involvedToons:
            simbase.air.cogPageManager.toonEncounteredCogs(toon, typeList)

    def exitIntroduction(self):
        self.removeSkipButton()
        ClashBossCogAI.ClashBossCogAI.exitIntroduction(self)
    
    def enterBattleOne(self):
        super().enterBattleOne()
        self.setupChairs()
    
    def exitBattleOne(self):
        super().exitBattleOne()
        self.deleteChairs()

    def enterPrepareBattleTwo(self):
        self.calcAndSetBattleDifficulty()
        self.__makeBattleTwoObjects()
        self.barrier = self.beginBarrier('PrepareBattleTwo', self.involvedToons, 55, self.__donePrepareBattleTwo)
        self.skipButton = DistributedCutsceneSkipButtonAI.DistributedCutsceneSkipButtonAI(self.air, 'clo', self.involvedToons)
        self.skipButton.generateWithRequired(self.zoneId)

    def __donePrepareBattleTwo(self, avIds):
        self.b_setState('BattleTwo')

    def exitPrepareBattleTwo(self):
        self.removeSkipButton()
        self.ignoreBarrier(self.barrier)

    def makeCannons(self):
        if self.cannons is None:
            self.cannons = []
            for index in range(len(BossCogGlobals.LawbotBossCannonPosHprs)):
                cannon = DistributedLawbotCannonAI.DistributedLawbotCannonAI(
                    self.air, self, index, *BossCogGlobals.LawbotBossCannonPosHprs[index]
                )
                cannon.generateWithRequired(self.zoneId)
                self.cannons.append(cannon)

    def __makeBattleTwoObjects(self):
        self.makeCannons()
        self.makeGavels()

    def deleteCannons(self):
        if self.cannons is not None:
            for cannon in self.cannons:
                cannon.requestDelete()

            self.cannons = None

    def __deleteBattleTwoObjects(self):
        self.deleteCannons()
        self.deleteGavels()
        self.resetLawyers()

    def enterBattleTwo(self):
        self.startBattleTime()
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleTwoPosHpr)
        self.setZ(0)
        self.makeInitialLawyers()
        self.enableGavels()
        self.barrier = self.beginBarrier("BattleTwo", self.involvedToons, BossCogGlobals.LawbotBossEvidenceRoundTime + 1, self.__doneBattleTwo)

    def exitBattleTwo(self):
        self.ignoreBarrier(self.barrier)
        self.stopBattleTime()
        self.resetBattles()
        self.stopAttacks()
        self.__deleteBattleTwoObjects()

    def __doneBattleTwo(self, avIds):
        self.b_setState('PrepareBattleThree')

    def enterPrepareBattleThree(self):
        self.barrier = self.beginBarrier('PrepareBattleThree', self.involvedToons, 35, self.__donePrepareBattleThree)
        self.divideToons()
        self.makeBattleThreeBattles()
        self.skipButton = DistributedCutsceneSkipButtonAI.DistributedCutsceneSkipButtonAI(self.air, 'clo', self.involvedToons)
        self.skipButton.generateWithRequired(self.zoneId)

    def exitPrepareBattleThree(self):
        self.removeSkipButton()
        self.ignoreBarrier(self.barrier)

    def makeBattleThreeBattles(self):
        self.postBattleState = "PrepareBattleFour"
        self.initializeBattles(2, BossCogGlobals.LawbotBossBattleBackFromTablePosHpr)

    def __donePrepareBattleThree(self, avIds):
        self.b_setState("BattleThree")

    def enterBattleThree(self):
        self.makeBattleThreeBattles()
        if self.battleA:
            self.battleA.startBattle(self.toonsA, self.suitsA)
        if self.battleB:
            self.battleB.startBattle(self.toonsB, self.suitsB)

    def exitBattleThree(self):
        self.resetBattles()

    def enterPrepareBattleFour(self):
        self.calcAndSetBattleDifficulty()
        self.barrier = self.beginBarrier('PrepareBattleFour', self.involvedToons, 60, self.__donePrepareBattleFour)
        self.skipButton = DistributedCutsceneSkipButtonAI.DistributedCutsceneSkipButtonAI(self.air, 'clo', self.involvedToons)
        self.skipButton.generateWithRequired(self.zoneId)

    def __donePrepareBattleFour(self, avIds):
        self.b_setState('BattleFour')

    def exitPrepareBattleFour(self):
        self.removeSkipButton()
        self.ignoreBarrier(self.barrier)

    def enterBattleFour(self):
        # Take away throwables, like from quests or snowballs
        self.takeAwayPies()
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleTwoPosHpr)
        self.startBattleTime()
        self.battleFourTimeStarted = globalClock.getFrameTime()
        self.calcAndSetBattleDifficulty()
        self.air.writeServerEvent('lawbotBossSettings', self.doId, '%s|%s' % (
            self.dept,
            self.toonupValue
        ))
        self.__makeBattleFourObjects()
        self.resetBattles()
        self.battleThreeStart = globalClock.getFrameTime()
        self.calculateEvidenceType()
        self.waitForNextAttack(9)
        self.numToonsAtStart = len(self.involvedToons)
        # Getting Sound Evidence Tip
        for avId in self.involvedToons:
            toon = simbase.air.doId2do.get(avId)
            if toon:
                toon.showToonTip(TTE.TIP_CLO_GET_EVIDENCE)

    def calculateEvidenceType(self):
        # Bugle at 0, Aoogah at 30, Trunk at 65, Fog at 100.
        for toonId in self.involvedToons:
            if toonId in self.evidence:
                evidenceAmt = self.evidence[toonId]

                if evidenceAmt >= BossCogGlobals.LawbotBossSoundEvidenceRequirement['fog']:
                    self.soundTypes[toonId] = 6
                elif evidenceAmt >= BossCogGlobals.LawbotBossSoundEvidenceRequirement['trunk']:
                    self.soundTypes[toonId] = 5
                elif evidenceAmt >= BossCogGlobals.LawbotBossSoundEvidenceRequirement['aoogah']:
                    self.soundTypes[toonId] = 4
                else:
                    self.soundTypes[toonId] = 3
            else:
                self.soundTypes[toonId] = 3

            toon = self.air.getDo(toonId)
            if toon:
                toon.b_setSoundType(self.soundTypes.get(toonId, 3))
                toon.b_setNumSound(0)

    def __makeBattleFourObjects(self):
        self.makeBossTrackingSpotlights()
        self.makeInitialLawyers()
        self.makeBumpyNPC()
        self.makeBossTraps()
        self.makeBossSpotlights()

    def __deleteBattleFourObjects(self):
        self.resetLawyers()
        self.deleteBossTrackingSpotlights()
        self.deleteBossSpotlights()
        self.removeBumpyNPC()
        self.deleteBossTraps()

    def doBattleFourInfo(self):
        didTheyWin = 0
        if self.bossDamage == BossCogGlobals.LawbotBossMaxDamage:
            didTheyWin = 1
        self.battleFourTimeInMin = globalClock.getFrameTime() - self.battleFourTimeStarted
        self.battleFourTimeInMin /= 60.0
        self.numToonsAtEnd = 0
        toonHps = []
        for toonId in self.involvedToons:
            toon = simbase.air.doId2do.get(toonId)
            if toon:
                self.numToonsAtEnd += 1
                toonHps.append(toon.getHp())

        self.air.writeServerEvent('b3Info', self.doId, '%d|%.2f|%d|%d|%d|%d|%s' % (
            didTheyWin,
            self.battleFourTimeInMin,
            self.numToonsAtStart,
            self.numToonsAtEnd,
            self.toonupValue,
            self.numAreaAttacks,
            toonHps
        ))

    def exitBattleFour(self):
        taskMgr.remove(self.uniqueName('NextLawyer'))
        self.stopBattleTime()
        self.doBattleFourInfo()
        self.stopAttacks()
        self.__deleteBattleFourObjects()
        self.deleteTreasures()

    def enterVictory(self):
        self.resetBattles()
        self.suitsKilled.append({
            'type': 'clo',
            'level': None,
            'track': self.dna.dept,
            'isSkelecog': 0,
            'isForeman': 0,
            'isBoss': 1,
            'isSupervisor': 0,
            'isVirtual': 0,
            'hasRevives': 0,
            'isElite': 0,
            'activeToons': self.involvedToons[:]
        })
        self.barrier = self.beginBarrier('Victory', self.involvedToons, 45, self.__doneVictory)

    def __doneVictory(self, avIds):
        self.notify.info("LogStats LawbotBossWasDefeated")

        for toonId in self.involvedToons:
            self.notify.info("LogStats ToonDefeatedLawbotBoss toonid %s" % toonId)
            toon = self.air.doId2do.get(toonId)
            if not toon:
                continue

            # Add dept exp bonus for winning the boss
            mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_LAWBOT)
            toon.addDepartmentExp(1000 * mult, ToontownGlobals.DEPARTMENT_LAWBOT)

            self.handleUniteRewards(toon)
            self.giveCeaseDesistReward(toon, toonId)
            toon.b_promote(self.deptIndex)
            if toon.cogTypes[self.deptIndex] == 7 and toon.cogLevels[self.deptIndex] >= 7:
                toon.getHammerspace().addItem(BackgroundItemType.HQ_Lawbot)
            # Promotion + Reward Tips
            toon.showToonTip(TTE.TIP_DISGUISE_PROMOTION)
            toon.showToonTip(TTE.TIP_REWARDS_CEASE_AND_DESIST)
            # Unite tip
            toon.showToonTip(TTE.TIP_REWARDS_UNITE)

            if self.begunToonAmount == 1:
                self.notify.info("LogStats ToonSoloDefeatedLawbotBoss toonid %s" % toonId)
            self.air.achievementsManager.clo(toonId, numPlayers=self.begunToonAmount)

            # Handle boss specific quests
            simbase.air.quest3Manager.progressObjective(
                toon, 
                LawbotBossContext(
                    "l",
                    self.toonStunsDict.get(toonId, 0),
                    self.toonDamagesDict.get(toonId, 0),
                    self.evidence.get(toonId, 0),
                    (
                        self.toonsNumSuitsDestroyed.get(toonId, 0),
                        self.toonsNumSuitsDefeated.get(toonId, 0),
                    ),
                    (
                        self.toonsNumExeSuitsDestroyed.get(toonId, 0),
                        self.toonsNumExeSuitsDefeated.get(toonId, 0),
                    ),
                )
            )

        self.prepareReward()
        self.rewardClubCoins()

    def giveCeaseDesistReward(self, toon, toonId):
        # Give the toon the needed bonuses depending on dept level, holiday, and daily bonus.
        bonusSlips = 0
        departmentLevel = toon.getDepartmentLevel(ToontownGlobals.DEPARTMENT_LAWBOT)
        if departmentLevel == ToontownGlobals.MaxDepartmentLevel[ToontownGlobals.DEPARTMENT_LAWBOT]:
            bonusSlips += 2
        bonusSlips = toon.applyBoosters([BoosterItemType.Reward_Boss_Global, BoosterItemType.Reward_Boss_Lawbot], bonusSlips)
        # toon.queueScavenge(self.numSues + bonusSlips, ScavengeType.Ceases, [])
        toon.getHammerspace().addItem(MaterialItemType.CeaseAndDesists, self.numSues + bonusSlips)
        self.d_setNumSuesEarned(toonId, self.numSues + bonusSlips)

    def d_setNumSuesEarned(self, toonId, numSues):
        # Inform the client of the gained c&ds for bumpy's victory dialogue.
        self.sendUpdate('setNumSuesEarned', [toonId, numSues])

    def exitVictory(self):
        self.deleteBossTraps()
        self.takeAwaySound()

    def enterFrolic(self):
        super().enterFrolic()
        self.b_setBossDamage(0)
        self.setupChairs()
    
    def exitFrolic(self):
        super().exitFrolic()
        self.deleteChairs()

    def takeAwaySound(self):
        for toonId in self.involvedToons:
            toon = simbase.air.doId2do.get(toonId)
            if toon:
                toon.b_setNumSound(0)

    def takeAwayPies(self):
        for toonId in self.involvedToons:
            toon = simbase.air.doId2do.get(toonId)
            if toon:
                toon.b_setNumPies(0)

    @staticmethod
    def getSoundDamage(soundType):
        return BossCogGlobals.LawbotBossSoundDamage.get(soundType, 1)

    def makeBossTraps(self):
        if self.traps is None:
            self.traps = []
            for index in range(len(BossCogGlobals.LawbotBossTrapsPosHpr)):
                # If the trap is index 0, make it a trapdoor. Else, it should be a quicksand.
                trapLevel = 5 if index in BossCogGlobals.LawbotBossTrapdoorsList else 4
                trap = DistributedLawbotBossTrapAI.DistributedLawbotBossTrapAI(self.air, self, index, trapLevel)
                trap.generateWithRequired(self.zoneId)
                trap.setPosHpr(*BossCogGlobals.LawbotBossTrapsPosHpr[index])
                self.traps.append(trap)

    def deleteBossTraps(self):
        if self.traps is not None:
            for trap in self.traps:
                trap.requestDelete()

            self.traps = None

    def makeBossSpotlights(self):
        if self.spotlights is None:
            self.spotlights = []
            for index in range(len(BossCogGlobals.LawbotBossSpotlightPosList)):
                spotlight = DistributedLawbotBossSecurityCameraAI.DistributedLawbotBossSecurityCameraAI(
                    self.air, self, BossCogGlobals.LawbotBossSpotlightPosList[index][:],
                    BossCogGlobals.LawbotBossSpotlightDamage
                )
                spotlight.generateWithRequired(self.zoneId)
                self.spotlights.append(spotlight)

    def deleteBossSpotlights(self):
        if self.spotlights is not None:
            for spotlight in self.spotlights:
                spotlight.requestDelete()

            self.spotlights = None

    def makeBossTrackingSpotlights(self):
        if self.trackingSpotlights is None:
            self.trackingSpotlights = []
            for index in range(len(BossCogGlobals.LawbotBossTrackingSpotlightPosList)):
                spotlight = DistributedLawbotBossSecurityCameraAI.DistributedLawbotBossSecurityCameraAI(
                    self.air, self, BossCogGlobals.LawbotBossTrackingSpotlightPosList[index][:],
                    BossCogGlobals.LawbotBossSpotlightDamage, tracking=1
                )
                spotlight.generateWithRequired(self.zoneId)
                self.trackingSpotlights.append(spotlight)

    def deleteBossTrackingSpotlights(self):
        if self.trackingSpotlights is not None:
            for spotlight in self.trackingSpotlights:
                spotlight.requestDelete()

            self.trackingSpotlights = None

    def setSpotlightVelocityAccel(self, velocity, acceleration):
        for spotlight in self.spotlights:
            spotlight.b_setVelocity(velocity)
            spotlight.b_setAcceleration(acceleration)

    def makeBumpyNPC(self):
        npcId = 2009
        self.bumpyNPC = DistributedNPCBumpyAI(self.air, self, npcId)
        self.bumpyNPC.setPosHpr(*BossCogGlobals.LawbotBossBumpyPosHpr)
        npcToon = NPCToons.NPCToonDict.get(npcId)
        npcToon.zoneId = self.zoneId
        npcToon.createNPC(self.bumpyNPC, 0)
        self.bumpyNPC.initializeTimers()

    def removeBumpyNPC(self):
        if self.bumpyNPC:
            self.bumpyNPC.requestDelete()
            self.bumpyNPC = None

    def resetLawyers(self):
        if not hasattr(self, 'lawyers'):
            # just in case some weird order of operations happens _after_ the DO is deleted
            self.lawyers = []
            self.lawyerPositions = {}
            return
        for suit in self.lawyers:
            suit.requestDelete()

        self.lawyers = []
        self.lawyerPositions = {}

    def sendLawyerId(self, lawyer):
        self.sendUpdate('sendLawyerId', [lawyer.doId])

    def sendDefenseSpecialistId(self, lawyer):
        self.sendUpdate('sendDefenseSpecialistId', [lawyer.doId])

    def getLawyerSpawnRate(self):
        toonsAmount = len(self.involvedToons)
        if toonsAmount >= 7:
            return 8
        elif toonsAmount >= 5:
            return 10
        else:
            return 12

    def makeInitialLawyers(self):
        self.resetLawyers()

        currState = self.getCurrentOrNextState()
        if currState == "BattleTwo":
            for i in range(10):
                self.makeLawyer(i)

            self.waitForNextLawyers(self.getLawyerSpawnRate())
        elif currState == "BattleFour":
            # Cogs below num 0 are considered virtuals.
            for i in range(-2, 10):
                self.makeLawyer(i, virtual=i < 0)

            self.waitForNextLawyers()

    def waitForNextLawyers(self, delayTime=12):
        currState = self.getCurrentOrNextState()
        if currState in ("BattleTwo", "BattleFour"):
            taskName = self.uniqueName('NextLawyer')
            taskMgr.remove(taskName)
            taskMgr.doMethodLater(delayTime, self.makeLawyers, taskName)

    def makeLawyers(self, taskName):
        currState = self.getCurrentOrNextState()
        if currState == "BattleTwo":
            availablePaintings = list(range(10))
            random.shuffle(availablePaintings)
            for i in availablePaintings:
                if len(self.lawyers) >= self.maxLawyersBattleTwo:
                    break
                # Chance to spawn Executive Skelecog
                elite = random.random() <= 0.12
                self.makeLawyer(i, elite=elite)

            self.waitForNextLawyers(self.getLawyerSpawnRate())
        elif currState == "BattleFour":
            sortedLawyersPerPainting = {p: l for p, l in sorted(self.lawyersPerPainting.items(), key=itemgetter(1))}
            for i in sortedLawyersPerPainting:
                if len(self.lawyers) >= self.maxLawyersBattleFour:
                    break
                self.makeLawyer(i)

            self.waitForNextLawyers()

    def makeLawyer(self, painting, virtual=False, elite=False):
        currState = self.getCurrentOrNextState()
        if currState == "BattleTwo":
            level = random.randint(1, 15)
        else:
            level = int(math.ceil(self.progressValue(2, self.lawyerMaxLevel)))
        spotlight = None
        suit = ClashLawbotBossSuitAI.ClashLawbotBossSuitAI(self, self.air, None, painting)
        suit.dna = SuitDNA.SuitDNA()

        suitDept = 'l'

        if virtual:
            spotlight = painting + 2
            spotlight = self.trackingSpotlights[spotlight]
            # Force the virtuals to be level 15 legal eagles.
            suit.dna.newSuitRandom(7, suitDept, wantAlts=0)
            suit.setLevel(15)
            suit.setVirtual(1)
        else:
            suitType = SuitDNA.getRandomSuitType(level)
            suit.dna.newSuitRandom(suitType, suitDept, wantAlts = not elite)
            suit.setLevel(level)
            self.lawyersPerPainting[painting] = self.lawyersPerPainting.get(painting, 0) + 1
        if currState == "BattleFour":
            # If a painting is in the middle, spawn a guaranteed skelecog.
            # Else, there is a 15% chance for the cog to become a skelecog.
            if ((painting in (4, 5) or (random.random() <= 0.15 and not virtual)) and not SuitDNA.isAlternate(suit.dna.name)):
                elite = True
        if elite:
            suit.setElite(1)
        suit.setPosHpr(*BossCogGlobals.LawbotBossLawyerPosHprs[painting])
        suit.generateWithRequired(self.zoneId)
        # Grab the cog's specialization for health purposes.
        specialization = SuitBattleGlobals.SuitAttributes[suit.dna.name].get('specialization', SuitBattleGlobals.NORMAL)
        health = SuitBattleGlobals.calculateHp({'specialization': specialization}, level, dnaName=suit.dna.name)
        # If the cog is elite, increase it's max HP by 1.5x
        if suit.isElite:
            health *= 1.5
        suit.b_setSuitMaxDamage(int(health))
        if spotlight is not None:
            # For virtuals, they need a spotlight attached to them for tracking.
            spotlight.b_setTrackingDoId(suit.doId)
            suit.waitForNextMove(BossCogGlobals.LawbotBossLawyerVirtualInitialDelay)
        else:
            delay = BossCogGlobals.LawbotBossLawyerInitialDelay
            if currState == "BattleFour":
                self.d_createPaintingMovie(painting)
                delay *= 2
            suit.waitForNextMove(delay)
        self.lawyers.append(suit)
        self.lawyerPositions[suit] = suit.getPos()
        self.sendLawyerId(suit)

    def removeLawyer(self, lawyer, painting):
        # Attempt to remove the lawyer from nearby lawyers
        self.lawyerNearExit(lawyer.doId)

        lawyersPerPainting = self.lawyersPerPainting.get(painting, 0)
        self.lawyersPerPainting[painting] = max(lawyersPerPainting - 1, 0)

        # Lawyer removed from boss lawyer list inside of suit removeLawyer function
        lawyer.removeLawyer()

    def d_createPaintingMovie(self, painting):
        self.sendUpdate('createPaintingMovie', [painting])

    def lawyerNearEnter(self, lawyerDoId):
        if lawyerDoId not in self.nearbyLawyers:
            self.nearbyLawyers.append(lawyerDoId)

    def lawyerNearExit(self, lawyerDoId):
        try:
            self.nearbyLawyers.remove(lawyerDoId)
        except Exception:
            pass

    def b_setMaxHp(self, hp):
        self.setMaxHp(hp)
        self.d_setMaxHp(hp)

    def setMaxHp(self, hp):
        self.bossMaxDamage = hp

    def d_setMaxHp(self, hp):
        self.sendUpdate('setMaxHp', [hp])

    def calcAndSetBattleDifficulty(self):
        # Max flying cogs in the cannon/evidence round
        self.maxLawyersBattleTwo = 16 + math.ceil(len(self.involvedToons) * 1.5)
        # Max flying cogs in the sound round
        self.maxLawyersBattleFour = 14 + len(self.involvedToons) // 2
        # Grab the sound damage toons should deal from Globals.
        self.soundDamage = BossCogGlobals.LawbotBossSoundKnockback.get(len(self.involvedToons), 1)
        self.getToonDifficulty()
        # Sets CLO HP, cog levels, # of sound, # of c&ds gained, and max flying cog level in sound round
        self.b_setMaxHp(BossCogGlobals.LawbotBossMaxDamage[2])
        self.numSound = 30
        self.numSues = 6
        self.lawyerMaxLevel = 10
        self.damageMult = BossCogGlobals.LawbotBossDamageMultipliers[2]
        self.battleOnePlanner = ClashSuitBuildingGlobals.SPE.CLO_HARD
        self.battleThreePlanner = ClashSuitBuildingGlobals.SPE.CLO_SKELECOGS_HARD
        self.universalUnites = 4

    def giveEvidence(self, toonID, evidenceAmt, extraMult=1.0):
        currEvidence = self.evidence.get(toonID, 0)
        self.evidence[toonID] = currEvidence + evidenceAmt
        self.d_updateEvidence(toonID, evidenceAmt)

        # Give dept exp for gaining evidence and check for nameplate
        toon = self.air.doId2do.get(toonID)
        if toon:
            mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_LAWBOT)
            xp = 4 * evidenceAmt * mult * extraMult
            toon.addDepartmentExp(math.ceil(xp), ToontownGlobals.DEPARTMENT_LAWBOT)

            # Nameplate Reward for Max Evidence
            if self.evidence[toonID] >= BossCogGlobals.LawbotBossSoundEvidenceRequirement['max']:
                toon.addItem(NameplateItemType.Special_UpToEleven)

    def d_updateEvidence(self, avId, evidenceAmt):
        self.sendUpdate('updateEvidence', [avId, evidenceAmt])

    def withdrawEvidence(self):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if av:
            # If a toon does not have a defined sound type for the boss (for some reason),
            # then give them a kazoo by default.
            if avId in self.soundTypes:
                soundType = self.soundTypes[avId]
            else:
                soundType = 0
            av.b_setSoundType(soundType)
            av.b_setNumSound(self.numSound)
            # Using Sound Evidence Tip
            av.showToonTip(TTE.TIP_CLO_USE_EVIDENCE)
    
    def cannon_destroyedSuit(self, suit: ClashLawbotBossSuitAI.ClashLawbotBossSuitAI, avId: int) -> None:
        if suit.isElite:
            self.toonsNumExeSuitsDestroyed.setdefault(avId, 0)
            self.toonsNumExeSuitsDestroyed[avId] += 1
        
        self.toonsNumSuitsDestroyed.setdefault(avId, 0)
        self.toonsNumSuitsDestroyed[avId] += 1

    def makeGavels(self):
        if self.gavels is None:
            self.gavels = []
            for index in range(len(BossCogGlobals.LawbotBossGavelPosHprs)):
                gavel = DistributedLawbotBossGavelAI.DistributedLawbotBossGavelAI(self.air, self, index)
                gavel.generateWithRequired(self.zoneId)
                self.gavels.append(gavel)

    def enableGavels(self):
        if self.gavels is not None:
            for gavel in self.gavels:
                gavel.startMoving()

    def deleteGavels(self):
        if self.gavels is not None:
            for gavel in self.gavels:
                gavel.requestDelete()

            self.gavels = None

    def startBattleTime(self):
        self.battleTimeStarted = globalClock.getFrameTime()

    def stopBattleTime(self):
        self.battleTimeStarted = 0

    def progressValue(self, fromValue, toValue):
        t0 = float(self.bossDamage) / float(self.bossMaxDamage)
        elapsed = globalClock.getFrameTime() - self.battleTimeStarted
        t1 = elapsed / float(self.battleDuration)
        t = max(t0, t1)
        return fromValue + (toValue - fromValue) * min(t, 1)

    def makeTreasure(self, lawyer, av):
        if self.state != 'BattleFour':
            return
        # If the max amount of treasures has been reached, dont
        if len(self.treasures) >= self.maxTreasures:
            return
        # If the lawyer is by the CLO, there is a 50% (scales up based on number of players) chance for it to dont
        if lawyer.doId in self.nearbyLawyers:
            if random.random() > 0.45 + 0.05 * len(self.involvedToons):
                return

        lawyerPos = lawyer.getPos()
        avPos = av.getPos()
        v = Vec3(avPos[0], avPos[1], 0.0)

        angle = random.uniform(0.0, 2.0 * math.pi)
        radius = 6
        dx = radius * math.cos(angle)
        dy = radius * math.sin(angle)
        fpos = Point3(v[0] + dx, v[1] + dy, 0)
        bounds = BossCogGlobals.LawbotBossTreasureBounds
        # Ensure the treasure's positions is within the bounds of the room
        fpos = Point3(min(max(fpos[0], bounds[0][0]), bounds[0][1]), min(max(fpos[1], bounds[1][0]), bounds[1][1]), 0)
        lawyerLevel = lawyer.getActualLevel()
        # Determine the playground style for this treasure
        if lawyerLevel <= 3:
            styleList = [ToontownGlobals.ToontownCentral,
                         ToontownGlobals.DonaldsDock,
                         ToontownGlobals.YeOlde,
                         ToontownGlobals.GolfZone,
                         ToontownGlobals.GoofySpeedway,
                         ToontownGlobals.DaisyGardens]
        elif lawyerLevel <= 5:
            styleList = [ToontownGlobals.DonaldsDock,
                         ToontownGlobals.YeOlde,
                         ToontownGlobals.GolfZone,
                         ToontownGlobals.GoofySpeedway,
                         ToontownGlobals.DaisyGardens,
                         ToontownGlobals.MinniesMelodyland]
        elif lawyerLevel <= 7:
            styleList = [ToontownGlobals.MinniesMelodyland,
                         ToontownGlobals.TheBrrrgh,
                         ToontownGlobals.OutdoorZone,
                         ToontownGlobals.DonaldsDreamland]
        else:
            styleList = [ToontownGlobals.OutdoorZone,
                         ToontownGlobals.DonaldsDreamland]
        style = random.choice(styleList)
        healAmount = math.ceil(lawyerLevel * 1.5)
        treasure = DistributedLawbotBossTreasureAI.DistributedLawbotBossTreasureAI(self.air, self, lawyer, style, lawyerPos[0], lawyerPos[1], lawyerPos[2], fpos[0], fpos[1], -71.601)
        treasure.generateWithRequired(self.zoneId)
        treasure.healAmount = healAmount
        self.treasures[treasure.doId] = treasure

    def grabAttempt(self, avId, treasureId):
        av = self.air.doId2do.get(avId)
        if not av:
            return
        treasure = self.treasures.get(treasureId)
        if treasure:
            if treasure.validAvatar(av):
                del self.treasures[treasureId]
                treasure.d_setGrab(avId)
                taskMgr.doMethodLater(5, treasure.requestDelete, treasure.uniqueName('deleteTreasure'), extraArgs=[])
            else:
                treasure.d_setReject()

    def deleteTreasures(self):
        for treasure in list(self.treasures.values()):
            taskMgr.remove(treasure.uniqueName("deleteTreasure"))
            treasure.requestDelete()

        self.treasures = {}

    def zapToon(self, x, y, z, h, p, r, bpx, bpy, attackCode, timestamp):
        currState = self.getCurrentOrNextState()
        # You shouldn't take damage during the Cannon Round
        if currState == "BattleTwo":
            return
        avId = self.air.getAvatarIdFromSender()
        if not self.validate(avId, avId in self.involvedToons, 'zapToon from unknown avatar'):
            return
        toon = simbase.air.doId2do.get(avId)
        if toon:
            self.d_showZapToon(avId, x, y, z, h, p, r, attackCode, timestamp)
            damage = BossCogGlobals.BossCogDamageLevels.get(attackCode)
            if damage is None:
                self.notify.warning('No damage listed for attack code %s' % attackCode)
                damage = 5
            damage *= self.getDamageMultiplier()
            # If the CLO is stunned, being rammed/bumped deals 4 damage.
            # Else, it is multiplied by her normal damage multiplier.
            if attackCode == BossCogGlobals.BossCogElectricFence:
                damage = 4
                if self.attackCode != BossCogGlobals.BossCogDizzyNow:
                    damage *= self.getDamageMultiplier()
            damage = math.floor(damage)
            self.damageToon(toon, damage)

    def getDamageMultiplier(self):
        mult = ClashBossCogAI.ClashBossCogAI.getDamageMultiplier(self)
        return mult * self.damageMult

    def makeDefenseSpecialists(self, healthLeft, trapDamage, empoweredSpawn):
        healthPercent = healthLeft / self.bossMaxDamage
        levelList = []
        if empoweredSpawn:
            levelList.append(15)
            # At 40% health, replace a Conveyancer with Advocate
            if healthPercent <= 0.4:
                levelList.append(15)
            else:
                levelList.append(8)
            # At 60% health, replace Pettifogger with Advocate
            if healthPercent <= 0.6:
                levelList.append(15)
            else:
                levelList.append(7)
            # At 20% health, replace a Conveyancer with Advocate
            if healthPercent <= 0.2:
                levelList.append(15)
            else:
                levelList.append(8)
        else:
            # All Conveyancers under 50%, otherwise Pettifoggers
            if healthPercent <= 0.5:
                levelList = [8, 8, 8, 8]
            else:
                levelList = [7, 7, 7, 7]
        for i in range(len(levelList)):
            suit = DistributedLawbotBossDefenseSpecialistAI(self, self.air, None)

            level = levelList[i]
            if level <= 7:
                # Levels 2 - 7: Pettifogger
                suitName = 'pf'
            elif level == 8:
                # Level 8: Conveyancer
                suitName = 'cv'
            else:
                # Level 9 - 15: Advocate
                suitName = 'ad'

            actualSuitName = suitName

            # Make DNA for the chosen specialist
            suit.dna = SuitDNA.SuitDNA()
            suit.dna.newSuit(actualSuitName)
            suit.setLevel(level)
            suit.setElite(1)
            suit.setPosHpr(*BossCogGlobals.LawbotBossDefenseSpecialistPos[i])
            suit.generateWithRequired(self.zoneId)

            # Get base health and scale it for each toon beyond 4
            health = BossCogGlobals.LawbotBossDefenseHealth[suitName][0]
            health = health + BossCogGlobals.LawbotBossDefenseHealth[suitName][1] * max(0, len(self.involvedToons) - 4)
            # Scale health further based on trap damage
            damageRange = BossCogGlobals.LawbotBossPrestigedTrapsDamage[5] - BossCogGlobals.LawbotBossTrapsDamage[4]
            adjustedTrapDamage = trapDamage - BossCogGlobals.LawbotBossTrapsDamage[4]
            healthScale = lerp(1, BossCogGlobals.LawbotBossDefenseHealthScaling, adjustedTrapDamage / damageRange)
            health = health * healthScale
            suit.b_setSuitMaxDamage(int(health))
            self.defenseSpecialists.append(suit)
            self.sendDefenseSpecialistId(suit)
