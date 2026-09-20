import math

from toontown.quest3.QuestLocalizer import HL_Wanted, OBJ_Defeat, PROG_Defeat, QuestProgress_Complete, SC_Laff_Building, \
    PFX_TAKEDOWN, GivenLaff, AuxillaryText_Less_Than, SC_Laff_Building_1Laff, GivenBut1Laff
from toontown.quest3.base.QuestObjective import *
from toontown.quest3.context.BuildingLaffContext import BuildingLaffContext
from toontown.clashsuit.suit import SuitDNA
from toontown.quest3.objectives.BuildingObjective import BuildingObjective


class BuildingLaffObjective(BuildingObjective):

    def __init__(self,
                 npc=2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 zoneUnlocks=None,
                 buildingLocation: int = None,
                 cogTrack: str = None,
                 floorMinimum: int = 1,
                 buildingCount: int = 1,
                 wantFloors: bool=False,
                 laffRatio: float = 1.0):
        super().__init__(npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable, zoneUnlocks=zoneUnlocks)
        self.cogTrack = cogTrack
        self.floorMinimum = floorMinimum
        self.buildingLocation = buildingLocation
        self.buildingCount = buildingCount
        self.wantFloors = wantFloors
        # Let's calculate the Laff we want based on the given ratio.
        self.laffRatio = laffRatio

    @staticmethod
    def getDifficultyRange(questerType: QuesterType, questSource: QuestSource, **extraArgs):
        """
        Returns the difficulty range required to use this objective in random quest generation.

        :return: Any of the following:
                 A) Two floats, for a lower and upper bound
                 B) A float and None, for a lower bound and no upper bound
                 C) None and a float, for no lower bound and an upper bound
                 D) Two nones, for no difficulty bound
                 E) One none, for "cannot be used"
        """
        return None

    def calculateProgress(self, context: BuildingLaffContext, questReference: QuestReference, quester: Quester) -> int:
        if type(context) is not BuildingLaffContext:
            return 0

        # Match zone id.
        zoneId = context.zoneId

        if self.buildingLocation is not None:
            # Match by Hood
            if ZoneUtil.getHoodId(self.buildingLocation) == self.buildingLocation:
                if ZoneUtil.getHoodId(self.buildingLocation) != ZoneUtil.getHoodId(zoneId):
                    # This cog was killed in the wrong hood.
                    return 0

            # Match by Branch
            elif ZoneUtil.getBranchZone(self.buildingLocation) == self.buildingLocation:
                if ZoneUtil.getBranchZone(self.buildingLocation) != ZoneUtil.getBranchZone(zoneId):
                    # This cog was killed in the wrong branch.
                    return 0

            # Undefined match
            else:
                raise AttributeError("DefeatCogObjective given undefined zoneId to parse")

        # Match the other args.
        if self.cogTrack is not None:
            if self.cogTrack != context.track:
                return 0

        if self.floorMinimum > context.floors:
            return 0

        # Calculate laff threshold with a laff value not a float
        if math.ceil(quester.getMaxHp() * self.laffRatio) < context.laffRatio and quester.getMaxHp() != 1:
            return 0

        # This building counts.
        if self.wantFloors:
            return context.floors
        return 1
    
    def getCompletionRequirement(self) -> int:
        return self.buildingCount

    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        buildingPoster = poster.LEFT

        geom, offset = self.getBuildingIconGeom()
        poster.fitGeometry(geom=geom, fFlip=0)
        if self.cogTrack:
            self.loadElevator(geom, self.floorMinimum)
            poster.visual_setFrameGeom(
                buildingPoster, geom=geom, scale=0.15, 
                pos=(-0.06 + offset, 10, 0), hpr=(180, 0, 0)
            )
        else:
            poster.visual_setFrameGeom(buildingPoster, geom=geom, scale=0.13)
        buildingName = self.getBuildingName(capitalize=True, accurate=True)
        buildingName = buildingName[0].lower() + buildingName[1:]
        poster.visual_setFrameText(buildingPoster, PFX_TAKEDOWN + buildingName)

        laffPoster = poster.RIGHT
        poster.visual_setLaffMeterGeom(laffPoster, math.ceil(base.localAvatar.getMaxHp() * self.laffRatio))
        if base.localAvatar.getMaxHp() == 1:
            poster.visual_setFrameText(laffPoster, text=GivenBut1Laff)
        else:
            poster.visual_setFrameText(laffPoster, text=GivenLaff % str(math.ceil(base.localAvatar.getMaxHp() * self.laffRatio)))

        # Other poster changes
        poster.visual_setFrameColor(poster.LEFT, 'blue')
        poster.visual_setFrameColor(poster.RIGHT, 'blue')
        poster.visual_setAuxText(AuxillaryText_Less_Than)
        poster.label_auxillaryText.show()

        # If we're complete, bonus info
        if complete:
            if self.npcReturnable:
                poster.visual_setFrameColor(poster.RIGHT, 'blue')
                poster.visual_setNpcFrame(poster.RIGHT, self.getToNpcId())
                poster.visual_setFrameText(poster.RIGHT, self.getToNpcName())
                poster.label_auxillaryText.show()
        # And if we're not, show progress
        else:
            if self.buildingCount > 1:
                value, range, textFormat = self.getProgressFormat(questReference)
                poster.visual_setProgressInfo(value=value, range=range, textFormat=textFormat)

    def getProgressFormat(self, questReference):
        return questReference.getQuestProgress(self.objectiveIndex), self.buildingCount, PROG_Defeat

    def getInfoTextStrings(self, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex) and self.npcReturnable:
            # Return the goal location
            return super().getInfoTextStrings(questReference)
        else:
            # Tell them where the cogs are, and what laff ratio.
            return self.getLocationName(self.buildingLocation),

    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                return self.getFinishToontaskStrings()
            return tuple()

        # Get the message formatting.
        buildingName = self.getBuildingName()

        # Get locaton formatting.
        locName = ''
        if self.buildingLocation is not None:
            locName = self.getLocationName(zoneId=self.buildingLocation)

        if quester.getMaxHp() == 1:
            return SC_Laff_Building_1Laff % (buildingName, locName),
        else:
            return SC_Laff_Building % (buildingName, locName, str(int(self.laffRatio*100))),

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Wanted
    
    def getObjectiveGoal(self) -> str:
        neededLaff = 15
        if base.localAvatar:
            neededLaff = int(base.localAvatar.getMaxHp() * self.laffRatio)
        return OBJ_Defeat % self.getBuildingName() + f' with less than {neededLaff} Laff'
    
    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        elif self.buildingCount == 1:
            return ''
        return PROG_Defeat.format(value=min(progress, self.buildingCount), range=self.buildingCount)

    """a little methodology"""

    def getBuildingName(self, capitalize=False, accurate=False):
        if self.wantFloors:
            return f"{self.buildingCount} Building Floor{'s' if self.buildingCount > 1 else ''}"

        buildingName = 'a ' if self.buildingCount == 1 else ('some ' if not accurate else f'{self.buildingCount} ')
        if capitalize:
            buildingName = buildingName[0].upper() + buildingName[1:]
        if self.floorMinimum != 1:
            numberName = {
                2: 'two+',
                3: 'three+',
                4: 'four+',
                5: 'five+',
                6: 'six',
            }.get(self.floorMinimum) + (' story ' if not capitalize else ' Story ')
            if capitalize:
                numberName = numberName[0].upper() + numberName[1:]
            buildingName = buildingName + numberName
        if self.cogTrack is not None:
            suitName = SuitDNA.suitDeptFullnames.get(self.cogTrack)
            buildingName = buildingName + suitName + ' '
        buildingName = buildingName + 'Cog Building' + ('' if self.buildingCount == 1 else 's')
        return buildingName

    def getBuildingIconGeom(self):
        if self.cogTrack:
            filepath, offset = {
                'c': ('phase_4/models/modules/suit_landmark_corp', -0.02),
                'l': ('phase_4/models/modules/suit_landmark_legal', 0.0),
                'm': ('phase_4/models/modules/suit_landmark_money', 0.0),
                's': ('phase_4/models/modules/suit_landmark_sales', 0.0),
                'g': ('phase_4/models/modules/suit_landmark_board', 0.02),
            }.get(self.cogTrack)
            return loader.loadModel(filepath), offset

        bookModel = loader.loadModel('phase_3.5/models/gui/stickerbook_gui')
        geom = bookModel.find('**/COG_building')
        bookModel.removeNode()
        return geom, 0

    @staticmethod
    def loadElevator(building, numFloors):
        elevatorNodePath = hidden.attachNewNode('elevatorNodePath')
        elevatorModel = loader.loadModel('phase_4/models/modules/elevator')
        floorIndicator = [None, None, None, None, None, None]
        npc = elevatorModel.findAllMatches('**/floor_light_?;+s')
        for np in npc:
            floor = int(np.getName()[-1:]) - 1
            floorIndicator[floor] = np
            if floor < numFloors:
                np.setColor(Vec4(0.5, 0.5, 0.5, 1.0))
            else:
                np.hide()

        elevatorModel.reparentTo(elevatorNodePath)
        suitDoorOrigin = building.find('**/*_door_origin')
        elevatorNodePath.reparentTo(suitDoorOrigin)
        elevatorNodePath.setPosHpr(0, 0, 0, 0, 0, 0)

    def _getKwargStr(self):
        kwargstr = super()._getKwargStr()
        if self.buildingLocation is not None:
            kwargstr += f'buildingLocation={self._numToLocStr(self.buildingLocation)}, '
        if self.cogTrack is not None:
            kwargstr += f"cogTrack='{self.cogTrack}', "
        if self.floorMinimum != 1:
            kwargstr += f"floorMinimum={self.floorMinimum}, "
        if self.buildingCount != 1:
            kwargstr += f"buildingCount={self.buildingCount}, "
        return kwargstr

    def __repr__(self):
        return f'BuildingLaffObjective({self._getKwargStr()[:-2]})'
