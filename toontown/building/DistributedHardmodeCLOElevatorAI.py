from toontown.building.ElevatorConstants import *
from toontown.building import DistributedBossElevatorAI, ElevatorConstants
from toontown.quest3.QuestEnums import QuestSource
from toontown.quest3.base.QuestHistory import QuestHistory
#from ..groups.GroupEnums import GroupType
from ..quest3.base.QuestReference import QuestId
from toontown.toonbase import ToontownGlobals
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from toontown.ai.ToontownAIRepository import ToontownAIRepository


class DistributedHardmodeCLOElevatorAI(DistributedBossElevatorAI.DistributedBossElevatorAI):
  #  questRequired = QuestId(QuestSource.Directive, 1, 1)
    base_elevator_time = ElevatorConstants.ElevatorData[ElevatorConstants.ELEVATOR_CLO_HARDMODE]['countdown']
    #groupType = GroupType.OCLO

    def __init__(self, air, bldg, zone, antiShuffle = 0, minLaff = 0):
        """
        :type air: ToontownAIRepository
        """
        DistributedBossElevatorAI.DistributedBossElevatorAI.__init__(self, air, bldg, zone, antiShuffle=antiShuffle, minLaff=minLaff)
        self.type = ELEVATOR_CLO_HARDMODE
        self.countdownTime = ElevatorData[self.type]['countdown']
        
   # def checkBoard(self, av):
    #    # Temporary logic, put in actual logic later. Maybe make hardmode elevator base.
     ##   dept = ToontownGlobals.cogHQZoneId2deptIndex(self.zone)
     #   if av.getHp() < self.minLaff:
     #       return ElevatorResponse.MinLaff
     #   if not av.readyForPromotion(dept):
     #       return ElevatorResponse.Promotion
     #   # Check for executive washroom key.
     #   if self.questRequired is not None:
     #       if not av.completedQuestId(self.questRequired, matchOk=True):
     #           # They have not done the quest lol cope
     #           return ElevatorResponse.MissingQuest
        # Looks like we're good!
     #   return ElevatorResponse.Success
