from direct.actor.Actor import Actor
from toontown.level.editor import EditorGlobals
from toontown.level import BasicEntities
from toontown.zone.entities.quest.QuestEntityBase import QuestCutsceneEntityBase
from toontown.zone.entities.quest.QuestInteractibleModels import SpecialQuestModelBase, SpecialModelRegistry
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory(debug=True)
class QuestAnimatedEntity(QuestCutsceneEntityBase, BasicEntities.NodePathEntity):
    def __init__(self, level, entId):
        QuestCutsceneEntityBase.__init__(self, level, entId)
        self.entInitialized = False
        BasicEntities.NodePathEntity.__init__(self, level, entId)
        self.entInitialized = True
        self.actor = None
        self.behaviorDict = {
            # Does nothing, default
            'None': self.__doNoneBehavior,
            # Poses the actor in a specific anim and specific frame
            'Pose': self.__doPoseBehavior,
            # Loops a specific anim on the actor
            'Loop': self.__doLoopBehavior,
            # Hides (stashes) the actor
            'Hide': self.__doHideBehavior,
            # A special behavior used for SpecialQuestModels.
            'Special': self.__doSpecialBehavior,
        }
        self.loadActor()

    def destroy(self):
        if self.actor:
            self.actor.cleanup()
            self.actor = None
        self.behaviorDict = {}
        BasicEntities.NodePathEntity.destroy(self)

    # Actor interface filler

    def play(self, *args, **kwargs):
        if not self.actor:
            return
        self.actor.play(*args, **kwargs)

    def loop(self, *args, **kwargs):
        if not self.actor:
            return
        self.actor.loop(*args, **kwargs)

    def pose(self, *args, **kwargs):
        if not self.actor:
            return
        self.actor.pose(*args, **kwargs)

    def stop(self, *args, **kwargs):
        if not self.actor:
            return
        self.actor.stop(*args, **kwargs)

    # Special model interface filler

    def setSpecial(self, *args, **kwargs):
        if not self.actor:
            return
        self.actor.setSpecial(*args, **kwargs)

    def getAnim(self, *args, **kwargs):
        if not self.actor:
            return
        return self.actor.getAnim(*args, **kwargs)

    # Loading

    def loadActor(self):
        if self.actor:
            self.actor.cleanup()
            self.actor = None
        if self.modelPath is None:
            return

        specialQuestModel = SpecialModelRegistry.get(self.modelPath)
        if not specialQuestModel:
            # Actor code
            try:
                if self.modelPath.find('-zero') != -1:
                    animPathBase = self.modelPath.split('-zero')[0]
                else:
                    animPathBase = self.modelPath
                animPathBase = animPathBase.replace('_chr_', '_anim_')
                animDict = {animName: animPathBase + f'-{animName}' for animName in self.animList}
                self.actor = Actor(loader.loadModel(self.modelPath), animDict)
            except:
                self.notify.warning(f'invalid Actor, please try again.')
                return
        else:
            # Special model code
            self.actor = specialQuestModel(self.modelPath)

        if not self.actor:
            return

        self.actor.reparentTo(self)

        # Make sure that wantedQuest is in QuestId format
        self.callSetters('wantedQuest')
        self.checkQuestState()

    def checkQuestState(self):
        # Check local av's quest state to determine what behavior the actor should do
        hasHistory = self.localAvHasQuestHistory()
        hasFurtherQuest = self.localAvHasFurtherQuest()
        if hasHistory or hasFurtherQuest:
            self.__doFinishedBehavior()
        else:
            self.__doUnfinishedBehavior()

    # Behavior functions

    def __doNoneBehavior(self, behaviorState='unfinished'):
        self.notify.debug(f'Got {behaviorState} None behavior, doing nothing.'),

    def __doPoseBehavior(self, behaviorState='unfinished'):
        if not (self.actor and self.animList):
            self.notify.debug('Ignoring behavior because invalid actor or anim list.')
            return
        if isinstance(self.actor, SpecialQuestModelBase):
            self.notify.debug('Ignoring behavior because special quest model cannot do poses.')
            return

        anim = self.qst_unfinAnim if behaviorState == 'unfinished' else self.qst_finAnim
        argList = self.qst_unfinArgs if behaviorState == 'unfinished' else self.qst_finArgs
        poseFrame = 0 if len(argList) < 1 else argList[0]
        self.notify.debug(f'Got {behaviorState} Pose behavior, posing actor with anim {anim} and frame {poseFrame}')
        self.actor.pose(anim, poseFrame)

    def __doLoopBehavior(self, behaviorState='unfinished'):
        if not (self.actor and self.animList):
            self.notify.debug('Ignoring behavior because invalid actor or anim list.')
            return
        if isinstance(self.actor, SpecialQuestModelBase):
            self.notify.debug('Ignoring behavior because special quest model cannot do loops.')
            return

        anim = self.qst_unfinAnim if behaviorState == 'unfinished' else self.qst_finAnim
        self.notify.debug(f'Got {behaviorState} Loop behavior, looping actor with anim {anim}')
        self.actor.loop(anim)

    def __doHideBehavior(self, behaviorState='unfinished'):
        self.notify.debug(f'Got {behaviorState} Hide behavior, stashing actor.')
        if self.actor:
            self.actor.stop()
            self.stash()

    def __doSpecialBehavior(self, behaviorState='unfinished'):
        if not (self.actor and isinstance(self.actor, SpecialQuestModelBase)):
            self.notify.debug('Ignoring behavior because invalid special model.')
            return

        anim = self.qst_unfinAnim if behaviorState == 'unfinished' else self.qst_finAnim
        args = self.qst_unfinArgs if behaviorState == 'unfinished' else self.qst_finArgs
        self.notify.debug(f'Got {behaviorState} special behavior with anim {anim} and args {args}, delegating to QuestSpecialModel.')
        self.actor.setSpecial(anim)

    def __doUnfinishedBehavior(self):
        # Local av hasn't finished the quest, so do our unfinished behavior
        self.behaviorDict[self.qst_unfinBehavior](behaviorState='unfinished')

    def __doFinishedBehavior(self):
        # Local av has finished the quest, so do our finished behavior
        self.behaviorDict[self.qst_finBehavior](behaviorState='finished')

    def cutscene_onFinish(self):
        self.notify.debug(f'Cutscene regarding us finished, checking quest state')
        # A cutscene has finished, check and set our quest state
        self.checkQuestState()

    if EditorGlobals.wantLevelEditor():
        def setModelPath(self, path):
            self.modelPath = path
            self.loadActor()

        def setAnimList(self, animList):
            self.animList = animList
            self.loadActor()

        def setQst_unfinBehavior(self, qst_unfinBehavior):
            self.qst_unfinBehavior = qst_unfinBehavior
            self.loadActor()

        def setQst_unfinAnim(self, qst_unfinAnim):
            self.qst_unfinAnim = qst_unfinAnim
            self.loadActor()

        def setQst_unfinArgs(self, qst_unfinArgs):
            self.qst_unfinArgs = qst_unfinArgs
            self.loadActor()

        def setQst_finBehavior(self, qst_finBehavior):
            self.qst_finBehavior = qst_finBehavior
            self.loadActor()

        def setQst_finAnim(self, qst_finAnim):
            self.qst_finAnim = qst_finAnim
            self.loadActor()

        def setQst_finArgs(self, qst_finArgs):
            self.qst_finArgs = qst_finArgs
            self.loadActor()
