import random

from direct.distributed.DistributedObjectAI import DistributedObjectAI

from toontown.clashbattle.battle import BattleGlobals
from toontown.clashbattle.battle.BattleGlobals import BattleStateEnum
from toontown.clashbattle.battle.BattleListenerObject import BattleListenerObject
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.server.toon import ToonAttackAI
from toontown.clashbattle.battle.statuses import StatusEffectGlobals as SEG
from toontown.clashbattle.battle.statuses.StatusEffectEnums import StatusEffectEnum as SEE
from toontown.inventory.enums.ItemEnums import MaterialItemType, UniteItemType
from toontown.inventory.registry import UniteRegistry, IOURegistry
from toontown.toon.gui.ToonTipGlobals import TTE

from typing import Dict, List, Any

from toontown.instances import HighRollerGlobals


class DistributedDiceChoiceAI(DistributedObjectAI, BattleListenerObject):

    def __init__(self, air, battle, battleListener):
        super().__init__(air)
        self.battle = battle
        self.battleListener = battleListener

        # State for toon data.
        self.pipsOwned: Dict[int, int] = {}
        self.pipChoices: Dict[int, List[int]] = {}
        self.rerollCount: Dict[int, int] = {}

        # Pip Actions
        self.pipActions = {
            0: self.doPipOne,
            1: self.doPipTwo,
            2: self.doPipThree,
            3: self.doPipFour,
            4: self.doPipFive,
            5: self.doPipSix,
            6: self.doGoldenPipSix,
        }

    def delete(self):
        super().delete()
        del self.battle
        del self.battleListener

    """
    Getters
    """

    def getBattle(self):
        return self.battle

    def getBattleListener(self):
        return self.battleListener

    def areDiceEnabled(self) -> bool:
        return self.getBattle().areDiceEnabled()

    def areDiceEnabledForAvId(self, avId: int) -> bool:
        av = self.air.doId2do.get(avId)
        if not av:
            return False

        if not av.getStatusEffectOfId(SEE.EFFECT_HR_TOON_GAGS_UNLOCKED):
            return True
        return self.areDiceEnabled()

    def getToons(self) -> list:
        toons = []
        for avId in self.getAvIds():
            toon = self.air.doId2do.get(avId)
            if toon:
                toons.append(toon)
        return toons

    def getAvIds(self) -> list:
        return self.getBattle().toons

    """
    Events
    """

    def enterBattleState(self, state: str):
        if state == 'WaitForInput':
            self.beginDice()
        else:
            self.endDice()

    def beginDice(self):
        """
        When the movie ends,
        figure out how many pips the Toons have,
        and give them their Pip choices.
        """
        self.pipsOwned = {}
        self.pipChoices = {}
        self.rerollCount = {}

        for avId in self.getAvIds():
            if not self.areDiceEnabledForAvId(avId):
                return

            # Cache pip fields.
            self.rerollPips(avId)

            av = self.air.doId2do.get(avId)
            if av:
                # Send them a toon tip about the dice picker here
                av.showToonTip(TTE.TIP_HIGH_ROLLER_DICE)

    def endDice(self):
        # Tell our avs to close their dice choices.
        for avId in self.getAvIds():
            self.sendUpdateToAvatarId(avId, 'closeChoices', [])

    """
    Astron Funnies
    """

    def rerollPips(self, avId: int) -> None:
        """
        Gives Pips to a given avId.
        """
        av = self.air.doId2do.get(avId)
        if not av:
            return
        if av.zoneId != self.zoneId:
            return

        # Set default fields.
        self.pipsOwned[avId] = 0
        self.pipChoices[avId] = []
        self.rerollCount.setdefault(avId, -1)
        self.rerollCount[avId] = self.rerollCount[avId] + 1

        # How many pips do they own?
        pipsqueak = av.getStatusEffectOfId(SEE.EFFECT_PIP_COUNTER)
        if pipsqueak:
            self.pipsOwned[avId] = pipsqueak.getPointCount()

        # Have they unlocked their gags yet from the initial dice?
        unlockedGags = av.getStatusEffectOfId(SEE.EFFECT_HR_TOON_GAGS_UNLOCKED)
        if unlockedGags:
            # Pick out some choices.
            tooMuchGambling = self.rerollCount[avId] >= HighRollerGlobals.MaxRerollCount
            readyToGamble = self.rerollCount[avId] >= HighRollerGlobals.RerollAddictionForceOneRequirement and not tooMuchGambling

            randomPips = list(range(1 if tooMuchGambling else 0, 6))  # If we've done too much gambling, we want to exclude 1.
            for effect in av.getStatusEffectsOfId(SEE.EFFECT_DICE_COOLDOWN):
                effectPip = effect.getPip()
                if effectPip in randomPips:
                    randomPips.remove(effectPip)
            random.shuffle(randomPips)
            randomPips = randomPips[:3]

            # If we are ready to gamble, force a 1.
            if readyToGamble and 0 not in randomPips:
                randomPips = randomPips[:2]
                randomPips.append(0)

            # Set pips now.
            randomPips = sorted(randomPips)
            self.pipChoices[avId] = randomPips

            # Send pip fields.
            pipsOwned = self.pipsOwned.get(avId, 0)
            pipChoices = self.pipChoices.get(avId, [])
        else:
            # They haven't unlocked their gags yet, we can ONLY give them the starter golden dice.
            pipsOwned = self.pipsOwned.get(avId, 0)
            self.pipChoices[avId] = [6]
            pipChoices = self.pipChoices[avId]

        self.sendUpdateToAvatarId(avId, 'sendPipFields', [pipChoices, max(0, pipsOwned)])

    def receivePipChoice(self, pip):
        """
        A Toon has requested to eat Pips for breakfast.
        """
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.getAvIds():
            return
        av = self.air.doId2do.get(avId)
        if not av:
            return

        # Validate them.
        pipsOwned = self.pipsOwned.get(avId, 0)
        pipChoices = self.pipChoices.get(avId, [])
        moveCost = HighRollerGlobals.getPipCost(av, AttackEnum.TOON_DICE, pip)

        if moveCost > pipsOwned:
            return
        if pip not in pipChoices:
            return
        if pip not in self.pipActions.keys():
            return

        battle = self.getBattle()
        if not battle:
            return
        if battle.ignoreResponses:
            return
        if battle.getCurrentOrNextState() != 'WaitForInput':
            return

        toon = None
        for t in self.getToons():
            if t.doId == avId:
                toon = t
                break
        else:
            return

        if toon.getBattleState() != BattleStateEnum.ACTIVE:
            return

        # Charge them.
        pipsqueak = toon.getStatusEffectOfId(SEE.EFFECT_PIP_COUNTER)
        if pipsqueak:
            pipsqueak.decrementPoints(moveCost)
        self.pipsOwned[avId] = pipsOwned - moveCost
        pipChoices.remove(pip)

        # Perform Pip action.
        action = self.pipActions.get(pip)
        actionResult = action(toon)
        if type(actionResult) not in (tuple, list):
            actionResult = [actionResult]

        # If the toon has an active attack in battle, we may need to remove it.
        battleCalc = battle.battleCalc
        attack: ToonAttackAI = battleCalc.toonAttacks.get(avId)
        if attack:
            if 0 <= attack.attackType < len(BattleGlobals.Tracks):
                if HighRollerGlobals.getPipCost(av, attack.track, attack.level) > self.pipsOwned[avId]:
                    # Force pull back.
                    battle.requestAttack(AttackEnum.TOON_UN_ATTACK, -1, -1, False, 0)

        # Influence battle.
        toon.sendStatusEffects()
        if len(actionResult) > 1:
            # If we had a second toon, update their effects too.
            # This is from the 5 pip dice.
            for toon in actionResult[1]:
                toon.sendStatusEffects()

        # Callback now.
        for battleAvId in self.getAvIds():
            self.sendUpdateToAvatarId(battleAvId, 'callbackPipChoice', [avId, pip, self.pipsOwned[avId], self.getPipPhrase(av, actionResult[0], pip)])

    """
    Pip Actions
    """

    def doPipOne(self, av) -> Any:
        """
        Reroll the dice for this avatar.
        """
        avId = av.doId
        self.rerollPips(avId)

        # Return the amount of times we have rerolled.
        return self.rerollCount.get(avId, 0)

    def doPipTwo(self, av) -> Any:
        """
        Give one-round perfect accuracy for the avatar.
        """
        effectId = SEE.EFFECT_TOONS_ACCURACY_UP
        existingEffect = av.getStatusEffectOfId(effectId)
        if existingEffect:
            existingEffect.setRounds(existingEffect.getRounds() + 1, adjust=False)
        else:
            newStatusEffect = SEG.createStatusEffect(av, effectId, extraArgs=[100, 100])
            newStatusEffect.setRounds(0)
            av.addStatusEffect(effectId, newStatusEffect)

    def doPipThree(self, av) -> Any:
        """
        Reduce Pip costs for the avatar by two.
        """
        effectId = SEE.EFFECT_PIP_DISCOUNT
        existingEffect = av.getStatusEffectOfId(effectId)
        if existingEffect:
            existingEffect.setRounds(existingEffect.getRounds() + 1, adjust=False)
        else:
            newStatusEffect = SEG.createStatusEffect(av, effectId, extraArgs=[2])
            newStatusEffect.setRounds(0)
            av.addStatusEffect(effectId, newStatusEffect)

    def doPipFour(self, av) -> Any:
        """
        Give a team-wide attack boost.
        """
        boost = HighRollerGlobals.PipGagBoost / 100
        for toon in self.getToons():
            effectId = SEE.EFFECT_TOON_MULT_DAMAGE_UP
            existingEffect = toon.getStatusEffectOfId(effectId)
            if existingEffect:
                existingEffect.setMultiplier(existingEffect.getMultiplier() + boost)
            else:
                newStatusEffect = SEG.createStatusEffect(toon, effectId, extraArgs=[1.0 + boost, 2])
                newStatusEffect.setRounds(0)
                toon.addStatusEffect(effectId, newStatusEffect)

        return None, [toon for toon in self.getToons() if toon is not av]

    def doPipFive(self, av) -> Any:
        """
        Gain a random IOU for two people in battle (including you!)
        """
        toons = self.getToons()
        if av not in toons:
            return '...?!?'

        # Figure out the toons to influence.
        toons.remove(av)
        random.shuffle(toons)
        toons = toons[:1]
        toons.append(av)

        # Get the name of the target toon.
        toonName = toons[0].getName()

        # Apply IOU buffs.
        effectId = SEE.EFFECT_TOON_DAMAGE_UP
        for toon in toons:
            others = toon.getStatusEffectsOfId(SEE.EFFECT_TOON_DAMAGE_UP)
            otherIous = {track: [effect.multiplier for effect in others if effect.gagTrack == track]
                         for track in BattleGlobals.ATTACK_TRACKS}
            iouCandidates = [iou for iou in IOURegistry.IOURegistry.values() if
                             iou.getBoost() not in otherIous.get(iou.getGagTrack(), [])
                             and iou.getGagTrack() in BattleGlobals.ATTACK_TRACKS]
            if iouCandidates:
                iou = random.choice(iouCandidates)
            else:  # If they somehow have all IOUs, then uhhh go away
                continue

            # Code copied from ToonNPCAttackAI
            newStatusEffect = SEG.createStatusEffect(toon, effectId)
            newStatusEffect.setGagTrack(iou.getGagTrack())
            newStatusEffect.setMultiplier(iou.getBoost())
            newStatusEffect.setUses(iou.getUses())
            toon.addStatusEffect(effectId, newStatusEffect)

        # Give a cooldown for this particular die
        diceCooldown = SEG.createStatusEffect(av, SEE.EFFECT_DICE_COOLDOWN)
        diceCooldown.setPip(4)
        diceCooldown.setRounds(1)
        av.addStatusEffect(SEE.EFFECT_DICE_COOLDOWN, diceCooldown)

        # Return name of partner.
        return toonName, [toons[0]]

    def doPipSix(self, av) -> Any:
        """
        Cast a 30% Toon-Up unite.
        """
        for toon in self.getToons():
            toon.doUniteEffect(UniteItemType.ToonUpMid)

        # Give a cooldown for this particular die
        diceCooldown = SEG.createStatusEffect(av, SEE.EFFECT_DICE_COOLDOWN)
        diceCooldown.setPip(5)
        diceCooldown.setRounds(2)
        av.addStatusEffect(SEE.EFFECT_DICE_COOLDOWN, diceCooldown)

    def doGoldenPipSix(self, av) -> Any:
        """
        Unlocks Gags for the Toons at the beginning of the fight.
        """
        av.addStatusEffect(SEE.EFFECT_HR_TOON_GAGS_UNLOCKED)

    def getPipPhrase(self, av, actionResult: Any, pip: int):
        phrase = HighRollerGlobals.DiceSpeedchatCast.get(pip)
        if type(phrase) in (tuple, list):
            phrase = random.choice(phrase)

        if pip == 0:
            # If pip 1, start screaming if we can't stop rerolling.
            if actionResult >= 5:
                phrase = random.choice(HighRollerGlobals.YouAreAFailureCast)

        if pip == 4:
            # If pip five, replace partner name with action result.
            phrase = phrase.format(partner=actionResult)

        return phrase
