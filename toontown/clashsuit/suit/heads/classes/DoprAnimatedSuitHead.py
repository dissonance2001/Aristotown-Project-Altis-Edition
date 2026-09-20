from toontown.clashsuit.suit.heads.AnimatedSuitHead import *
from toontown.clashsuit.suit.heads.AnimatedSuitHeadRepository import AnimatedSuitHeadClass
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.interval.IntervalGlobal import Sequence, ActorInterval, Func
import random


FreakoutTaskName = 'DoprAnimatedSuitHead-NeutralFreakoutTask'
WaitRange = (0.6, 7)
AnimationSpeedRange = (15, 19)
AnimationChoices = (
    'victory', 'squirt-large-react', 'slip-forward', 'slip-backward', 'drop-react', 'sidestep-left',
    'sidestep-right', 'reach', 'soak', 'effort', 'throw-object', 'finger-wag', 'speak', 'mob-mentality'
)
RepeatAnimationTimes = [1, 2, 3, 4]
RepeatAnimationWeights = [6, 6, 1, 1]


@DirectNotifyCategory()
@AnimatedSuitHeadClass(suitName='dopr')
class DoprAnimatedSuitHead(AnimatedSuitHead):
    """
    While this is technically dopr's animated head, this also handles making his body freak out
    and do random animations while in neutral.
    Once the battle round starts, he will stop freaking out.
    """
    def __init__(self, *args, **kwargs):
        AnimatedSuitHead.__init__(self, *args, **kwargs)
        self.freakoutSeq = None

    def uniqueName(self, str):
        if getattr(self, 'suit', None) and getattr(self.suit, 'doId', None):
            return f'{self.suit.doId}-{str}'

        return f'{id(self)}-{str}'

    def listenForEvents(self):
        self.accept('ClashBattleBase-enterLocalToonWaitForInput', self.__startFreakout)
        self.accept('ClashBattleBase-exitLocalToonWaitForInput', self.__stopFreakout)

    def __startFreakout(self, battle=None):
        self.__endOldFreakout()

        if settings['reduce-battle-effects']:
            return

        self.doMethodLater(0, self.__newFreakout, name=self.uniqueName(FreakoutTaskName))

    def __stopFreakout(self):
        self.__endOldFreakout()

    def __endOldFreakout(self):
        self.removeTask(self.uniqueName(FreakoutTaskName))
        self.__finishFreakoutSeq()

    def __finishFreakoutSeq(self):
        if self.freakoutSeq:
            self.freakoutSeq.finish()
            self.freakoutSeq = None

    def __newFreakout(self, task=None):
        self.__finishFreakoutSeq()
        if not getattr(self, 'suit', None):
            self.__endOldFreakout()
            return

        animChoice = random.choice(AnimationChoices)
        animSpeed = lerp(AnimationSpeedRange[0], AnimationSpeedRange[1], random.random())
        waitForNextTime = lerp(WaitRange[0], WaitRange[1], random.random())
        animRepeatAmt = random.choices(RepeatAnimationTimes, weights=RepeatAnimationWeights)[0]

        self.freakoutSeq = Sequence()
        for _ in range(animRepeatAmt):
            endFrame = self.suit.getNumFrames(animChoice)
            if random.random() < 0.45:
                endFrame = int(round((endFrame / 2) + (random.random() * endFrame / 2)))
            self.freakoutSeq.append(ActorInterval(self.suit, animChoice, playRate=animSpeed, endFrame=endFrame))

        self.freakoutSeq.append(Func(self.suit.loop, 'neutral'))
        self.freakoutSeq.start()

        task.delayTime = waitForNextTime + self.freakoutSeq.getDuration()
        return task.again

    def cleanup(self):
        self.ignoreAll()
        self.__endOldFreakout()
        super().cleanup()
