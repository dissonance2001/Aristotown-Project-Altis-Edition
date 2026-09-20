import random
from direct.interval.IntervalGlobal import *
from toontown.clashsuit.suit.heads.classes.UniqueSkelecogAnimatedSuitHead import *
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


FreakoutTaskName = 'FindTheFamilyAnimatedSuitHead-NeutralFreakoutTask'
WaitRange = (0.4, 2.0)
RepeatTwitchTimes = [1, 2, 3]
RepeatTwitchWeights = [6, 9, 7]
AngleRange = [14, 40]
TwitchTimeRange = (0.06, 0.17)

BodyFreakoutTaskName = 'FindTheFamilyAnimatedSuitHead-BodyNeutralFreakoutTask'
BodyWaitRange = (0.6, 7)
BodyAnimationSpeedRange = (15, 19)
BodyAnimationChoices = (
    'victory', 'slip-forward', 'slip-backward', 'drop-react', 'sidestep-left',
    'sidestep-right', 'reach', 'soak', 'finger-wag', 'mob-mentality'
)
BodyRepeatAnimationTimes = [1, 2, 3, 4]
BodyRepeatAnimationWeights = [6, 6, 1, 1]


@DirectNotifyCategory()
@AnimatedSuitHeadClass(suitName=('ftf_s', 'ftf_m', 'ftf_l', 'ftf_c', 'ftf_s_rt', 'ftf_s_br', 'ftf_m_cf', 'ftf_c_ac'))
class FindTheFamilyAnimatedSuitHead(UniqueSkelecogAnimatedSuitHead):
    """
    Used for Find the Family cogs to do the nuclear effect.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.freakoutSeq = None
        self.bodyFreakoutSeq = None

    def cleanup(self):
        self.__stopFreakout()
        self.__stopBodyFreakout()
        self.ignoreAll()
        super().cleanup()

    def uniqueName(self, str):
        if getattr(self, 'suit', None) and getattr(self.suit, 'doId', None):
            return f'{self.suit.doId}-{str}'

        return f'{id(self)}-{str}'

    def listenForEvents(self):
        self.accept('ClashBattleBase-enterLocalToonWaitForInput', self.startBodyFreakout)
        self.accept('MovieDrop-suitPreFlatten', self.suitGotFlattened)
        # self.accept('ClashBattleBase-exitLocalToonWaitForInput', self.__stopBodyFreakout)

    def suitGotFlattened(self, suit):
        if not getattr(self, 'suit', None):
            return
        if suit is not self.suit:
            return

        # Can't have this goober freaking out when they're a hole in the floor
        self.__stopFreakout()
        self.__stopBodyFreakout()

    def startFreakout(self):
        self.__endOldFreakout()

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

        waitForNextTime = lerp(WaitRange[0], WaitRange[1], random.random())
        twitchRepeatAmt = random.choices(RepeatTwitchTimes, weights=RepeatTwitchWeights)[0]

        self.freakoutSeq = Sequence()
        for i in range(twitchRepeatAmt):
            lastTwitch = i == twitchRepeatAmt - 1
            twitchTime = lerp(TwitchTimeRange[0], TwitchTimeRange[1], random.random())
            isH = random.random() < 0.5
            angleRange = AngleRange if isH else (AngleRange[0] * 2/3, AngleRange[1] * 2/3)
            ourAngle = lerp(angleRange[0], angleRange[1], random.random())
            multiplier = random.choice([-1, 1])
            finalHpr = (ourAngle*multiplier, 0, 0) if isH else (0, 0, ourAngle*multiplier)
            self.freakoutSeq.append(Sequence(
                self.hprInterval(twitchTime, finalHpr, startHpr=(0, 0, 0)),
            ))
            if lastTwitch:
                self.freakoutSeq.append(self.hprInterval(twitchTime * 2, (0, 0, 0), blendType='easeOut'))

        self.freakoutSeq.start()

        task.delayTime = waitForNextTime + self.freakoutSeq.getDuration()
        return task.again

    def startBodyFreakout(self, battle=None):
        self.__endOldBodyFreakout()

        if settings['reduce-battle-effects']:
            return

        if battle:
            if not getattr(self, 'suit', None) or self.suit not in battle.suits:
                return

        self.doMethodLater(0, self.__newBodyFreakout, name=self.uniqueName(BodyFreakoutTaskName))

    def __stopBodyFreakout(self):
        self.__endOldBodyFreakout()

    def __endOldBodyFreakout(self):
        self.removeTask(self.uniqueName(BodyFreakoutTaskName))
        self.__finishBodyFreakoutSeq()

    def __finishBodyFreakoutSeq(self):
        if self.bodyFreakoutSeq:
            self.bodyFreakoutSeq.finish()
            self.bodyFreakoutSeq = None

    def __newBodyFreakout(self, task=None):
        self.__finishBodyFreakoutSeq()
        if not getattr(self, 'suit', None):
            self.__endOldBodyFreakout()
            return

        animChoice = random.choice(BodyAnimationChoices)
        animSpeed = lerp(BodyAnimationSpeedRange[0], BodyAnimationSpeedRange[1], random.random())
        waitForNextTime = lerp(BodyWaitRange[0], BodyWaitRange[1], random.random())
        animRepeatAmt = random.choices(BodyRepeatAnimationTimes, weights=BodyRepeatAnimationWeights)[0]

        self.bodyFreakoutSeq = Sequence()
        for _ in range(animRepeatAmt):
            endFrame = self.suit.getNumFrames(animChoice)
            if random.random() < 0.45:
                endFrame = int(round((endFrame / 2) + (random.random() * endFrame / 2)))
            self.bodyFreakoutSeq.append(ActorInterval(self.suit, animChoice, playRate=animSpeed, endFrame=endFrame))

        self.bodyFreakoutSeq.append(Func(self.suit.loop, 'neutral'))
        self.bodyFreakoutSeq.start()

        task.delayTime = waitForNextTime + self.bodyFreakoutSeq.getDuration()
        return task.again

    def stopAllFreakout(self):
        self.__stopFreakout()
        self.__stopBodyFreakout()
        self.ignoreAll()
