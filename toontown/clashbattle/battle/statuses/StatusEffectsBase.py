class _LazyStatusEffectGlobals:
    """Stands in for the StatusEffectGlobals module (imported as SEG in the other status files).
    It resolves on first use, so this module never imports StatusEffectGlobals while loading
    and the circular import stays broken."""
    def __getattr__(self, name):
        from toontown.clashbattle.battle.statuses import StatusEffectGlobals
        return getattr(StatusEffectGlobals, name)

SEG = _LazyStatusEffectGlobals()

class StatusEffectBase:
    VisualSortOrder = 0  # Determines the sort order of this effect on battle panels.

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        self.avProfile = avProfile
        self.effectId = effectId
        # We increment this by 1 because of the rules of how status effects work.
        # The rounds you define is how many rounds you want it to last after the round it is created.
        # The round that it is created should not take away from its round counter.
        if rounds != SEG.NO_ROUNDS:
            rounds = rounds + 1
        self.rounds = rounds
        self.disabledRounds = disabledRounds
        self.extraArgs = extraArgs
        self.combines = True
        # Fill in names of variables that apply to extraArgs in subclasses.
        self.fields = []
        # Do we want to send this to the client?
        self.wantShow = True
        # What visual effect enums is this status effect associated with?
        self.visualEffectEnums = []
        # Which event definitions do we wanna inherit into this status effect? (Useful for subclasses)
        # Example: The base status effect definition is a decrement of 1 round on the end round event send.
        self.inheritedEventDefinitions = []
        self.lureAbilityQueue = []
        self.wasDisabledThisRound = False

        self.cleanedUp = False

    def increment(self, amount):
        self.rounds += amount

    def checkDisabledDecrement(self):
        if self.disabledRounds > 0:
            if self.wasDisabledThisRound:
                self.wasDisabledThisRound = False
            else:
                self.disabledRounds -= 1

    def decrement(self, amount):
        isDisabled = self.isDisabled()
        self.checkDisabledDecrement()
        if isDisabled:
            return

        # Don't decrement NO_ROUNDS status effects (-1 rounds)
        if self.rounds == SEG.NO_ROUNDS:
            return
        self.rounds -= amount
        # 0 rounds remaining is when the effect dies.
        if self.rounds <= 0:
            self.roundsRanOut()
            return

    def combine(self, otherEffect):
        # Default combine behavior; override if needed
        otherRounds = otherEffect.getRounds()
        # If the other effect's rounds is -1 (permanent), override entirely.
        # If it's not infinite rounds, then just increment the rounds by the given amount.
        if otherRounds != SEG.NO_ROUNDS:
            self.increment(otherRounds)
        else:
            self.setRounds(SEG.NO_ROUNDS, adjust=False)

    def wantCombine(self, otherEffect):
        return self.combines

    def getEffectId(self):
        return self.effectId

    def getRounds(self):
        return self.rounds

    def setRounds(self, rounds, adjust=True):
        # adjust flag adjusts round sets to account for the +1 needed on initial rounds set.
        # See __init__ for more details.
        extra = 1 if adjust else 0
        self.rounds = rounds + extra

    def getExtraArgs(self):
        return self.extraArgs

    def setExtraArgs(self, extraArgs):
        self.extraArgs = extraArgs

    def getAv(self):
        # Returns the actual avatar that this status effect belongs to
        if self.cleanedUp:
            return None
        return self.avProfile

    @property
    def av(self):
        return self.getAv()

    def getTranslatedExtraArgs(self):
        # Call this when sending status effect info over to the client.
        extraArgs = []
        # Populate extraArgs with new info for each of these fields for the client.
        for field in self.fields:
            extraArgs.append(getattr(self, field))
        return extraArgs

    def getInfo(self):
        return [self.getEffectId(), self.getRounds(), self.getTranslatedExtraArgs()]

    def isAi(self):
        # Sees if the AI is running this effect
        return self.avProfile.battleListener

    def getBattleCalc(self):
        # AI Only
        return self.avProfile.battleListener.battleCalc

    @property
    def battleCalc(self):
        return self.getBattleCalc()

    def getBattle(self):
        # AI Only
        return self.avProfile.battle

    @property
    def battle(self):
        return self.getBattle()

    @property
    def activeToons(self):
        return [self.battle.getToon(toonId) for toonId in self.battle.activeToons]

    def roundsRanOut(self):
        # Define things that need to happen on natural status effect deletion but not in forced ways.
        self.delete()

    def cleanup(self):
        if self.cleanedUp:
            return

        self.cleanedUp = True

        del self.avProfile
        del self.lureAbilityQueue
        del self.inheritedEventDefinitions
        del self.visualEffectEnums

    def delete(self):
        # Override if needed in subclasses.
        # Make sure the effect hasn't been cleaned up.
        # This is to prevent crashes from outside sources trying to delete this after it's already been deleted.
        if self.cleanedUp:
            return
        self.avProfile.deleteStatusEffect(self)
        self.cleanup()

    def createLureResistanceStatusEffect(self, rounds=2):
        lureEffect = SEG.createStatusEffect(self.getAv(), SEE.EFFECT_LURE_RESISTANCE)
        lureEffect.setAmount(rounds)
        self.getAv().addStatusEffect(SEE.EFFECT_LURE_RESISTANCE, lureEffect)

    @property
    def lureResistanceEffect(self):
        return self.getAv().getStatusEffectOfId(SEE.EFFECT_LURE_RESISTANCE)

    def isVisible(self):
        """
        Client-only.
        Can be overridden for making unique cases for when
        a status effect is supposed to be shown to the Client.
        """
        return True

    def createAttack(self, attackType, insertMethod=None, extraArgs=None,
                     passedArgs=None, attemptQueue=True, unlure=False,
                     damageMult=1.0, insertArgs=None, targets: list=None,
                     priority: int=0, tauntIndex: int=0):
        """
        Instantly creates and inserts a suit attack with the given arguments

        :param attackType: The enum of suit attack that this attack should be
        :param insertMethod: The method/placement of insertion. Index, beginning, or end.
        :param extraArgs: The extra arguments that should be passed into the attack class
        :param passedArgs: If lure queue is being used, passedArgs are used to feed back into the creation function for that attack.
        :param attemptQueue: If an ability should attempt to use the lure queue or not
        :param unlure: If this attack should unlure the cog that is going to be using it
        :param damageMult: The multiplier of damage for the attack
        :param targets: If given, the specific targets that this suit attack should be forced to hit
        :param insertArgs: If insertMethod is index, these define the index and the adjustment.
        :param priority: The priority of the move.
        :return:
        """
        # Only avatars who are actually in battle can attack.
        if self.getAv().getBattleState() != BattleGlobals.BattleStateEnum.ACTIVE:
            return

        extraArgs = extraArgs or []
        passedArgs = passedArgs or []
        insertArgs = insertArgs or {}
        targets = targets or []

        # If the suit is lured, add this attack to the queue of attacks to do after they unlure.
        if self.getAv().getStatusEffectOfType(LureStatusEffect) and not unlure:
            if attemptQueue:
                self.addAttackToLureQueue(attackType, passedArgs)
        else:
            from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import createAttack
            attack = createAttack(
                attackType, invoker=self.getAv(), unlure=unlure,
                damageMult=damageMult, targets=targets, extraArgs=extraArgs,
                tauntIndex=tauntIndex
            )

            if insertMethod:
                if insertMethod == 'index':
                    insertIndex = insertArgs.get('insertIndex')
                    adjust = insertArgs.get('adjust', True)
                    respectPreviousAdditions = insertArgs.get('respectPreviousAdditions', True)
                    self.getBattleCalc().insertAttack(
                        attack, "insert", insertIndex, adjust=adjust, priority=priority,
                        respectPreviousAdditions=respectPreviousAdditions)
                    return
                elif insertMethod == 'beginning':
                    self.getBattleCalc().insertAttack(attack, "beginning", priority=priority)
                    return
                elif insertMethod == 'replace':
                    self.getBattleCalc().insertAttack(attack, "replace", priority=priority)
                    return

            self.getBattleCalc().insertAttack(attack, "end", priority=priority)

    def createGeneralAttack(self, attackType, extraArgs=None, targetList=None, insertKwargs: dict=None):
        extraArgs = extraArgs or []
        targetList = targetList or [self.getAv()]
        self.getBattleCalc().createAndInsertAttack(
            attackType,
            {"targets": targetList, "extraArgs": extraArgs},
            insertKwargs,
        )

    def addAttackToLureQueue(self, attackId, passedArgs):
        self.lureAbilityQueue.append([attackId, passedArgs])
        self.createGeneralAttack(AttackEnum.SHOW_HP_TEXT, extraArgs=[TTLocalizer.HP_TEXT_ABILITY_QUEUE])

    def checkLureQueue(self):
        if self.getAv().getStatusEffectOfType(LureStatusEffect):
            return
        for attackList in self.lureAbilityQueue[:]:
            attackId, attackArgs = attackList
            createFunc = self.attackId2Type.get(attackId, self.createAttack)
            createFunc(*attackArgs)

            if attackList in self.lureAbilityQueue:
                self.lureAbilityQueue.remove(attackList)

    def addStatusEffectToAllSuits(self, effectID, suits=None):
        suits = suits or self.getBattleCalc().suits
        for suit in suits:
            suit.addStatusEffect(effectID)

    def getVisualSortOrder(self):
        return self.VisualSortOrder

    ### Handler for certain disabled status effects

    def setDisabledRounds(self, rounds, doThisRound: bool = False) -> None:
        self.disabledRounds = rounds
        if not doThisRound:
            self.wasDisabledThisRound = True

    def getDisabledRounds(self) -> int:
        return self.disabledRounds

    def isDisabled(self):
        return self.disabledRounds and not self.wasDisabledThisRound


# Flag class that will cause the avatar to ignore visual effect unapply movies while this is active
class IgnoreVisualEffectMovieUnapplyEffect:
    pass
