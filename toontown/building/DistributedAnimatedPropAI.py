from direct.distributed import DistributedObjectAI
from direct.distributed.ClockDelta import *
from direct.fsm import ClassicFSM, State
from otp.ai.AIBaseGlobal import *
from urllib.parse import urlparse, parse_qs
import re

class DistributedAnimatedPropAI(DistributedObjectAI.DistributedObjectAI):

    def __init__(self, air, propId):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.fsm = ClassicFSM.ClassicFSM(
            'DistributedAnimatedPropAI',
            [
                State.State('off', self.enterOff, self.exitOff,
                            ['playing']),
                State.State('attract', self.enterAttract, self.exitAttract,
                            ['playing']),
                State.State('playing', self.enterPlaying, self.exitPlaying,
                            ['attract'])
            ], 'off', 'off')
        self.fsm.enterInitialState()
        self.propId = propId
        self.avatarId = 0
        self.videoUrl = ''
        self.videoTimestamp = 0

    def delete(self):
        self.fsm.requestFinalState()
        del self.fsm
        DistributedObjectAI.DistributedObjectAI.delete(self)

    def getPropId(self):
        return self.propId

    def getAvatarInteract(self):
        return self.avatarId

    def getInitialState(self):
        return [self.fsm.getCurrentState().getName(), globalClockDelta.getRealNetworkTime()]

    def getOwnerDoId(self):
        return self.ownerDoId

    def requestInteract(self):
        avatarId = self.air.getAvatarIdFromSender()
        stateName = self.fsm.getCurrentState().getName()
        if self.propId == 9613:
            self.fsm.request('attract' if stateName == 'playing' else 'playing')
            return
        if stateName != 'playing':
            self.sendUpdate('setAvatarInteract', [avatarId])
            self.avatarId = avatarId
            self.fsm.request('playing')
        else:
            self.sendUpdateToAvatarId(avatarId, 'rejectInteract', [])

    def requestExit(self):
        avatarId = self.air.getAvatarIdFromSender()
        stateName = self.fsm.getCurrentState().getName()
        if self.propId == 9613:
            if stateName == 'playing':
                self.fsm.request('attract')
            return
        if avatarId == self.avatarId and stateName == 'playing':
            self.sendUpdate('avatarExit', [avatarId])
            self.fsm.request('attract')

    def getVideo(self):
        return [self.videoUrl, self.videoTimestamp]

    def requestPlayVideo(self, videoUrl):
        avatarId = self.air.getAvatarIdFromSender()
        if self.propId != 9613 or not isinstance(videoUrl, str) or len(videoUrl) > 512:
            return
        parsed = urlparse(videoUrl.strip())
        host = (parsed.hostname or '').lower()
        videoId = ''
        if host == 'youtu.be':
            videoId = parsed.path.strip('/').split('/')[0]
        elif host in ('youtube.com', 'www.youtube.com', 'm.youtube.com', 'music.youtube.com'):
            if parsed.path == '/watch':
                videoId = parse_qs(parsed.query).get('v', [''])[0]
            elif parsed.path.startswith(('/shorts/', '/embed/', '/live/')):
                parts = parsed.path.strip('/').split('/')
                if len(parts) > 1:
                    videoId = parts[1]
        if not re.fullmatch(r'[A-Za-z0-9_-]{6,20}', videoId):
            return
        videoUrl = 'https://www.youtube.com/watch?v=' + videoId
        if self.fsm.getCurrentState().getName() == 'playing':
            self.fsm.request('attract')
        self.videoUrl = videoUrl
        self.videoTimestamp = globalClockDelta.getRealNetworkTime()
        self.sendUpdate('setVideo', [self.videoUrl, self.videoTimestamp])
        self.fsm.request('playing')

    def requestSeekVideo(self, seconds):
        if self.propId != 9613 or not self.videoUrl or self.fsm.getCurrentState().getName() != 'playing':
            return
        try:
            seconds = max(0, min(65535, int(seconds)))
        except (TypeError, ValueError):
            return
        self.videoTimestamp = globalClockDelta.getRealNetworkTime() - seconds
        self.sendUpdate('setVideo', [self.videoUrl, self.videoTimestamp])

    def getState(self):
        return [self.fsm.getCurrentState().getName(), globalClockDelta.getRealNetworkTime()]

    def d_setState(self, state):
        self.sendUpdate('setState', [state, globalClockDelta.getRealNetworkTime()])

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterAttract(self):
        self.d_setState('attract')

    def exitAttract(self):
        pass

    def enterPlaying(self):
        self.d_setState('playing')

    def exitPlaying(self):
        pass