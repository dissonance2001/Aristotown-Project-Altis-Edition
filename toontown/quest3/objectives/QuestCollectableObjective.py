from toontown.quest3.base.QuestObjective import *
from toontown.quest3.context.QuestCollectableContext import \
    QuestCollectableContext
from toontown.quest3.QuestEnums import QuestCollectable
from toontown.quest3.QuestLocalizer import HL_Search, OBJ_Collect, QuestProgress_Complete, SC_Search, PROG_Collect, \
    PROG_Times


class QuestCollectableObjective(QuestObjective):
    """
    The de facto "treasure hunt" objective.
    """

    CollectableInfoStrings = {
        QuestCollectable.SwingsetA: ('Behind a tree, on a', 'street in the punchline', 'of Toontown Central'),
        QuestCollectable.SwingsetB: ('Behind a tree, on a', 'street in a playground', 'filled with saltwater'),
        QuestCollectable.SwingsetC: ('Where the water falls', 'in a forested playground'),
        QuestCollectable.SwingsetD: ('Hidden', 'in a playground', 'of green growth'),
        QuestCollectable.TumblesTiara: ("On the gazebo", "in Daffodil Gardens"),
        QuestCollectable.ToonselPresent: ("Somewhere in the", "Toonseltown Playground"),
        QuestCollectable.KudosBox: ("In the alleyway", "on Wizard Way"),
        QuestCollectable.AllStarShower: ("Fast Asleep - All Star Suites", "Drowsy Dreamland", "Lullaby Lane"),
    }

    def __init__(self,
                 npc = 2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 collectable: QuestCollectable = QuestCollectable.TumblesTiara):
        super().__init__(npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable)
        self.collectable = collectable

    def calculateProgress(self, context: QuestCollectableContext, questReference: QuestReference, quester: Quester) -> int:
        if type(context) is not QuestCollectableContext:
            return 0
        return context.getCollectable() == self.collectable

    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        searchPoster = poster.CENTER if not (complete and self.npcReturnable) else poster.LEFT

        poster.visual_setFrameColor(searchPoster, {
            QuestCollectable.AllStarShower: 'ourple',
        }.get(self.collectable, 'green'))
        self.setPosterGeom(searchPoster, poster)

        # If we're complete, bonus info
        if complete:
            if self.npcReturnable:
                poster.visual_setFrameColor(poster.RIGHT, 'green')
                poster.visual_setNpcFrame(poster.RIGHT, self.getToNpcId())
                poster.visual_setFrameText(poster.RIGHT, self.getToNpcName())
                poster.label_auxillaryText.show()

    def getCollectableGeom(self):
        if self.collectable in (QuestCollectable.SwingsetA, QuestCollectable.SwingsetB,
                                QuestCollectable.SwingsetC, QuestCollectable.SwingsetD):
            geom = loader.loadModel('areas/estate/furniture/models/cc_m_ara_est_prp_furn_candy_swingset')
            return geom, (0, 0, -0.05), 0.012
        elif self.collectable == QuestCollectable.TumblesTiara:
            geom = loader.loadModel('cosmetics/hat/models/cc_m_acc_hat_crown_tiara_classic')
            return geom, (0, 0, -0.03), 0.06
        elif self.collectable == QuestCollectable.ToonselPresent:
            geom = loader.loadModel('phase_13/models/events/toonseltown/present_1')
            return geom, (0, 0, -0.05), 0.01
        elif self.collectable == QuestCollectable.KudosBox:
            geom = loader.loadModel('phase_9/models/cogHQ/woodCrateB')
            return geom, (0, 0, -0.05), 0.017
        elif self.collectable == QuestCollectable.AllStarShower:
            paceLobby = loader.loadModel('phase_8/models/areas/ttcc_int_psetter_lobby')
            geom = NodePath('shower')
            nodeParts = (
                'waterfall',
                # 'fountain_wall_geom',
                # 'lights',
                'fountain_side_geom',
                'fountain_floor_geom',
                # 'ceiling_lights_bottom',
            )
            for nodeName in nodeParts:
                node = geom.attachNewNode('node')
                paceLobby.find(f'**/{nodeName}').copyTo(node)
            geom.setDepthTest(1)
            geom.setDepthWrite(1)
            paceLobby.removeNode()
            return geom, (0, 0, -0.07118), 0.00578

    def setPosterGeom(self, posterPosition, poster):
        # Set Image
        geom, pos, scale = self.getCollectableGeom()
        poster.visual_setFrameGeom(posterPosition, geom=geom,
                                   scale=scale, pos=pos, hpr=(0, 0, 0))
        # Set Text
        poster.visual_setFrameText(posterPosition, f'{self.getItemPrefix()}{self.getItemName()}')

    def getInfoTextStrings(self, questReference: QuestReference) -> tuple:
        # If we're complete and demand NPC completion, point to NPC instead
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex) and self.npcReturnable:
            return super().getInfoTextStrings(questReference)

        return self.CollectableInfoStrings.get(self.collectable, ("Undefined Info",))

    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                if self.collectable == QuestCollectable.AllStarShower:
                    return 'I did it. I am now clean.', 'I knew something was missing from my life.'
                else:
                    return self.getFinishToontaskStrings()
            return tuple()
        if self.collectable == QuestCollectable.AllStarShower:
            return 'I need to take an All-Star Shower SOOOOO BADLY!!', 'WAGH!!!! I STINK!!!!', 'WHERE CAN I FIND A SHOWER???'
        return SC_Search % self.getItemName(),

    def getItemPrefix(self) -> str:
        if self.collectable == QuestCollectable.AllStarShower:
            return 'Take an '
        return 'Find a '
    
    def getItemName(self) -> str:
        if self.collectable in (QuestCollectable.SwingsetA, QuestCollectable.SwingsetB,
                                QuestCollectable.SwingsetC, QuestCollectable.SwingsetD):
            return "Swingset"
        elif self.collectable == QuestCollectable.TumblesTiara:
            return "Tiara"
        elif self.collectable == QuestCollectable.ToonselPresent:
            return "Present"
        elif self.collectable == QuestCollectable.KudosBox:
            return "Box"
        elif self.collectable == QuestCollectable.AllStarShower:
            return "All-Star Shower"
        return "Something"

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        if self.collectable == QuestCollectable.AllStarShower:
            return 'CLEANSE'
        return HL_Search
    
    def getObjectiveGoal(self) -> str:
        if self.collectable == QuestCollectable.AllStarShower:
            return f'Cleanse at {TTLocalizer.zone2TitleDict[ToontownGlobals.AllStarSuites]} on {TTLocalizer.lLullabyLane} in {TTLocalizer.lDonaldsDreamland}'
        baseStr = OBJ_Collect % f"a {self.getItemName()}"
        extendedStr = ''
        strData = self.CollectableInfoStrings.get(self.collectable, ['Undefined'])
        for i, infoStr in enumerate(strData):
            extendedStr += ' ' if i == 0 else ''
            extendedStr += infoStr[0].lower() + infoStr[1:] + (" " if i != len(strData) - 1 else "")
        return baseStr + extendedStr

    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        return ''

    def getProgressFormat(self, questReference):
        if self.collectable == QuestCollectable.AllStarShower:
            return questReference.getQuestProgress(self.objectiveIndex), 1, PROG_Times
        return questReference.getQuestProgress(self.objectiveIndex), 1, PROG_Collect

    def _getKwargStr(self):
        kwargstr = super()._getKwargStr()
        kwargstr += f'collectable=QuestCollectable.{QuestCollectable(self.collectable).name}, '
        return kwargstr

    def __repr__(self):
        return f'QuestCollectableObjective({self._getKwargStr()[:-2]})'
