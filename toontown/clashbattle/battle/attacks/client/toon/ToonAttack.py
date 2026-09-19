from toontown.battle.BattleGlobals import attackAffectsGroup
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.battle.attacks.client.Attack import Attack
from toontown.toon.DistributedToon import DistributedToon


class ToonAttack(Attack):
    
    def setTargets(self) -> bool:
        targetGone = 0
        track = self.attackType

        adict = {}
        self.atkDict = adict

        level = self.level
        adict["avatar"] = self.invoker
        adict["track"] = track
        adict["level"] = level
        adict["extraArgs"] = self.extraArgs

        adict["toons"] = self.toons
        adict["suits"] = self.suits

        if track == AttackEnum.TOON_NPC:
            targets = []
            for target in self.targetObjs:
                tdict = {}
                result = self.findTarget(target.doId)
                tdict["avatar"] = target
                tdict["hp"] = result.hpAdjust
                targets.append(tdict)

            if len(targets) > 0:
                adict["target"] = targets
        elif track == AttackEnum.TOON_HEAL:
            targets = []
            for target in self.targetObjs:
                result = self.findTarget(target.doId)
                targets.append({"avatar": target, "hp": result.hpAdjust})

            if targets:
                adict["target"] = targets
            else:
                targetGone = 1
        elif attackAffectsGroup(track, level):
            targets = []
            for target in self.targetObjs:
                result = self.findTarget(target.doId)
                targets.append({
                    "suit": target,
                    "hp": result.hpAdjust,
                    "kbbonus": result.kbBonus,
                    "died": result.died,
                    "revived": result.revived,
                    "hpbonus": result.hpBonus,
                    "leftSuits": [],
                    "rightSuits": [],
                    "extraArgs": result.extraArgs,
                    "landed": result.landed,
                })

            adict["target"] = targets
        elif self.target < 0:
            targetGone = 1
        else:
            targets = []
            for target in self.targetObjs:
                # For "general" attacks (ie throw self heal where a toon target gets added)
                if isinstance(target, DistributedToon):
                    continue
                    
                lenSuits = len(self.battle.activeSuits)
                suitIndex = self.battle.activeSuits.index(target)
                
                leftSuits = []
                for si in range(0, suitIndex):
                    asuit = self.battle.activeSuits[si]
                    if not asuit.isLured:
                        leftSuits.append(asuit)

                rightSuits = []
                if lenSuits > suitIndex + 1:
                    for si in range(suitIndex + 1, lenSuits):
                        asuit = self.battle.activeSuits[si]
                        if not asuit.isLured:
                            rightSuits.append(asuit)
                
                result = self.findTarget(target.doId)
                targets.append({
                    "suit": target,
                    "hp": result.hpAdjust,
                    "hpbonus": result.hpBonus,
                    "kbbonus": result.kbBonus,
                    "died": result.died,
                    "revived": result.revived,
                    "leftSuits": leftSuits,
                    "rightSuits": rightSuits,
                    "extraArgs": result.extraArgs,
                    "landed": result.landed,
                })

            if track in (AttackEnum.TOON_DROP, AttackEnum.TOON_TRAP, AttackEnum.TOON_ZAP, AttackEnum.TOON_SQUIRT):
                adict["target"] = targets
            else:
                adict["target"] = targets[0]

        adict["sidestep"] = not self.landed
        adict["battle"] = self.battle
        adict["playByPlayText"] = self.playByPlayText

        return targetGone
