from toontown.battle import DistributedBattleMinibossAI


class DistributedBattlePlutocratAI(DistributedBattleMinibossAI.DistributedBattleMinibossAI):
    def __init__(self, air, bossCog, roundCallback, finishCallback, battleSide):
        DistributedBattleMinibossAI.DistributedBattleMinibossAI.__init__(
            self, air, bossCog, roundCallback, finishCallback, battleSide)
        self.bossCog = bossCog
        self.suitsDiedThisTurn = []

    def suitDied(self, suit):
        try:
            if suit.dna.name in ('charon', 'nix', 'hydra', 'styx', 'kerberos'):
                self.suitsDiedThisTurn.append(suit.dna.name)
        except:
            pass
        try:
            return DistributedBattleMinibossAI.DistributedBattleMinibossAI.suitDied(self, suit)
        except:
            return None
