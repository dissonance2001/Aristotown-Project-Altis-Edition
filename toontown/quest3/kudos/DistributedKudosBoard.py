from direct.gui.OnscreenText import OnscreenText
from panda3d.core import *
from direct.distributed.DistributedObject import DistributedObject
from direct.interval.IntervalGlobal import *

from toontown.effects import DustCloud
from toontown.quest3.base import QuestGlobals
from toontown.quest3.kudos.ExteriorKudosBoardGUI import ExteriorKudosBoardGUI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.toonbase import ToontownGlobals, TTLocalizer, RealmGlobals
from toontown.toon.OneTimeCutsceneGlobals import OneTimeCutscenes as OTC

DefaultPosHpr = (26.003, -43.0, 4.025, 135, 0, 0)
ZoneToPosHpr = {
    ToontownGlobals.ToontownCentral:   (26.003, -43.0, 4.025, 130, 0, 0),
    ToontownGlobals.DonaldsDock:       (23.981, 167.286, 3.280, -52.5, 0, 0),
    ToontownGlobals.YeOlde:      (32.172, 50.55, -7.16, -34, 0, 0.5),
    ToontownGlobals.DaisyGardens:      (-25.0, 90.816, 0.025, -36, 0, 0),
    ToontownGlobals.MinniesMelodyland: (73.85, 35.9, -14.483, -65, 0, 0),
    ToontownGlobals.TheBrrrgh:         (-159.735, -63.769, 6.192, 100, 0, 0),
    ToontownGlobals.OutdoorZone:       (-1.371, -168.688, 0.0, -133, 0, 0),
    ToontownGlobals.DonaldsDreamland:  (-57.4, -31.446, -15.55, 85, 0, -3),
}
ZoneToBoardName = {
    ToontownGlobals.ToontownCentral: 'ttc',
    ToontownGlobals.DonaldsDock: 'bb',
    ToontownGlobals.YeOlde: 'yott',
    ToontownGlobals.DaisyGardens: 'dg',
    ToontownGlobals.MinniesMelodyland: 'mml',
    ToontownGlobals.TheBrrrgh: 'tb',
    ToontownGlobals.OutdoorZone: 'aa',
    ToontownGlobals.DonaldsDreamland: 'ddl',
}
TexPathBase = 'phase_4/maps/kudos/ttcc_ext_{0}_kudosboard.png'

ZoneToStarburstColor = {
    ToontownGlobals.ToontownCentral: (1.0, 1.0, 0.7),
    ToontownGlobals.DonaldsDock: (1.0, 1.0, 0.7),
    ToontownGlobals.YeOlde: (1.0, 1.0, 0.7),
    ToontownGlobals.DaisyGardens: (1.0, 1.0, 0.7),
    ToontownGlobals.MinniesMelodyland: (1.0, 1.0, 0.7),
    ToontownGlobals.TheBrrrgh: (0.7, 0.7, 1.0),
    ToontownGlobals.OutdoorZone: (1.0, 1.0, 0.7),
    ToontownGlobals.DonaldsDreamland: (1.0, 1.0, 0.7),
}

ZoneToUnlockTextColor = {
    ToontownGlobals.ToontownCentral: (1.0, 0.7, 0.7),
    ToontownGlobals.DonaldsDock: (1.0, 1.0, 0.7),
    ToontownGlobals.YeOlde: (1.0, 1.0, 0.7),
    ToontownGlobals.DaisyGardens: (1.0, 1.0, 0.7),
    ToontownGlobals.MinniesMelodyland: (1.0, 1.0, 0.7),
    ToontownGlobals.TheBrrrgh: (0.7, 0.7, 1.0),
    ToontownGlobals.OutdoorZone: (1.0, 1.0, 0.7),
    ToontownGlobals.DonaldsDreamland: (1.0, 1.0, 0.7),
}

ZoneToUnlockCutscene = {
    ToontownGlobals.ToontownCentral:   OTC.KudosUnlock_TTC,
    ToontownGlobals.DonaldsDock:       OTC.KudosUnlock_BB,
    ToontownGlobals.YeOlde:      OTC.KudosUnlock_YOTT,
    ToontownGlobals.DaisyGardens:      OTC.KudosUnlock_DG,
    ToontownGlobals.MinniesMelodyland: OTC.KudosUnlock_MML,
    ToontownGlobals.TheBrrrgh:         OTC.KudosUnlock_TB,
    ToontownGlobals.OutdoorZone:       OTC.KudosUnlock_AA,
    ToontownGlobals.DonaldsDreamland:  OTC.KudosUnlock_DDL,
}

InactiveTipId = 76

# :smirk:
IgnoreFirstTimeCutsceneOnDev = True


@DirectNotifyCategory()
class DistributedKudosBoard(DistributedObject):
    """
    A board in each playground that allows toons to walk up to it and view their kudos tasks.
    """

    def __init__(self, cr):
        super().__init__(cr)
        self.geom = None
        self.gui = None
        self.active = False
        self.firstTimeSeq = None

    def announceGenerate(self):
        super().announceGenerate()
        self.checkActive()
        self.setupModel()
        self.gui = ExteriorKudosBoardGUI(self, zoneId=self.zoneId)
        self.gui.hide()

    @property
    def cutsceneId(self):
        return ZoneToUnlockCutscene.get(self.zoneId, OTC.KudosUnlock_TTC)

    @property
    def posHpr(self):
        return ZoneToPosHpr.get(self.zoneId, DefaultPosHpr)

    @property
    def starburstColor(self):
        return ZoneToStarburstColor.get(self.zoneId, (1, 1, 1))

    @property
    def unlockTextColor(self):
        return ZoneToUnlockTextColor.get(self.zoneId, (1, 1, 0.7))

    def checkActive(self):
        # Is the board active for this toon?
        # If inactive, they won't be able to properly interact with it and it will
        # Have tape over it to show that it is inactive.
        questHistoryReq = QuestGlobals.QuestHistoryForPlaygroundCompletion.get(self.zoneId)
        self.active = base.localAvatar.hasCompletedQuestHistory(questHistoryReq)

        if RealmGlobals.getCurrentRealm() == RealmGlobals.Realm.Development and IgnoreFirstTimeCutsceneOnDev:
            return

        # If the board is determined to be active and we haven't seen the first-time cutscene,
        # pause the toon and give them a little cutscene showing that the board has become active.
        if self.active and not base.localAvatar.hasSeenCutscene(self.cutsceneId):
            # Mark active as false so that the board stays "disabled" until the cutscene.
            self.active = False
            # Once the toon enters walk, show them the cutscene.
            self.acceptOnce('Playground-enterWalk', self.__delayFirstTimeCutscene)

    def setupModel(self):
        self.geom = loader.loadModel('phase_4/models/props/ttcc_ext_kudosboard')

        # Apply their position
        self.geom.setPosHpr(*self.posHpr)

        # Make a node for the opposite side of the board
        self.geomOtherSide = self.geom.attachNewNode('otherSide')
        self.geomOtherSide.setH(180)

        # Show the proper node for this active mode
        self.setActiveMode()

        # Find and apply our playground-specific kudos board texture
        texExtension = ZoneToBoardName.get(self.zoneId, 'gen')
        texture = loader.loadTexture(TexPathBase.format(texExtension))
        texture.setMinfilter(Texture.FTLinearMipmapLinear)
        texture.setMagfilter(Texture.FTLinear)
        self.geom.find('**/board').setTexture(texture, 1)

        newsManager = base.cr.newsManager
        if newsManager:
            holidayId = base.cr.newsManager.getDecorationHolidayId()
            if holidayId == ToontownGlobals.HALLOWEEN and base.cr.playGame.hood.spookySkyFile:
                self.geom.setColorScale(0.55, 0.55, 0.65, 1.0)
        self.geom.reparentTo(render)
        self.initCollisions()

    def setActiveMode(self):
        # Hide and show the proper nodes based on whether the board is "active"
        # and available to the local toon.
        activatedNode = self.geom.find('**/activated')
        deactivatedNode = self.geom.find('**/deactivated')
        wantedNode = activatedNode if self.active else deactivatedNode
        unwantedNode = deactivatedNode if self.active else activatedNode
        wantedNode.show()
        unwantedNode.hide()

    def __delayFirstTimeCutscene(self):
        self.doMethodLater(0, self.__handleFirstTimeCutscene, extraArgs=[], priority=-60, name=self.uniqueName('delay-first-time-cutscene'))

    def __handleFirstTimeCutscene(self):
        # Tell the server we've now seen this cutscene
        base.localAvatar.requestAddSeenCutscene(self.cutsceneId)

        camParent = camera.getParent()
        camPos = camera.getPos()
        camHpr = camera.getHpr()

        # Make a dustcloud for it
        dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
        dustCloud.setBillboardAxis(2.0)
        dustCloud.setZ(3)
        dustCloud.setScale(1.9)
        dustCloud.setBin('fixed', 110)
        dustCloud.createTrack()

        # Get the local toon into the correct state
        place = base.cr.playGame.getPlace()
        place.setState('Stopped')

        base.localAvatar.cameraFSM.request('Off')
        base.camera.wrtReparentTo(render)

        def updateActive():
            self.active = True
            self.setActiveMode()

        boardTrack = Sequence(
            Func(base.transitions.fadeOut, 1.1),
            Wait(1.11),
            Func(base.camera.reparentTo, self.geom),
            Func(base.camera.setPosHpr, 0, -16, 6, 0, 0, 0),
            Wait(0.25),
            Func(base.transitions.fadeIn, 0.9),
            Wait(1.8),
            Func(dustCloud.reparentTo, self.geom),
            Parallel(
                dustCloud.track,
                Sequence(
                    Wait(0.4),
                    Func(updateActive)
                )
            ),
            Func(dustCloud.destroy),
            Wait(2.0),
            Func(base.transitions.fadeOut, 1.1),
            Wait(1.11),
            Func(base.camera.reparentTo, camParent),
            Func(base.camera.setPosHpr, *camPos, *camHpr),
            Wait(0.25),
            Func(base.transitions.fadeIn, 0.9),
            Wait(0.9),
            Func(base.localAvatar.cameraFSM.request, 'Orbit'),
            Func(place.setState, 'walk')
        )

        drumroll = loader.loadSfx('phase_5/audio/sfx/SZ_MM_drumroll.ogg')
        fanfare = loader.loadSfx('phase_5/audio/sfx/SZ_MM_fanfare.ogg')

        sfxSeq = Sequence(
            Wait(2.2),
            SoundInterval(drumroll),
            SoundInterval(fanfare)
        )

        boardNode = self.geom.find('**/board')
        activatedNode = self.geom.find('**/activated')
        starburst = loader.loadModel('phase_3.5/models/props/ttcc_gen_starburst')
        starburst.setScale(4.5)
        starburst.setPos(self.geom, 0, 1.0, 4)
        starburst.setColorScale(*self.starburstColor, 0)
        starburst.setHpr(self.geom, 0, 0, 0)
        starburst.reparentTo(render)

        starburstSeq = Sequence(
            Wait(3.5),
            Func(base.camera.wrtReparentTo, render),
            Func(boardNode.setBin, 'fixed', 95),
            Func(activatedNode.setBin, 'fixed', 100),
            Func(starburst.setBin, 'fixed', 105),
            Parallel(
                LerpHprInterval(starburst, 2.5, (self.geom.getH(), 0, 360)),
                Sequence(
                    LerpColorScaleInterval(starburst, 0.5, (*self.starburstColor, 0.6)),
                    Wait(1.5),
                    LerpColorScaleInterval(starburst, 0.5, (*self.starburstColor, 0))
                )
            ),
            Func(boardNode.clearBin),
            Func(activatedNode.clearBin),
            Func(starburst.removeNode)
        )

        unlockText = OnscreenText(TTLocalizer.KudosBoardUnlocked,
                                  parent=aspect2d,
                                  font=ToontownGlobals.getSignFont(),
                                  scale=0.13,
                                  fg=(*self.unlockTextColor, 1.0),
                                  pos=(0, -0.875))
        unlockText.setColorScale(1, 1, 1, 0)

        textTrack = Sequence(
            Wait(3.5),
            LerpColorScaleInterval(unlockText, 0.5, (1, 1, 1, 1)),
            Wait(1.5),
            LerpColorScaleInterval(unlockText, 0.5, (1, 1, 1, 0)),
            Func(unlockText.destroy)
        )

        self.firstTimeSeq = Parallel(boardTrack, starburstSeq, textTrack, sfxSeq)
        self.firstTimeSeq.play()

    def disable(self):
        self.removeAllTasks()
        self.ignoreAll()
        self.cleanupCollisions()
        if self.firstTimeSeq:
            self.firstTimeSeq.finish()
            self.firstTimeSeq = None
        if self.geom:
            self.geom.removeNode()
            self.geom = None
        if self.gui:
            self.gui.destroy()
            self.gui = None

    """
    Collision management
    """

    def initCollisions(self):
        self.cSphere = CollisionTube(0.0, 1.0, 0.0, 0.0, 1.0, 5.0, 3.25)
        self.cSphere.setTangible(0)
        self.cSphereNode = CollisionNode('KudosBoardcSphereNode')
        self.cSphereNode.addSolid(self.cSphere)
        self.cSphereNodePath = self.geom.attachNewNode(self.cSphereNode)
        self.cSphereNodePath.hide()
        self.cSphereNodePath.setPos(0, -2, 0)
        self.cSphereNodePath.setScale(0.8, 0.4, 1.0)
        self.cSphereNode.setCollideMask(ToontownGlobals.WallBitmask)
        self.accept('enter' + self.cSphereNode.getName(), self.onCollision)

    def cleanupCollisions(self):
        del self.cSphere
        del self.cSphereNode
        self.cSphereNodePath.removeNode()
        del self.cSphereNodePath

    def onCollision(self, _=None):
        if settings['interactkey']:
            self.accept('exit' + self.cSphereNode.getName(), self.handleCollisionSphereExit)
            self.accept('teleportBegin', self.handleCollisionSphereExit)
            self.accept(base.INTERACT, self.activate)
            if hasattr(self, "name"):
                text = ("Press " + str(base.INTERACT).upper() + " to interact with %s" %self.getName())
            else:
                text = "Press " + str(base.INTERACT).upper() + " to interact"

            self.enterText = OnscreenText(
                text = text,
                style = 3,
                scale = .09,
                parent = base.a2dBottomCenter,
                fg = (1, 0.9, 0.1, 1),
                pos = (0.0, 0.5)
            )
            self.enterText.setColorScale(1, 1, 1, 0)
            self.colorSeq = Sequence(
                LerpColorScaleInterval(self.enterText, .8, VBase4(1, 1, 1, 1)),
                LerpColorScaleInterval(self.enterText, .8, VBase4(.5, .6, 1, .9))).loop()
        else:
            self.activate()

    def activate(self):
        if settings['interactkey']:
            self.handleCollisionSphereExit()
        if self.active:
            self.openGui()
        elif InactiveTipId not in base.localAvatar.toonTipsSeen:
            base.localAvatar.sendUpdate('requestToonTip', [InactiveTipId])

    def handleCollisionSphereExit(self, collEntry=None):
        self.ignore('exit' + self.cSphereNode.getName())
        self.ignore('teleportBegin')
        self.ignore(base.INTERACT)
        if hasattr(self, "colorSeq"):
            if self.colorSeq:
                self.colorSeq.finish()
                self.colorSeq = None
        if hasattr(self, "enterText"):
            self.enterText.removeNode()
            del self.enterText

    """
    GUI handling
    """

    transitionLength = 1.0
    guiUseTime = 120

    def openGui(self):
        base.cr.playGame.getPlace().setState('Stopped')
        base.localAvatar.lockControlsForEntry()
        camera.posQuatInterval(
            self.transitionLength,
            Vec3(-5, 9, 4.5), Vec3(-150, -2, 0),
            other=self.geomOtherSide, blendType='easeOut',
            name=self.uniqueName('lerpCamera')
        ).start()
        taskMgr.doMethodLater(self.transitionLength, self.__createGui, self.uniqueName('openBoardGUI'))
        taskMgr.doMethodLater(self.guiUseTime, self.closeGui, self.uniqueName('boardAntisleep'))

    def __createGui(self, task=None):
        self.gui.show()
        self.gui.performInitSequence()
        self.acceptOnce('escape', self.closeGui)
        if task is not None:
            return task.done

    def closeGui(self, task=None):
        base.cr.playGame.getPlace().setState('Walk')
        base.localAvatar.unlockControlsForEntry()
        self.ignore('escape')
        self.gui.hide()
        taskMgr.remove(self.uniqueName('boardAntisleep'))
        if task is not None:
            return task.done

    def chooseKudosQuest(self, questId):
        self.sendUpdate('chooseKudosQuest', [questId])
