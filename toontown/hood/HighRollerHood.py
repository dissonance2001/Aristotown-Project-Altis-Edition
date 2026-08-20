from __future__ import absolute_import
from direct.fsm import ClassicFSM, State
from toontown.hood.Hood import Hood
from toontown.toonbase import ToontownGlobals
from toontown.coghq import HighRollerHQLoader


class HighRollerHood(Hood):
    notify = directNotify.newCategory('HighRollerHood')

    ID = ToontownGlobals.HighRollerHQ
    SKY_FILE = 'phase_3.5/models/props/TT_sky'
    TITLE_COLOR = (0.55, 0.85, 1.0, 1.0)

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        Hood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.fsm = ClassicFSM.ClassicFSM(
            'HighRollerHood',
            [State.State('start', self.enterStart, self.exitStart,
                         ['highRollerLoader']),
             State.State('highRollerLoader',
                         self.enterHighRollerLoader,
                         self.exitHighRollerLoader,
                         ['quietZone']),
             State.State('quietZone', self.enterQuietZone,
                         self.exitQuietZone, ['highRollerLoader']),
             State.State('final', self.enterFinal, self.exitFinal, [])],
            'start', 'final')
        self.fsm.enterInitialState()
        self.id = self.ID
        self.storageDNAFile = None
        self.skyFile = self.SKY_FILE
        self.titleColor = self.TITLE_COLOR

    def load(self):
        Hood.load(self)
        self.parentFSM.getStateNamed('HighRollerHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('HighRollerHood').removeChild(self.fsm)
        Hood.unload(self)

    def getHoodText(self, zoneId):
        return 'The High Roller'

    def spawnTitleText(self, zoneId):
        self.doSpawnTitleText('The High Roller')

    def loadLoader(self, requestStatus):
        if requestStatus['loader'] != 'highRollerLoader':
            self.notify.error('Unknown High Roller loader: %s' %
                              requestStatus['loader'])
            return
        self.loader = HighRollerHQLoader.HighRollerHQLoader(
            self, self.fsm.getStateNamed('highRollerLoader'),
            self.loaderDoneEvent)
        self.loader.load(requestStatus['zoneId'])

    def enterHighRollerLoader(self, requestStatus):
        self.accept(self.loaderDoneEvent, self.handleHighRollerLoaderDone)
        self.loader.enter(requestStatus)

    def exitHighRollerLoader(self):
        self.ignore(self.loaderDoneEvent)
        self.loader.exit()
        self.loader.unload()
        del self.loader

    def handleHighRollerLoaderDone(self):
        doneStatus = self.loader.getDoneStatus()
        if self.isSameHood(doneStatus):
            self.fsm.request('quietZone', [doneStatus])
        else:
            self.doneStatus = doneStatus
            messenger.send(self.doneEvent)

    def handleWaitForSetZoneResponse(self, requestStatus):
        # Supports a reload inside the same dynamic encounter without falling
        # back to Hood's safe-zone/town/cog-HQ loader switch.
        if requestStatus.get('loader') == 'highRollerLoader' and not hasattr(self, 'loader'):
            self.loadLoader(requestStatus)

    def enter(self, requestStatus):
        Hood.enter(self, requestStatus)
        base.localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        base.camLens.setNearFar(ToontownGlobals.DefaultCameraNear,
                               ToontownGlobals.DefaultCameraFar)

    def exit(self):
        base.localAvatar.setCameraFov(settings['fieldofview'])
        base.camLens.setNearFar(ToontownGlobals.DefaultCameraNear,
                               ToontownGlobals.DefaultCameraFar)
        Hood.exit(self)
