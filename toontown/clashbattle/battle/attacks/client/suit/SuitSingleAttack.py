from direct.interval.IntervalGlobal import *

from toontown.clashbattle.battle import MovieUtil
from toontown.clashbattle.battle.attacks.client.Attack import Attack


class SuitSingleAttack(Attack):
    ALLOW_GROUPING = False
    FORCE_SPLIT_CAMERA = False

    def getAttackMovie(self):
        suitTrack = Sequence(Func(self.doConditionCallout), self.doAttack())
        toonHprTrack = Parallel()
        for t in self.targetDicts:
            toon = t["avatar"]
            if not self.isToon(toon):
                continue
            toonHprTrack.append(Sequence(
                Func(toon.headsUp, self.battle, MovieUtil.PNT3_ZERO), 
                Func(toon.loop, 'neutral')
            ))

        neutralIval = Func(self.invoker.loop, 'neutral')
        suitTrack = Sequence(suitTrack, neutralIval, toonHprTrack)
        preAttackSeq = self.invoker.getPreAttackSeq()
        postAttackSeq = self.invoker.getPostAttackSeq()
        resetTrack = self.getResetTrack()
        endTrack = self.getEndTrack()
        resetSuitTrack = Sequence(
            Func(self.invoker.onSuitAttackBegin),
            preAttackSeq,
            resetTrack, suitTrack, endTrack,
            Func(self.invoker.onSuitAttackEnd),
            postAttackSeq,
        )
        camTrack = self.chooseCameraShot(resetSuitTrack.getDuration())
        return resetSuitTrack, camTrack

    def getCameraShot(self, duration):
        if not self.targetDicts:
            return self.camera.randomActorShot(self.invoker, self.battle, duration, 'suit')

        if self.FORCE_SPLIT_CAMERA:
            return self.camera.randomSplitShot(self.invoker, self.targetDicts[0]["avatar"], self.battle, duration)

        return self.camera.randomAttackCam(
            self.invoker, self.targetDicts[0]["avatar"], self.battle, duration, self.OPEN_SHOT_DUR, 'suit')
