from otp.ai.AIBase import *
from toontown.building.ElevatorConstants import *
from toontown.instances.InstanceGlobals import *
from toontown.building import DistributedElevatorAI
from toontown.building import DistributedElevatorExtAI
#from toontown.quest3.base.QuestHistory import QuestHistory
#from toontown.quest3.base.QuestReference import QuestId, QuestReference


class DistributedInstanceElevatorAI(DistributedElevatorExtAI.DistributedElevatorExtAI):
   # questRequired = None

    def __init__(self, air, bldg, zone, antiShuffle=0, minLaff=0):
        DistributedElevatorExtAI.DistributedElevatorExtAI.__init__(self, air, bldg, numSeats=4, antiShuffle=antiShuffle, minLaff=minLaff)
        self.zone = zone
        self.type = ELEVATOR_DERRICK_MAN
        self.bossType = DERRICK_MAN
        self.countdownTime = ElevatorData[self.type]['countdown']

    def delete(self):
        taskMgr.remove(self.uniqueName('closing-timer'))
        taskMgr.remove(self.uniqueName('opening-timer'))
        DistributedElevatorExtAI.DistributedElevatorExtAI.delete(self)

    def elevatorClosed(self):
        numPlayers = self.countFullSeats()
        if numPlayers > 0:
            bossZone = self.bldg.createBossOffice(self.seats, self.bossType)
            for seatIndex in xrange(len(self.seats)):
                avId = self.seats[seatIndex]
                if avId:
                    self.sendUpdateToAvatarId(avId, 'setBossOfficeZone', [bossZone])
                    self.clearFullNow(seatIndex)

        else:
            self.notify.warning('The elevator left, but was empty.')
        self.fsm.request('closed')

    def sendAvatarsToDestination(self, avIdList):
        if len(avIdList) > 0:
            bossZone = self.bldg.createBossOffice(avIdList, self.bossType)
            for avId in avIdList:
                if avId:
                    self.sendUpdateToAvatarId(avId, 'setBossOfficeZoneForce', [bossZone])

    def getSpecificGroupType(self):
        return self.groupType

    @property
    def closeTime(self):
        return ElevatorData[self.type]['closeTime']

    @property
    def openTime(self):
        return ElevatorData[self.type]['openTime']

    def enterClosing(self):
        DistributedElevatorAI.DistributedElevatorAI.enterClosing(self)
        taskMgr.doMethodLater(self.closeTime, self.elevatorClosedTask, self.uniqueName('closing-timer'))

    def enterClosed(self):
        DistributedElevatorExtAI.DistributedElevatorExtAI.enterClosed(self)
        self.fsm.request('opening')

    def enterOpening(self):
        DistributedElevatorAI.DistributedElevatorAI.enterOpening(self)
        taskMgr.doMethodLater(self.openTime, self.waitEmptyTask, self.uniqueName('opening-timer'))

    def checkBoard(self, av):
        # Are they TOO SMALL laff?
        if av.getHp() < self.minLaff:
            return ElevatorResponse.MinLaff

        # Are we checking for questRequired?
      #  if self.questRequired is not None:
       #     # Is this elevator force exiting?
        #    if self.questRequired is True:
         #       return ElevatorResponse.MissingQuest

            # Have they done this quest?
          #  if not av.completedQuestId(self.questRequired, matchOk=True):
           #     # They have not done the quest lol cope
            #    return ElevatorResponse.MissingQuest

        # All else has passed, they're good
        return ElevatorResponse.Success

    def requestBoard(self, *args):
        self.notify.debug('reBoard')
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if av:
            boardResponse = self.checkBoard(av)
            newArgs = (avId,) + args + (boardResponse,)
            if boardResponse == ElevatorResponse.Success:
                self.acceptingBoardersHandler(*newArgs)
            else:
                self.rejectingBoardersHandler(*newArgs)
        else:
            self.notify.warning('avid: %s does not exist, but tried to board an elevator' % avId)