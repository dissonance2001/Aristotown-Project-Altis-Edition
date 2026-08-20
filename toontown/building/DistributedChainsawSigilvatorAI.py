from __future__ import absolute_import
from toontown.building.DistributedSigilvatorAI import DistributedSigilvatorAI
from toontown.instances import InstanceGlobals


class DistributedChainsawSigilvatorAI(DistributedSigilvatorAI):
    def _getPreferredSeat(self, avId):
        party = getattr(self, 'boardingParty', None)
        if not party:
            return None
        try:
            leaderId = party.getGroupLeader(avId)
            if leaderId is None:
                return None
            members = party.getGroupMemberList(leaderId)
        except:
            return None
        if not members:
            return None
        ordered = [leaderId]
        for memberId in members:
            if memberId != leaderId and memberId not in ordered:
                ordered.append(memberId)
        try:
            seatIndex = ordered.index(avId)
        except ValueError:
            return None
        if seatIndex < 0 or seatIndex >= len(self.seats):
            return None
        return seatIndex

    def acceptingBoardersHandler(self, avId, reason=0, wantBoardingShow=0):
        seatIndex = self._getPreferredSeat(avId)
        if seatIndex is not None and self.seats[seatIndex] is None:
            self.acceptBoarder(avId, seatIndex, wantBoardingShow)
            return
        DistributedSigilvatorAI.acceptingBoardersHandler(
            self, avId, reason, wantBoardingShow)

    def getInstanceId(self):
        return InstanceGlobals.CHAINSAW

    @property
    def closeTime(self):
        return 4.0
