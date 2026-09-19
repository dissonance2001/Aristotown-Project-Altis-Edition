from otp.nametag import NametagGlobals
from direct.showbase.DirectObject import DirectObject
from toontown.battle.BattleCamera import BattleCamera
from toontown.battle.RewardPanel import *
from toontown.battle.BattleSounds import *
from otp import *

from toontown.utils.DirectNotifyCategory import getNotify

notify = getNotify('MovieToonVictory')

def __findToonReward(rewards, toon):
    for r in rewards:
        if r['toon'] == toon:
            return r

    return None


class ToonVictorySkipper(DirectObject):

    def __init__(self, numToons, noSkip, camera: bool = True):
        self._numToons = numToons
        self._noSkip = noSkip
        self._camera = camera
        self._startTimes = {}
        self._ivals = []
        self._battle = None

    def destroy(self):
        self._ivals = None

    def getSetupFunc(self, index):
        return Func(self._setupSkipListen, index)

    def getTeardownFunc(self, index):
        return Func(self._teardownSkipListen, index)

    def setBattle(self, battle):
        self._battle = battle

    def setStartTime(self, index, startT):
        self._startTimes[index] = startT

    def setIvals(self, ivals, timeOffset = 0.0):
        for index in self._startTimes:
            self._startTimes[index] += timeOffset

        self._ivals = ivals

    def _setupSkipListen(self, index):
        if not self._noSkip:
            func = Functor(self._skipToon, index)
            self.accept(base.MAP_PAGE_HOTKEY, func)
            self.accept(base.DIALOG_KEY, func)
            self.accept(RewardPanel.SkipBattleMovieEvent, func)

    def _teardownSkipListen(self, index):
        if not self._noSkip:
            self.ignore(base.MAP_PAGE_HOTKEY)
            self.ignore(base.DIALOG_KEY)
            self.ignore(RewardPanel.SkipBattleMovieEvent)

    def _skipToon(self, index):
        nextIndex = index + 1
        if nextIndex >= self._numToons:
            for ival in self._ivals:
                ival.finish()

            if self._battle:
                self._battle.setSkippingRewardMovie()
            for toon in self._battle.toons:
                if toon.doId == base.localAvatar.doId and self._camera:
                    base.camLens.setMinFov(settings['fieldofview']/(4./3.))
                    base.localAvatar.cameraFSM.request("Off")
                    camera.wrtReparentTo(base.localAvatar)
                    base.localAvatar.cameraFSM.request("Orbit")
        elif nextIndex in self._startTimes:
            for ival in self._ivals:
                ival.setT(self._startTimes[nextIndex])


def doToonVictory(localToonActive, toons, rewardToonIds, rewardDicts, rpanel, 
                  allowGroupShot = 1, updatedQuests = {},
                  noSkip = False, dance: bool = True, camera: bool = True):
    track = Sequence()
    if localToonActive == 1:
        track.append(Func(rpanel.show))
        track.append(Func(NametagGlobals.setOnscreenChatForced, 1))
    camTrack = Sequence()
    endTrack = Sequence()
    danceSound = globalBattleSoundCache.getSound('ENC_Win.ogg')
    toonList = []
    countToons = 0
    for t in toons:
        if isinstance(t, int):
            t = base.cr.doId2do.get(t)
        if t:
            toonList.append(t)
        countToons += 1
        if t and dance:
            t.setAnimState('Victory', 1)

    toonId2toon = {}
    for toon in toonList:
        toonId2toon[toon.doId] = toon

    rewardToonList = []
    for id in rewardToonIds:
        rewardToonList.append(toonId2toon.get(id))

    skipper = ToonVictorySkipper(len(toonList), noSkip, camera=camera)
    lastListenIndex = 0
    track.append(skipper.getSetupFunc(lastListenIndex))
    for tIndex, t in enumerate(toonList):
        rdict = __findToonReward(rewardDicts, t)
        if rdict is not None:
            expTrack = rpanel.getExpTrack(
                t, rdict['origExp'], rdict['earnedExp'], 
                rdict['origQuests'], rdict['origMerits'], 
                rdict['merits'], rdict['parts'], rewardToonList, 
                updatedQuests.get(t.doId, []),
                noSkip=noSkip)
            if expTrack:
                skipper.setStartTime(tIndex, track.getDuration())
                track.append(skipper.getTeardownFunc(lastListenIndex))
                lastListenIndex = tIndex
                track.append(skipper.getSetupFunc(lastListenIndex))
                track.append(expTrack)
                camDuration = expTrack.getDuration()
                if camera:
                    camTrack.append(BattleCamera.chooseRewardShot(t, camDuration, allowGroupShot=allowGroupShot))

    track.append(skipper.getTeardownFunc(lastListenIndex))
    track.append(Func(skipper.destroy))
    if localToonActive == 1:
        track.append(Func(rpanel.hide))
        track.append(Func(NametagGlobals.setOnscreenChatForced, 0))
        track.append(Func(base.localAvatar.cameraFSM.request, "Orbit"))
    track.append(endTrack)
    trackdur = track.getDuration()
    if dance:
        soundTrack = SoundInterval(danceSound, duration=trackdur, loop=1)
    else:
        soundTrack = Wait(1.0)
    mtrack = Parallel(track, soundTrack)
    skipper.setIvals((mtrack, camTrack))
    return (mtrack, camTrack, skipper)
