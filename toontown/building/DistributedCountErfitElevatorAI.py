from toontown.building.ElevatorConstants import *
from toontown.building import DistributedElevatorExtAI
from toontown.toonbase import ToontownGlobals

class DistributedCountErfitElevatorAI(DistributedElevatorExtAI.DistributedElevatorExtAI):

    def __init__(self, air, zone, antiShuffle=0, minLaff=0):
        DistributedElevatorExtAI.DistributedElevatorExtAI.__init__(
            self,
            air,
            self,
            numSeats=4,
            antiShuffle=antiShuffle,
            minLaff=minLaff
        )

        self.zone = zone
        self.bldgDoId = 0

    def getDoId(self):
        return 0
    
    def _createInterior(self):
        from toontown.suit import DistributedCountErclaimBossAI

        boss = DistributedCountErclaimBossAI.DistributedCountErclaimBossAI(self.air)
        boss.generateWithRequired(ToontownGlobals.SellbotLobby)

        print 'COUNT ERFIT: boss generated', boss.doId

        for avId in self.seats:
            print 'COUNT ERFIT: checking seat', avId

            if avId:
                toon = self.air.doId2do.get(avId)
                print 'COUNT ERFIT: toon is', toon

                if toon:
                    toon.b_setLocation(boss.doId, ToontownGlobals.SellbotLobby)
                    print 'COUNT ERFIT: toon sent'

    def createCountErfitBoss(self):
        from toontown.suit import DistributedCountErclaimBossAI

        boss = DistributedCountErclaimBossAI.DistributedCountErclaimBossAI(self.air)
        boss.generateWithRequired(ToontownGlobals.SellbotLobby)

        for avId in self.seats:
            if avId:
                toon = self.air.doId2do.get(avId)
                if toon:
                    toon.b_setLocation(boss.doId, ToontownGlobals.SellbotLobby)

    def sendToBossBattle(self):
        avIds = []

        for avId in self.seats:
            if avId:
                avIds.append(avId)

        for avId in avIds:
            toon = self.air.doId2do.get(avId)
            if toon:
                toon.b_setLocation(ToontownGlobals.CountErfitBattle, ToontownGlobals.CountErfitBattle)