import random
from otp.ai.AIBaseGlobal import *
from otp.avatar import DistributedAvatarAI
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.statuses.StatusEffectEnums import SEE
from toontown.clashbattle.battle.statuses import StatusEffectGlobals as SEG
from toontown.clashbattle.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.clashsuit.suit import SuitBase
from toontown.clashsuit.suit import SuitDNA
from toontown.shtiker import CogPageGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.clashbattle.battle import SuitBattleGlobals
from toontown.clashbattle.battle import PassiveAttributeDefs
from toontown.clashsuit.suit.SuitDefinitionsBase import SuitDefinitions


@DirectNotifyCategory()
class DistributedSuitBaseAI(DistributedAvatarAI.DistributedAvatarAI, SuitBase.SuitBase):
    def __init__(self, air, suitPlanner):
        DistributedAvatarAI.DistributedAvatarAI.__init__(self, air)
        SuitBase.SuitBase.__init__(self)

        self.sp = suitPlanner

        # the current health of this suit
        # for now use some default values, these are pulled
        # from a table once the suit's level is determined
        self.maxHp = 10
        self.hp = 10
        self.zoneId = 0
        self.dna = SuitDNA.SuitDNA()

        self.virtual = 0  # the red glowing effect
        self.waiter = 0
        self.isElite = 0

        self.dmgMult = 1.0
        self.skeleRevives = 0  # number of times to reanimate into a skelecog
        self.maxSkeleRevives = 0  # keep track of how many times we have reanimated
        self.reviveFlag = 0
        self.overhealed = 0
        self.hpMultIndex = 0
        self.noRegularAttackRounds = 0
        self.calculatedHpAlready = False
        self.persistent = False

        # This is filled in only if the suit is trying to take over a building of a particular height.
        self.buildingHeight = None

        # Sometimes, even when we have a suit planner, we will really want the suit to clean up.
        # In particular, when removeSuit is called already (avoid a circular call)
        self.forceRemove = False

        # Effects in dict format
        # effectId
        # rounds
        self.startingStatusEffects = []
        self.startingVisualEffects = []
        # Skelecog and Virtuals have a randomly chosen health value
        self.healthPercentChosen = None

    def generate(self):
        """
        Called when the DistributedObject is reintroduced to the world, either for the first time or from the cache.
        """
        DistributedAvatarAI.DistributedAvatarAI.generate(self)
        # Ensure the health is up to date if we need to update it
        if self.healthPercentChosen is not None:
            self.b_setMaxHp(self.calculateHp())

    def delete(self):
        self.sp = None
        del self.dna

        DistributedAvatarAI.DistributedAvatarAI.delete(self)
        SuitBase.SuitBase.delete(self)
    
    def applyStartingStatusEffects(self):
        if self.dna.name in SuitBattleGlobals.SuitAttributes:
            info = SuitBattleGlobals.SuitAttributes[self.dna.name]
            if "passives" in info:
                if PassiveAttributeDefs.STATUS_EFFECTS in info["passives"]:
                    statusEffects = info["passives"][PassiveAttributeDefs.STATUS_EFFECTS]
                    if not isinstance(statusEffects, list):
                        statusEffects = [statusEffects]

                    for effectId in statusEffects:
                        self.addStatusEffect(effectId)

                # Add a lure resistance effect based on the lure resistance passive given
                if PassiveAttributeDefs.LURE_RESISTANCE in info["passives"]:
                    self.addStatusEffect(SEE.EFFECT_LURE_RESISTANCE, extraArgs=[info["passives"][PassiveAttributeDefs.LURE_RESISTANCE]])

            self.addStatusEffect(info["attackBehavior"])

        # Also add any starting effects defined on the suit
        for effectDict in self.startingStatusEffects:
            effectId = effectDict['effectId']
            rounds = effectDict['rounds']
            extraArgs = effectDict['extraArgs']
            newEffect = SEG.createStatusEffect(self, effectId, extraArgs)
            if rounds is not None:
                adjust = rounds != SEG.NO_ROUNDS
                newEffect.setRounds(rounds, adjust)

            self.addStatusEffect(effectId, newEffect)

        # And starting visual effects
        for effectDict in self.startingVisualEffects:
            effectEnum = effectDict['effectEnum']
            extraArgs = effectDict['extraArgs']
            self.addVisualEffect(effectEnum, extraArgs=extraArgs)
        
        self.startingStatusEffects = []
        self.startingVisualEffects = []

        # Ensure they get their skelecog/virtual cog effects as well
        skelecogEffect = None
        if self.virtual:
            skelecogEffect, _ = self.addStatusEffect(SEE.EFFECT_VIRTUAL_COG)
        elif self.isSkelecog and self.dna.name not in SuitBattleGlobals.SkelecogEffectBlocklist:
            skelecogEffect, _ = self.addStatusEffect(SEE.EFFECT_SKELECOG)
        if skelecogEffect:
            skelecogEffect.setChosenPercent(self.healthPercentChosen)

        # If they're a skelecog, make sure they get that visual effect.
        if self.getSkelecog():
            self.addVisualEffect(VisualEffectEnum.SKELECOG)

        self.sendStatusEffects()

    def requestRemoval(self):
        """
        Suggest that this suit is done with its duties and should be removed.
        """
        if self.sp is not None and not self.forceRemove:
            # If we have a SuitPlanner, it should do the removing.
            self.sp.removeSuit(self)
        else:
            # Otherwise, remove ourselves.
            self.requestDelete()
        return

    def calculateHp(self):
        attributes = SuitBattleGlobals.SuitAttributes[self.dna.name]
        hp = SuitBattleGlobals.calculateHp(attributes, self.level,
                                           hpMultIndex=self.hpMultIndex, dnaName=self.dna.name)

        forced = False
        # Check if the HP is forced to anything. If it is, do not multiply the HP by 1.5.
        if SuitDefinitions[self.dna.name].forceHp:
            forced = True

        ### apply elite status ###
        if self.isElite:
            if not forced:
                hp = int(hp * 1.5)
            if not self.calculatedHpAlready:
                self.setDamageMultiplier(self.getDamageMultiplier() * 1.2)
            self.calculatedHpAlready = True

        if self.healthPercentChosen is not None:
            hp = int(hp * self.healthPercentChosen)

        # Remap HP if necessary.
        hp = SuitBattleGlobals.HealthRemapping.get(hp, hp)

        return hp

    def setLevel(self, lvl = None, hpMultIndex = 0):
        """
        Randomly choose a level for this suit based on the type of the suit (such as yesman, flunky, etc)
        or set the level to be the one specified

        :param int lvl: level the suit should be
        """
        self.level = lvl
        self.notify.debug('Assigning level ' + str(lvl))
        if hasattr(self, 'doId'):
            self.d_setLevelDist(self.level, hpMultIndex = hpMultIndex)
        # be sure to set the hp to proper values based on the suit's new level
        self.hpMultIndex = hpMultIndex
        hp = self.calculateHp()
        self.maxHp = hp
        self.hp = hp

    def getLevelDist(self):
        """
        the distributed function to be called when the server side suit changes level

        :param int level: the new level of the suit
        """
        return self.getLevel(), 0  # todo - this should be its hpMultIndex if this function is used

    def d_setLevelDist(self, level, hpMultIndex = 0):
        """
        the distributed function to be called when the server side suit changes level

        :param int level: the new level of the suit
        """
        self.sendUpdate('setLevelDist', [level, hpMultIndex])

    def b_setElite(self, flag):
        self.setElite(flag)
        self.d_setElite(flag)

    def d_setElite(self, flag):
        self.sendUpdate('setElite', [flag])

    def setElite(self, flag):
        self.isElite = flag
        if flag:
            hp = self.calculateHp()
            if self.isGenerated():
                self.b_setMaxHp(hp)
            else:
                self.maxHp = hp
                self.hp = hp

    def getElite(self):
        return self.isElite
    
    def b_setPersistent(self, flag: bool) -> None:
        self.d_setPersistent(flag)
        self.setPersistent(flag)
    
    def d_setPersistent(self, flag: bool) -> None:
        self.sendUpdate("setPersistent", [flag])
    
    def setPersistent(self, flag: bool) -> None:
        self.persistent = flag
    
    def getPersistent(self) -> bool:
        return self.persistent

    def setupSuitDNA(self, level, type, track, respectsInvasion = False, wantAlts = False):
        """
        :param int level: indicated level (1..9)
        :param int type: (1..8)
        :param str track: ("g", "c", "l", "m", "s")
        """
        dna = SuitDNA.SuitDNA()
        if respectsInvasion:
            if simbase.air.suitInvasionManager.getInvading():
                invading = simbase.air.suitInvasionManager.getInvadingCog()[1]
            else:
                invading = ''
        else:
            invading = ''
        dna.newSuitRandom(type, track, invading, wantAlts = wantAlts)
        self.dna = dna
        self.track = track
        self.setLevel(level)

    def setupCustomSuitDNA(self, name, track, level):
        dna = SuitDNA.SuitDNA()
        dna.newSuit(name)
        self.dna = dna
        self.track = track
        if name in SuitBattleGlobals.ALWAYS_SKELECOGS:
            self.setSkelecog(1)
        if name not in CogPageGlobals.cogNamesForRadar:
            level = SuitBattleGlobals.SuitAttributes[name]['level'] + 1
        self.setLevel(level)
        if name in SuitBattleGlobals.COG_MINIBOSSES or name in SuitBattleGlobals.ALWAYS_EXECUTIVES and not self.isElite:
            self.setElite(1)

    def addStartingStatusEffect(self, effectId, rounds=None, extraArgs: list=None):
        self.startingStatusEffects.append({'effectId': effectId, 'rounds': rounds, 'extraArgs': extraArgs})

    def addStartingVisualEffect(self, effectEnum, extraArgs = None):
        if extraArgs is None:
            extraArgs = []
        self.startingVisualEffects.append(
            {
                'effectEnum': effectEnum,
                'extraArgs': extraArgs
            }
        )

    def removeStartingStatusEffect(self, effectId):
        for effect in self.startingStatusEffects:
            if effect['effectId'] == effectId:
                self.startingStatusEffects.remove(effect)
                break

    def removeStartingVisualEffect(self, effectEnum):
        for effect in self.startingVisualEffects:
            if effect['effectEnum'] == effectEnum:
                self.startingVisualEffects.remove(effect)
                break

    def getDNAString(self):
        """
        Retrieve the dna information from this suit, called whenever a client needs to create this suit

        :return: netString representation of this suit's dna
        """
        if self.dna:
            return self.dna.makeNetString()
        else:
            self.notify.debug('No dna has been created for suit %d!' % self.getDoId())
            return ''

    def b_setBrushOff(self, index):
        """
        Sets the brush off on this instance with the set index b_ means astron
        :return: No
        """
        # Local
        self.setBrushOff(index)
        # Distributed
        self.d_setBrushOff(index)

    def d_setBrushOff(self, index):
        self.sendUpdate('setBrushOff', [index])

    def setBrushOff(self, index):
        # I guess on the AI side there is nothing to do here
        pass

    def d_denyBattle(self, toonId):
        self.sendUpdateToAvatarId(toonId, 'denyBattle', [])

    def b_setSkeleRevives(self, num):
        if num is None:
            num = 0
        self.setSkeleRevives(num)
        self.d_setSkeleRevives(self.getSkeleRevives())

    def d_setSkeleRevives(self, num):
        self.sendUpdate('setSkeleRevives', [num])

    def getSkeleRevives(self):
        return self.skeleRevives

    def setSkeleRevives(self, num):
        if num is None:
            num = 0
        self.skeleRevives = num

    def b_setMaxSkeleRevives(self, num):
        if num is None:
            num = 0
        self.setMaxSkeleRevives(num)
        self.d_setMaxSkeleRevives(num)

    def d_setMaxSkeleRevives(self, num):
        self.sendUpdate('setMaxSkeleRevives', [num])

    def getMaxSkeleRevives(self):
        return self.maxSkeleRevives

    def setMaxSkeleRevives(self, num):
        if num is None:
            num = 0
        self.maxSkeleRevives = num

    def useSkeleRevive(self):
        self.skeleRevives -= 1
        self.maxSkeleRevives += 1
        self.reviveFlag = 1
        revAttr = SuitBattleGlobals.REVIVE_ATTRIBUTES
        hpMult = revAttr.get(self.dna.name, revAttr['standard'])[0]
        self.setMaxHp(int(self.maxHp * hpMult))
        self.b_setSkelecog(2, revived=True)
        self.b_setMaxSkeleRevives(self.maxSkeleRevives)

    def reviveCheckAndClear(self):
        returnValue = 0
        if self.reviveFlag == 1:
            returnValue = 1
            self.reviveFlag = 0
        return returnValue

    def d_setAfterReviveDamage(self, afterReviveDamage):
        self.sendUpdate('setAfterReviveDamage', [afterReviveDamage])

    def setStashed(self, mode):
        self.sendUpdate('setStashed', [mode])

    # allowOverheal flag will let the suit be healed past their maxHp cap
    def healSuit(self, amount, allowOverheal=False):

        if amount <= 0:
            return

        if not allowOverheal and self.hp + amount >= self.getMaxHp():
            self.hp = self.getMaxHp()
        else:
            self.hp += amount
        if self.hp > self.getMaxHp():
            self.overhealed = 1
        else:
            self.overhealed = 0

    def getHp(self):
        return self.hp

    def setHp(self, hp):
        """
        Sets the current health of this suit; this can be called during battle and at initialization

        :param int hp: value to set health to
        """
        if hp > self.getMaxHp() and not self.overhealed:
            self.hp = self.getMaxHp()
        else:
            self.hp = hp
        if self.hp < self.getMaxHp():
            self.overhealed = 0

    def b_setHp(self, hp):
        self.setHp(hp)
        self.d_setHp(hp)

    def d_setHp(self, hp):
        self.sendUpdate('setHp', [hp])

    def setMaxHp(self, hp):
        self.maxHp = hp
        self.hp = hp

    def d_setMaxHp(self, hp):
        self.sendUpdate('setMaxHp', [hp])

    def b_setMaxHp(self, hp):
        self.d_setMaxHp(hp)
        self.setMaxHp(hp)

    def getMaxHp(self):
        return self.maxHp
    
    def toonUp(self, num):
        return  # NO

    def setDamageMultiplier(self, mult):
        self.dmgMult = mult

    def getDamageMultiplier(self):
        return self.dmgMult

    def releaseControl(self):
        # Do whatever needs to be done to turn control of the suit over to
        # another party (e.g. a battle) - should be redefined by child if
        # any behavior is required
        pass

    def getDeathEvent(self):
        return 'cogDead-%s' % self.doId

    def resume(self):
        self.notify.debug('resume, hp=%s' % self.hp)
        # Do whatever needs to be done to restore control of the suit from
        # another party (e.g. a battle) - should be redefined by child if
        # any additional behavior is required
        if self.hp <= 0:
            messenger.send(self.getDeathEvent())
            # Clean up dead suits
            self.requestRemoval()

    def prepareToJoinBattle(self):
        """
        do whatever is appropriate when the suit is about to join
        a battle; most likely, stop doing anything and let the battle
        puppeteer
        """
        pass

    def b_setSkelecog(self, flag, revived=False):
        """
        by setting our personal flag differently than the flag
        that gets sent to the client, we can have it so that
        the server properly updates the suit to be a skelecog, but
        the client delays the skelecog transformation for whatever reason.
        (e.g. a revive movie)
        """
        if flag == 2:
            self.setSkelecog(1, revived=revived)
            self.d_setSkelecog(0)
        else:
            self.setSkelecog(flag, revived=revived)
            self.d_setSkelecog(flag)

    def setSkelecog(self, flag, revived=False):
        SuitBase.SuitBase.setSkelecog(self, flag)
        if flag and not revived:
            self.updateHpPercentChosen(SuitBattleGlobals.SkelecogHpRange[0], SuitBattleGlobals.SkelecogHpRange[1])

    def d_setSkelecog(self, flag):
        self.sendUpdate('setSkelecog', [flag])

    # Is this the factory foreman?
    def isForeman(self):
        return 0

    # Is this a mint floor supervisor?
    def isSupervisor(self):
        return 0

    def setVirtual(self, virtual):
        self.virtual = virtual
        if virtual:
            self.updateHpPercentChosen(SuitBattleGlobals.VirtualHpRange[0], SuitBattleGlobals.VirtualHpRange[1])

    def getVirtual(self):
        return self.virtual

    def isVirtual(self):
        return self.getVirtual()

    def updateHpPercentChosen(self, minRange, maxRange):
        self.healthPercentChosen = 1.00
        # Minibosses disregard the HP percentage
        if self.isMiniboss():
            return

        # Ensure a reroll if the value is equal to 100%
        while round(self.healthPercentChosen, 2) == 1.00:
            self.healthPercentChosen = lerp(minRange, maxRange, random.random())

        newHp = self.calculateHp()
        if self.isGenerated():
            self.b_setMaxHp(newHp)
        else:
            self.maxHp = newHp
            self.hp = newHp

    def isMiniboss(self):
        return self.dna.name in SuitBattleGlobals.COG_MINIBOSSES

    def setWaiter(self, flag):
        SuitBase.SuitBase.setWaiter(self, flag)

    def d_setWaiter(self, flag):
        self.sendUpdate('setWaiter', [flag])

    def b_setWaiter(self, flag):
        self.setWaiter(flag)
        self.d_setWaiter(flag)

    def getWaiter(self):
        return self.waiter
    
    def getRandomAttack(self) -> AttackEnum:
        attacks: dict = SuitBattleGlobals.SuitAttributes[self.dna.name]["attacks"]
        attackFrequencies = [attack[2][min(self.getLevel(), len(attack[2]) - 1)] for attack in list(attacks.values())]
        return random.choices(list(attacks), weights=attackFrequencies)[0]

    def isStubborn(self):
        """
        Returns True if the suit is Stubborn.
        A suit that is Stubborn will be very unlikely to leave a street zone
        through traditional means, whether that is an invasion summoning/retreating,
        entering a cog building, or by walking into another battle.
        """
        return self.dna.name in SuitBattleGlobals.STUBBORN_COGS
