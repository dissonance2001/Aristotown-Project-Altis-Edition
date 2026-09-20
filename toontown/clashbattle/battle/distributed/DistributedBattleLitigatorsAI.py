from toontown.clashsuit.suit import BossCogGlobals
from toontown.clashbattle.battle.BattleGlobals import BattleOrderPriority
from toontown.clashbattle.battle.distributed.DistributedBattleFinalAI import DistributedBattleFinalAI
from toontown.toonbase import ToontownGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedBattleLitigatorsAI(DistributedBattleFinalAI):

    def enterResume(self):
        # We need to do 2 things here, if we have minibosses remaining:
        # If another battle exists, we place ourselves into reserve suits so that they can join the other battle.
        # If no other battle exists, then let the boss know to create a new battle and force the other members into it.
        boss = self.air.doId2do.get(self.bossCogId)
        if boss and not boss.surrendered:
            # Keep track of the current HP of each of the miniboss suits
            litigationMemberInfo = {suit.dna.name: suit.getHp() for suit in self.suits if suit.dna.name in boss.litigationOrder}

            # We don't have anything to do here if we don't have any minibosses.
            if len(litigationMemberInfo) > 0:
                # For each litigation member, generate a new boss suit with the given HP.
                # Then, add it to the bosses reserve suits.
                battlePriority = [
                    suit.getBattleOrderPriority() for suit in self.activeSuits 
                    if suit.getHp() and suit.dna.name in boss.litigationOrder
                ]
                for litMember in list(litigationMemberInfo.keys()):
                    suit = boss.genBossSuit(litMember, 
                        BattleOrderPriority.END 
                        if BattleOrderPriority.BEGINNING in battlePriority else 
                        BattleOrderPriority.BEGINNING
                    )
                    suit.b_setHp(litigationMemberInfo[litMember])
                    boss.reserveSuits.append((suit, 0))
                    battleSide = 1 if self is boss.battleB else 0
                    boss.d_updateLitigationMemberPosition(litMember, battleSide)

                # First scenario: There is another battle, we are going to place these into reserves.
                if (self is boss.battleA and boss.battleB) or (self is boss.battleB and boss.battleA):
                    # Just pass, the boss will naturally handle everything we need with reserves already placed.
                    pass
                # Second scenario: No other battle exists, lets drag everybody into a new battle.
                else:
                    battleNum = 2
                    # Create a new battleA if we are battleB, or battleB if we are battleA.
                    # Once created, force all of the toons not in a battle into it.
                    if self is boss.battleA:
                        bossPos = BossCogGlobals.LawbotBossBattleBackFromTablePosHpr
                        battlePos = BossCogGlobals.LawyerBattleBPosHpr
                        roundDone = boss.handleBossRoundBDone
                        battleDone = boss.handleBattleBDone
                        battleSide = 1
                        battle = boss.battleB = boss.makeBattle(bossPos, battlePos, roundDone, battleDone, battleNum, battleSide)
                        boss.battleBId = boss.battleB.doId
                    else:
                        bossPos = BossCogGlobals.LawbotBossBattleBackFromTablePosHpr
                        battlePos = BossCogGlobals.LawyerBattleAPosHpr
                        roundDone = boss.handleBossRoundADone
                        battleDone = boss.handleBattleADone
                        battleSide = 0
                        battle = boss.battleA = boss.makeBattle(bossPos, battlePos, roundDone, battleDone, battleNum, battleSide)
                        boss.battleAId = boss.battleA.doId

                    boss.sendBattleIds()
                    # Grab our minibosses from reserve suits, place them into active suits
                    newSuits = [suitInfo[0] for suitInfo in boss.reserveSuits]
                    boss.reserveSuits = []
                    # Grab all toons that are:
                    # in the boss, and
                    # don't have a battle id, and
                    # not in our current battles toons, and
                    # are not sad.
                    involvedToons = []
                    for toonId in boss.involvedToons:
                        toon = self.air.doId2do.get(toonId)
                        if toon and not toon.battleId and toonId not in self.toons and toon.getHp() > 0:
                            involvedToons.append(toonId)

                    # Make sure we actually have some toons left.
                    if len(involvedToons) > 0:
                        # Start the new battle!
                        battle.startBattle(involvedToons, newSuits)
                    else:
                        # There's nobody left, get rid of the battles.
                        boss.resetBattles()
                        for suit in newSuits:
                            suit.requestDelete()

        super().enterResume()
