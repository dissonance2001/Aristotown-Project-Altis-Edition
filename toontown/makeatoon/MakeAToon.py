from direct.actor.Actor import Actor
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.fsm import StateData
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.task import Task
from panda3d.core import *
import random
import builtins
from toontown.makeatoon import BodyShop
from toontown.makeatoon import ColorShop
from toontown.makeatoon import StartShop
from toontown.makeatoon import StatusShop
from .MakeAToonGlobals import *
from toontown.makeatoon import MakeClothesGUI
from toontown.makeatoon import NameShop
from otp import *
from toontown.toon import Toon
from toontown.toon import ToonDNA
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.gui.TTGui import ScalingButton
from toontown.toonbase.ToontownGlobals import toonBodyScales
from decimal import Decimal

from ..utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.toon.ToonDNA import ClothesColors
from toontown.chat.constants.ChatGlobals import CFSpeech, CFTimeout

CAM_ZOOM_DUR = 0.2


@DirectNotifyCategory()
class MakeAToon(StateData.StateData):
    def __init__(self, parentFSM, avList, doneEvent, index):
        StateData.StateData.__init__(self, doneEvent)
        self.phase = 3
        self.names = ['',
         '',
         '',
         '']
        self.dnastring = None
        self.dna = None
        self.progressing = 0
        self.toonPosition = Point3(-1.62, -3.49, 0)
        self.toonScale = Point3(1, 1, 1)
        self.toonHpr = Point3(180, 0, 0)
        self.leftTime = 1.6
        self.rightTime = 1
        self.slide = 0
        self.nameList = []
        self.warp = 0
        self.zoomRatio = 1
        for av in avList:
            if av.position == index:
                self.warp = 1
                self.namelessPotAv = av
            self.nameList.append(av.name)

        self.fsm = ClassicFSM.ClassicFSM('MakeAToon', [
         State.State('Init', self.enterInit, self.exitInit, ['BodyShop', 'NameShop']),
         State.State('BodyShop', self.enterBodyShop, self.exitBodyShop, ['ColorShop']),
         State.State('ColorShop', self.enterColorShop, self.exitColorShop, ['BodyShop', 'ClothesShop']),
         State.State('ClothesShop', self.enterClothesShop, self.exitClothesShop, ['ColorShop', 'StatusShop']),
         State.State('StatusShop', self.enterStatusShop, self.exitStatusShop, ['ClothesShop', 'NameShop']),
         State.State('NameShop', self.enterNameShop, self.exitNameShop, ['StatusShop', 'StartShop']),
         State.State('StartShop', self.enterStartShop, self.exitStartShop, ['NameShop']),
         State.State('Done', self.enterDone, self.exitDone, [])], 'Init', 'Done')
        self.parentFSM = parentFSM
        self.parentFSM.getStateNamed('createAvatar').addChild(self.fsm)
        self.bs = BodyShop.BodyShop(self, 'BodyShop-done')
        self.cos = ColorShop.ColorShop('ColorShop-done')
        self.cls = MakeClothesGUI.MakeClothesGUI('ClothesShop-done')
        self.ns = NameShop.NameShop(self, 'NameShop-done', avList, index)
        self.sts = StartShop.StartShop('StartShop-done', avList, index)
        self.ss = StatusShop.StatusShop('StatusShop-done')

        self.shop = BODYSHOP
        self.shopsVisited = []
        if self.warp:
            self.shopsVisited = [GENDERSHOP,
             BODYSHOP,
             COLORSHOP,
             CLOTHESSHOP,
             STATUSSHOP,
             STARTSHOP]
        self.soundBack = None
        self.music = None
        self.fsm.enterInitialState()
        self.hprDelta = -1
        self.dropIval = None
        self.roomSquishIval = None
        self.propSquishIval = None
        self.focusOutIval = None
        self.focusInIval = None
        self.toon = None
        self.defaultH = 180
        self.canZoom = False
        self.lastRot = self.defaultH
        self.toonRotateSlider = None
        self.zoomSeq = None

    def getToon(self):
        return self.toon

    def enter(self):
        self.notify.info('Starting Make A Toon.')
        if ConfigVariableBool('want-qa-regression', False).getValue():
            self.notify.info('QA-REGRESSION: MAKEATOON: Starting Make A Toon')
        base.camLens.setMinFov(ToontownGlobals.MakeAToonCameraFov/(4./3.))
        base.playMusic(self.music, looping=1, volume=self.musicVolume)
        camera.setPosHpr(-5.7, -12.3501, 2.15, -24.8499, 2.73, 0)
        if self.warp:
            if self.toon.style.torso[1] == 's':
                self.toon.gender = 's'
            else:
                self.toon.gender = 'd'
            self.toon.reparentTo(render)
            self.toon.loop('neutral')
            self.toon.setPosHpr(-4.1, -2, 0, 200, 0, 0)
        self.guiTopBar.show()
        self.guiBottomBar.show()
        self.guiCancelButton.show()
        self.accept('wheel_up', self.cameraZoomIn)
        self.accept('wheel_down', self.cameraZoomOut)
        if self.warp:
            self.progressing = 0
            self.guiLastButton.hide()
            self.fsm.request('NameShop')
        else:
            self.fsm.request('BodyShop')

    def exit(self):
        if self.zoomSeq:
            self.zoomSeq.finish()
            self.zoomSeq = None
        base.camLens.setMinFov(builtins.settings['fieldofview']/(4./3.))
        self.guiTopBar.hide()
        self.guiBottomBar.hide()
        if self.music:
            self.music.stop()
        self.fsm.request('Done')
        self.room.reparentTo(hidden)
        self.ignore('wheel_up')
        self.ignore('wheel_down')

    def heightZoomRatio(self, height):
        toon = self.getToon()
        if toon:
            speciesName = ToonDNA.getSpeciesName(toon.style.head)
        else:
            speciesName = 'cat'  # Average body height
        return height * (toonBodyScales[speciesName] - (self.zoomRatio))

    def moveCamera(self):
        toon = self.getToon()
        if self.zoomSeq:
            self.zoomSeq.pause()

        self.zoomSeq = Parallel()
        b = 'easeInOut'
        if toon:
            height = toon.getHeight()
            camVal = max(2.15 + self.heightZoomRatio(height), 2.15)
            self.zoomSeq.append(LerpFunctionInterval(camera.setZ, fromData=camera.getZ(), toData=camVal, duration=CAM_ZOOM_DUR, blendType=b))
            if self.spotlightActor:
                spotlightVal = max(self.heightZoomRatio(height), 0)
                self.zoomSeq.append(LerpFunctionInterval(self.spotlightActor.setZ, fromData=self.spotlightActor.getZ(), toData=spotlightVal, duration=CAM_ZOOM_DUR, blendType=b))
        camLensVal = (ToontownGlobals.MakeAToonCameraFov/(4./3.)) * self.zoomRatio
        self.zoomSeq.append(LerpFunctionInterval(base.camLens.setMinFov, fromData=base.camLens.getMinFov(), toData=camLensVal, duration=CAM_ZOOM_DUR, blendType=b))
        self.zoomSeq.start()

    def cameraZoomIn(self):
        if self.canZoom:
            self.zoomRatio -= 0.1
            if self.zoomRatio < 0.5:
                self.zoomRatio = 0.5
            self.moveCamera()

    def cameraZoomOut(self):
        if self.canZoom:
            self.zoomRatio += 0.1
            if self.zoomRatio > 1:
                self.zoomRatio = 1
            self.moveCamera()

    def cameraReset(self):
        if self.zoomSeq:
            self.zoomSeq.pause()

        zoomDuration = CAM_ZOOM_DUR * 2.5
        b = 'easeInOut'
        self.zoomSeq = Parallel()
        camLensVal = (ToontownGlobals.MakeAToonCameraFov/(4./3.))
        self.zoomSeq.append(LerpFunctionInterval(base.camLens.setMinFov, fromData=base.camLens.getMinFov(), toData=camLensVal, duration=zoomDuration, blendType=b))
        self.zoomSeq.append(LerpFunctionInterval(camera.setZ, fromData=camera.getZ(), toData=2.15, duration=zoomDuration, blendType=b))
        if self.spotlightActor:
            self.zoomSeq.append(LerpFunctionInterval(self.spotlightActor.setZ, fromData=self.spotlightActor.getZ(), toData=0, duration=zoomDuration, blendType=b))
        self.zoomSeq.start()

    def load(self):
        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')
        gui.flattenMedium()
        guiAcceptUp = gui.find('**/tt_t_gui_mat_okUp')
        guiAcceptUp.flattenStrong()
        guiAcceptDown = gui.find('**/tt_t_gui_mat_okDown')
        guiAcceptDown.flattenStrong()
        guiCancelUp = gui.find('**/tt_t_gui_mat_closeUp')
        guiCancelUp.flattenStrong()
        guiCancelDown = gui.find('**/tt_t_gui_mat_closeDown')
        guiCancelDown.flattenStrong()
        guiNextUp = gui.find('**/tt_t_gui_mat_nextUp')
        guiNextUp.flattenStrong()
        guiNextDown = gui.find('**/tt_t_gui_mat_nextDown')
        guiNextDown.flattenStrong()
        guiNextDisabled = gui.find('**/tt_t_gui_mat_nextDisabled')
        guiNextDisabled.flattenStrong()
        skipTutorialUp = gui.find('**/tt_t_gui_mat_skipUp')
        skipTutorialUp.flattenStrong()
        skipTutorialDown = gui.find('**/tt_t_gui_mat_skipDown')
        skipTutorialDown.flattenStrong()
        rotateUp = gui.find('**/tt_t_gui_mat_arrowRotateUp')
        rotateUp.flattenStrong()
        rotateDown = gui.find('**/tt_t_gui_mat_arrowRotateDown')
        rotateDown.flattenStrong()
        self.guiTopBar = DirectFrame(relief=None, text=TTLocalizer.CreateYourToon, text_font=ToontownGlobals.getSignFont(),
            text_fg=(0.0, 0.65, 0.35, 1), text_scale=0.18, text_pos=(0, -0.03), pos=(0, 0, 0.86))
        self.guiTopBar.hide()
        self.guiBottomBar = DirectFrame(relief=None, image_scale=(1.25, 1, 1), pos=(0.01, 0, -0.86))
        self.guiBottomBar.hide()
        self.guiCheckButton = ScalingButton(parent=self.guiBottomBar, relief=None, image=(guiAcceptUp,
            guiAcceptDown,
            guiAcceptUp,
            guiAcceptDown), image_scale=halfButtonScale, image1_scale=halfButtonScale, image2_scale=halfButtonScale,
            pos=(1.165, 0, -0.018), command=self.__handleNext, text=('', TTLocalizer.MakeAToonDone, TTLocalizer.MakeAToonDone, ''),
            text_font=ToontownGlobals.getInterfaceFont(), text_scale=0.08, text_align=TextNode.ARight, text_pos=(0.075, 0.13),
            text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1))
        self.guiCheckButton.setPos(-0.13, 0, 0.13)
        self.guiCheckButton.reparentTo(base.a2dBottomRight)
        self.guiCheckButton['state'] = DGG.NORMAL
        self.guiCheckButton.hide()
        self.guiCancelButton = ScalingButton(parent=self.guiBottomBar, relief=None, image=(guiCancelUp,
            guiCancelDown,
            guiCancelUp,
            guiCancelDown), image_scale=halfButtonScale, image1_scale=halfButtonScale, image2_scale=halfButtonScale,
            pos=(-1.179, 0, -0.011), command=self.__handleCancel, text=('', TTLocalizer.MakeAToonCancel, TTLocalizer.MakeAToonCancel),
            text_font=ToontownGlobals.getInterfaceFont(), text_scale=TTLocalizer.MATguiCancelButton, text_pos=(0, 0.115),
            text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1))
        self.guiCancelButton.setPos(0.13, 0, 0.13)
        self.guiCancelButton.reparentTo(base.a2dBottomLeft)
        self.guiCancelButton.hide()
        self.guiNextButton = ScalingButton(parent=self.guiBottomBar, relief=None, image=(guiNextUp,
            guiNextDown,
            guiNextUp,
            guiNextDisabled), image_scale=(0.3, 0.3, 0.3), image1_scale=(0.3, 0.3, 0.3), image2_scale=(0.3, 0.3, 0.3), pos=(1.165, 0, -0.018), command=self.__handleNext, text=('',
            TTLocalizer.MakeAToonNext,
            TTLocalizer.MakeAToonNext,
            ''), text_font=ToontownGlobals.getInterfaceFont(), text_scale=TTLocalizer.MATguiNextButton, text_pos=(0, 0.115), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1))
        self.guiNextButton.setPos(-0.13, 0, 0.13)
        self.guiNextButton.reparentTo(base.a2dBottomRight)
        self.guiNextButton.hide()
        self.guiLastButton = ScalingButton(parent=self.guiBottomBar, relief=None, image=(guiNextUp,
            guiNextDown,
            guiNextUp,
            guiNextDown), image3_color=Vec4(0.5, 0.5, 0.5, 0.75), image_scale=(-0.3, 0.3, 0.3), image1_scale=(-0.3, 0.3, 0.3),
            image2_scale=(-0.3, 0.3, 0.3), pos=(0.825, 0, -0.018), command=self.__handleLast, text=('',
            TTLocalizer.MakeAToonLast,
            TTLocalizer.MakeAToonLast,
            ''), text_font=ToontownGlobals.getInterfaceFont(), text_scale=0.08, text_pos=(0, 0.115), text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1))
        self.guiLastButton.setPos(-0.37, 0, 0.13)
        self.guiLastButton.reparentTo(base.a2dBottomRight)
        self.guiLastButton.hide()
        self.rotateLeftButton = DirectButton(parent=self.guiBottomBar, relief=None, image=(rotateUp,
            rotateDown,
            rotateUp,
            rotateDown), image_scale=(-0.4, 0.4, 0.4), image1_scale=(-0.5, 0.5, 0.5), image2_scale=(-0.5, 0.5, 0.5),
            pos=(-0.355, 0, 0.36))
        self.rotateLeftButton.flattenMedium()
        self.rotateLeftButton.reparentTo(base.a2dBottomCenter)
        self.rotateLeftButton.hide()
        self.rotateLeftButton.bind(DGG.B1PRESS, self.rotateToonLeft)
        self.rotateLeftButton.bind(DGG.B1RELEASE, self.stopToonRotateLeftTask)
        self.rotateRightButton = DirectButton(parent=self.guiBottomBar, relief=None, image=(rotateUp,
         rotateDown,
         rotateUp,
         rotateDown), image_scale=(0.4, 0.4, 0.4), image1_scale=(0.5, 0.5, 0.5), image2_scale=(0.5, 0.5, 0.5), pos=(0.355, 0, 0.36))
        self.rotateRightButton.flattenStrong()
        self.rotateRightButton.reparentTo(base.a2dBottomCenter)
        self.rotateRightButton.hide()
        self.rotateRightButton.bind(DGG.B1PRESS, self.rotateToonRight)
        self.rotateRightButton.bind(DGG.B1RELEASE, self.stopToonRotateRightTask)
        gui.removeNode()
        self.roomDropActor = Actor()
        self.roomDropActor.loadModel('phase_3/models/makeatoon/roomAnim_model')
        self.roomDropActor.loadAnims({'drop': 'phase_3/models/makeatoon/roomAnim_roomDrop'})
        self.roomDropActor.reparentTo(render)
        self.roomDropActor.setBlend(frameBlend = base.wantSmoothAnims)
        # Set this here to stop the camera from trying to cull the actor when close up.
        self.roomDropActor.node().setBounds(OmniBoundingVolume())
        self.roomDropActor.node().setFinal(True)
        self.dropJoint = self.roomDropActor.find('**/droppingJoint')
        self.roomSquishActor = Actor()
        self.roomSquishActor.loadModel('phase_3/models/makeatoon/roomAnim_model')
        self.roomSquishActor.loadAnims({'squish': 'phase_3/models/makeatoon/roomAnim_roomSquish'})
        self.roomSquishActor.reparentTo(render)
        self.roomSquishActor.setBlend(frameBlend = base.wantSmoothAnims)
        self.squishJoint = self.roomSquishActor.find('**/scalingJoint')
        self.propSquishActor = Actor()
        self.propSquishActor.loadModel('phase_3/models/makeatoon/roomAnim_model')
        self.propSquishActor.loadAnims({'propSquish': 'phase_3/models/makeatoon/roomAnim_propSquish'})
        self.propSquishActor.reparentTo(render)
        self.propSquishActor.pose('propSquish', 0)
        self.propSquishActor.setBlend(frameBlend = base.wantSmoothAnims)
        self.propJoint = self.propSquishActor.find('**/propJoint')
        self.spotlightActor = Actor()
        self.spotlightActor.loadModel('phase_3/models/makeatoon/roomAnim_model')
        self.spotlightActor.loadAnims({'spotlightShake': 'phase_3/models/makeatoon/roomAnim_spotlightShake'})
        self.spotlightActor.reparentTo(render)
        self.spotlightActor.setBlend(frameBlend = base.wantSmoothAnims)
        self.spotlightJoint = self.spotlightActor.find('**/spotlightJoint')
        ee = DirectFrame(pos=(-1, 1, 1), frameSize=(-.01, 0.01, -.01, 0.01), frameColor=(0, 0, 0, 0.05), state='normal')
        ee.bind(DGG.B1PRESS, lambda x, ee = ee: self.toggleSlide())
        self.eee = ee
        self.room = loader.loadModel('phase_3/models/makeatoon/tt_m_ara_mat_room')
        self.room.flattenMedium()

        self.bodyWalls = self.room.find('**/bodyWalls')
        self.bodyWalls.flattenStrong()
        self.bodyProps = self.room.find('**/bodyProps')
        self.bodyProps.flattenStrong()

        self.colorWalls = self.room.find('**/colorWalls')
        self.colorWalls.flattenStrong()
        self.colorProps = self.room.find('**/colorProps')
        self.colorProps.flattenStrong()

        self.clothesWalls = self.room.find('**/clothWalls')
        self.clothesWalls.flattenStrong()
        self.clothesProps = self.room.find('**/clothProps')
        self.clothesProps.flattenStrong()

        # GenderShop is no longer a step in this flow, so its room nodes are
        # otherwise unused; StatusShop and StartShop borrow them.
        self.statusWalls = self.room.find('**/genderWalls')
        self.statusWalls.flattenStrong()
        self.statusProps = self.room.find('**/genderProps')
        self.statusProps.flattenStrong()

        self.startWalls = self.statusWalls
        self.startProps = self.statusProps

        self.nameWalls = self.room.find('**/nameWalls')
        self.nameWalls.flattenStrong()
        self.nameProps = self.room.find('**/nameProps')
        self.nameProps.flattenStrong()

        self.floor = self.room.find('**/floor')
        self.floor.reparentTo(render)

        self.spotlight = self.room.find('**/spotlight')
        self.spotlight.reparentTo(self.spotlightJoint)
        self.spotlight.setColor(1, 1, 1, 0.3)
        self.spotlight.setPos(1.18, -1.27, 0.41)
        self.spotlight.setScale(2.6)
        self.spotlight.setHpr(0, 0, 0)
        smokeSeqNode = SequenceNode('smoke')
        smokeModel = loader.loadModel('phase_3/models/makeatoon/tt_m_ara_mat_smoke')
        smokeFrameList = list(smokeModel.findAllMatches('**/smoke_*'))
        smokeFrameList.reverse()
        for smokeFrame in smokeFrameList:
            smokeSeqNode.addChild(smokeFrame.node())

        smokeSeqNode.setFrameRate(12)
        self.smoke = render.attachNewNode(smokeSeqNode)
        self.smoke.setScale(1, 1, 0.75)
        self.smoke.hide()
        if self.warp:
            self.dna = ToonDNA.ToonDNA()
            self.dna.makeFromNetString(self.namelessPotAv.dna)
            self.toon = Toon.Toon()
            self.toon.setDNA(self.dna)
            self.toon.setNameVisible(0)
            self.toon.startBlink()
            self.toon.startLookAround()
        # self.gs.load()
        self.bs.load()
        self.cos.load()
        self.cls.load()
        self.sts.load()
        self.ss.load()
        self.ns.load()
        self.music = base.loader.loadMusic('phase_3/audio/bgm/create_a_toon.ogg')
        self.musicVolume = ConfigVariableDouble('makeatoon-music-volume', 1).getValue()
        self.sfxVolume = ConfigVariableInt('makeatoon-sfx-volume', 1).getValue()
        self.soundBack = base.loader.loadSfx('phase_3/audio/sfx/GUI_create_toon_back.ogg')
        self.crashSounds = list(map(base.loader.loadSfx, ['phase_3/audio/sfx/tt_s_ara_mat_crash_boing.ogg',
                                              'phase_3/audio/sfx/tt_s_ara_mat_crash_glassBoing.ogg',
                                              'phase_3/audio/sfx/tt_s_ara_mat_crash_wood.ogg',
                                              'phase_3/audio/sfx/tt_s_ara_mat_crash_woodBoing.ogg',
                                              'phase_3/audio/sfx/tt_s_ara_mat_crash_woodGlass.ogg']))

    def unload(self):
        self.exit()
        if self.toon:
            self.toon.stopBlink()
            self.toon.stopLookAroundNow()
        # self.gs.unload()
        if self.music:
            self.music.stop()
            self.music = None
        self.bs.unload()
        self.cos.unload()
        self.cls.unload()
        self.sts.unload()
        self.ss.unload()
        self.ns.unload()
        # del self.gs
        del self.bs
        del self.cos
        del self.cls
        del self.sts
        del self.ss
        del self.ns
        self.guiTopBar.destroy()
        self.guiBottomBar.destroy()
        self.guiCancelButton.destroy()
        self.guiCheckButton.destroy()
        self.eee.destroy()
        self.guiNextButton.destroy()
        self.guiLastButton.destroy()
        if self.toonRotateSlider is not None:
            self.toonRotateSlider.destroy()
        del self.guiTopBar
        del self.guiBottomBar
        del self.guiCancelButton
        del self.guiCheckButton
        del self.eee
        del self.guiNextButton
        del self.guiLastButton
        del self.toonRotateSlider
        del self.rotateLeftButton
        del self.rotateRightButton
        del self.names
        del self.dnastring
        del self.nameList
        del self.soundBack
        del self.dna
        if self.toon:
            self.toon.delete()
        del self.toon
        self.cleanupDropIval()
        self.cleanupRoomSquishIval()
        self.cleanupPropSquishIval()
        self.cleanupFocusInIval()
        self.cleanupFocusOutIval()
        self.room.removeNode()
        del self.room
        # self.room.removeNode() above already recursively destroyed everything
        # found under it (bodyWalls/bodyProps .. smoke are all self.room.find()
        # results) -- calling removeNode() on them again operates on an
        # already-destroyed node and crashes, so just drop the references.
        del self.bodyWalls
        del self.bodyProps
        del self.colorWalls
        del self.colorProps
        del self.clothesWalls
        del self.clothesProps
        del self.statusWalls
        del self.statusProps
        del self.startWalls
        del self.startProps
        del self.nameWalls
        del self.nameProps
        del self.floor
        del self.spotlight
        del self.smoke
        while len(self.crashSounds):
            del self.crashSounds[0]

        self.parentFSM.getStateNamed('createAvatar').removeChild(self.fsm)
        del self.parentFSM
        del self.fsm
        self.ignoreAll()
        loader.unloadModel('phase_3/models/gui/create_a_toon_gui')
        loader.unloadModel('phase_3/models/gui/create_a_toon')
        ModelPool.garbageCollect()
        TexturePool.garbageCollect()

    def getDNA(self):
        return self.dnastring

    def __handleCancel(self):
        self.doneStatus = 'cancel'
        self.shopsVisited = []
        base.transitions.fadeOut(finishIval=EventInterval(self.doneEvent))

    def toggleSlide(self):
        self.slide = 1 - self.slide

    def resetZoom(self):
        self.cameraReset()
        self.zoomRatio = 1

    def goToNextShop(self):
        self.progressing = 1
        self.canZoom = False

        if self.shop == BODYSHOP:
            self.fsm.request('ColorShop')
        elif self.shop == COLORSHOP:
            self.fsm.request('ClothesShop')
        elif self.shop == CLOTHESSHOP:
            self.fsm.request('StatusShop')
        elif self.shop == STATUSSHOP:
            self.resetZoom()
            self.fsm.request('NameShop')
        elif self.shop == NAMESHOP:
            self.fsm.request('StartShop')
        else:
            self.notify.warning("goToNextShop: No shop found?")

    def goToLastShop(self):
        self.progressing = 0
        self.canZoom = False

        if self.shop == COLORSHOP:
            self.fsm.request('BodyShop')
        elif self.shop == CLOTHESSHOP:
            self.fsm.request('ColorShop')
        elif self.shop == STATUSSHOP:
            self.fsm.request('ClothesShop')
        elif self.shop == NAMESHOP:
            self.fsm.request('StatusShop')
        elif self.shop == STARTSHOP:
            self.fsm.request('NameShop')
        else:
            self.notify.warning("goToLastShop: No shop found?")

    def charSez(self, char, statement, dialogue = None):
        import pdb
        pdb.set_trace()
        char.setChatAbsolute(statement, CFSpeech, dialogue)

    def enterInit(self):
        pass

    def exitInit(self):
        pass

    def bodyShopOpening(self):
        self.bs.showButtons()
        self.guiNextButton.show()
        self.guiLastButton.hide()
        self.toonRotateSlider.show()

    def enterBodyShop(self):
        guiButton = loader.loadModel('phase_3/models/gui/quit_button')
        self.shop = BODYSHOP
        self.canZoom = True
        self.guiTopBar['text'] = TTLocalizer.ShapeYourToonTitle
        self.guiTopBar['text_fg'] = (0.0, 0.98, 0.5, 1)
        self.guiTopBar['text_scale'] = TTLocalizer.MATenterBodyShop
        self.accept('BodyShop-done', self.__handleBodyShopDone)
        if BODYSHOP not in self.shopsVisited:
            self.createRandomToon()
            self.shopsVisited.append(BODYSHOP)
            self.bodyWalls.reparentTo(self.squishJoint)
            self.bodyProps.reparentTo(self.propJoint)

            if not self.toonRotateSlider:
                self.toonRotateSlider = DirectSlider(parent = self.guiBottomBar, thumb_geom=(guiButton.find('**/QuitBtn_UP')), frameSize = (-0.8, 0.8, 0.1, -0.1), thumb_relief=None, thumb_geom_scale=1, text = 'Rotate', text_fg = (1, 1, 1, 1), text_style = 3, text_scale = 0.18, text_pos = (0.8, -0.04), text_align = TextNode.ALeft, scale = 1, value = 0, range = (-180, 180), command = self.rotateToonSlider)
                self.toonRotateSlider.setPos(-0.1, 0, -0.07)
                self.toonRotateSlider.setScale(0.5)
                self.toonRotateSliderRotationText = OnscreenText("0.0", scale=.1, pos=(0, .1), fg=(1, 1, 1, 1), style = 3)
                self.toonRotateSliderRotationText.reparentTo(self.toonRotateSlider.thumb)
                self.toonRotateSlider['extraArgs'] = [self.toonRotateSlider]
        else:
            self.dropRoom(self.bodyWalls, self.bodyProps)

        self.bs.enter(self.toon, self.shopsVisited)
        self.toon.show()
        self.bodyShopOpening()

    def exitBodyShop(self):
        self.canZoom = False
        self.squishRoom(self.bodyWalls)
        self.squishProp(self.bodyProps)
        self.bs.exit()
        self.ignore('BodyShop-done')

    def __handleBodyShopDone(self):
        self.guiNextButton.hide()
        self.guiLastButton.hide()
        if self.bs.doneStatus == 'next':
            self.bs.hideButtons()
            self.goToNextShop()
        else:
            self.bs.hideButtons()
            self.goToLastShop()

    def colorShopOpening(self):
        self.cos.showButtons()
        self.guiNextButton.show()
        self.guiLastButton.show()
        self.toonRotateSlider.show()

    def enterColorShop(self):
        self.shop = COLORSHOP
        self.canZoom = True
        self.guiTopBar['text'] = TTLocalizer.PaintYourToonTitle
        self.guiTopBar['text_fg'] = (0, 1, 1, 1)
        self.guiTopBar['text_scale'] = TTLocalizer.MATenterColorShop
        self.accept('ColorShop-done', self.__handleColorShopDone)
        self.dropRoom(self.colorWalls, self.colorProps)
        self.toon.setPos(self.toonPosition)
        self.colorShopOpening()
        self.cos.enter(self.toon, self.shopsVisited)
        if COLORSHOP not in self.shopsVisited:
            self.shopsVisited.append(COLORSHOP)

    def exitColorShop(self):
        self.canZoom = False
        self.squishRoom(self.colorWalls)
        self.squishProp(self.colorProps)
        self.cos.exit()
        self.ignore('ColorShop-done')

    def __handleColorShopDone(self):
        self.guiNextButton.hide()
        self.guiLastButton.hide()
        if self.cos.doneStatus == 'next':
            self.cos.hideButtons()
            self.goToNextShop()
        else:
            self.cos.hideButtons()
            self.goToLastShop()

    def clothesShopOpening(self):
        self.guiNextButton.show()
        self.guiLastButton.show()
        self.cls.showButtons()
        self.toonRotateSlider.show()

    def enterClothesShop(self):
        self.shop = CLOTHESSHOP
        self.canZoom = True
        self.guiTopBar['text'] = TTLocalizer.PickClothesTitle
        self.guiTopBar['text_fg'] = (1, 0.92, 0.2, 1)
        self.guiTopBar['text_scale'] = TTLocalizer.MATenterClothesShop
        self.accept('ClothesShop-done', self.__handleClothesShopDone)
        self.dropRoom(self.clothesWalls, self.clothesProps)
        self.toon.setScale(self.toonScale)
        self.toon.setPos(self.toonPosition)
        if not self.progressing:
            self.toon.setHpr(self.toonHpr)
        self.clothesShopOpening()
        self.cls.enter(self.toon)
        if CLOTHESSHOP not in self.shopsVisited:
            self.shopsVisited.append(CLOTHESSHOP)

    def exitClothesShop(self):
        self.canZoom = False
        self.squishRoom(self.clothesWalls)
        self.squishProp(self.clothesProps)
        self.cls.exit()
        self.ignore('ClothesShop-done')

    def __handleClothesShopDone(self):
        self.guiNextButton.hide()
        self.guiLastButton.hide()
        if self.cls.doneStatus == 'next':
            self.cls.hideButtons()
            self.goToNextShop()
        else:
            self.cls.hideButtons()
            self.goToLastShop()

    def statusShopOpening(self):
        self.guiNextButton.show()
        self.guiLastButton.show()
        self.ss.showButtons()
        self.toonRotateSlider.show()

    def enterStatusShop(self):
        self.shop = STATUSSHOP
        self.canZoom = True
        self.guiTopBar['text'] = TTLocalizer.PickStatusTitle
        self.guiTopBar['text_fg'] = (1, 0.92, 0.2, 1)
        self.guiTopBar['text_scale'] = TTLocalizer.MATenterClothesShop
        self.accept('StatusShop-done', self.__handleStatusShopDone)
        self.dropRoom(self.statusWalls, self.statusProps)
        self.toon.setScale(self.toonScale)
        self.toon.setPos(self.toonPosition)
        if not self.progressing:
            self.toon.setHpr(self.toonHpr)
        self.statusShopOpening()
        self.ss.enter(self.toon)
        if STATUSSHOP not in self.shopsVisited:
            self.shopsVisited.append(STATUSSHOP)

    def exitStatusShop(self):
        self.canZoom = False
        self.squishRoom(self.statusWalls)
        self.squishProp(self.statusProps)
        self.ss.exit()
        self.ignore('StatusShop-done')

    def __handleStatusShopDone(self):
        self.guiNextButton.hide()
        self.guiLastButton.hide()
        if self.ss.doneStatus == 'next':
            self.ss.hideButtons()
            self.goToNextShop()
        else:
            self.ss.hideButtons()
            self.goToLastShop()

    def startShopOpening(self):
        self.guiCheckButton.show()
        self.guiLastButton.show()
        self.sts.showButtons()
        self.toonRotateSlider.show()

    def enterStartShop(self):
        self.shop = STARTSHOP
        self.guiTopBar['text'] = TTLocalizer.PickStartTitle[2]
        self.guiTopBar['text_fg'] = (1, 0.92, 0.2, 1)
        self.guiTopBar['text_scale'] = TTLocalizer.MATenterClothesShop
        self.accept('StartShop-done', self.__handleStartShopDone)
        self.accept('updateTopBar', self.updateTopBar)
        self.dropRoom(self.startWalls, self.startProps)
        self.toon.setScale(self.toonScale)
        self.toon.setPos(self.toonPosition)
        if not self.progressing:
            self.toon.setHpr(self.toonHpr)
        self.startShopOpening()
        self.sts.enter(self.toon)
        if STARTSHOP not in self.shopsVisited:
            self.shopsVisited.append(STARTSHOP)

    def exitStartShop(self):
        self.guiNextButton['state'] = DGG.NORMAL
        self.squishRoom(self.startWalls)
        self.squishProp(self.startProps)
        self.sts.exit()
        self.ignore('StartShop-done')
        self.ignore('updateTopBar')

    def __handleStartShopDone(self):
        self.guiNextButton.hide()
        self.guiLastButton.hide()
        if self.sts.doneStatus == 'done':
            self.notify.debug("created")
            self.doneStatus = 'created'
            base.transitions.fadeOut(finishIval=EventInterval(self.doneEvent))
        elif self.sts.doneStatus == 'last':
            self.sts.hideButtons()
            self.goToLastShop()
        else:
            self.notify.warning(f"__handleStartShopDone: unknown done status: {self.sts.doneStatus}")

    def nameShopOpening(self):
        # self.guiCheckButton.show()
        self.guiNextButton.show()
        self.guiLastButton.show()
        if self.warp:
            self.guiLastButton.hide()
        if NAMESHOP not in self.shopsVisited:
            self.shopsVisited.append(NAMESHOP)

    def enterNameShop(self):
        pianoBase = self.nameProps.find("**/name_prop_piano_base")
        if not pianoBase.isEmpty():
            pianoBase.setColorScale(random.choice(ClothesColors))
        self.shop = NAMESHOP
        self.guiTopBar['text'] = TTLocalizer.NameToonTitle
        self.guiTopBar['text_fg'] = (0.0, 0.98, 0.5, 1)
        self.guiTopBar['text_scale'] = TTLocalizer.MATenterNameShop
        self.accept('NameShop-done', self.__handleNameShopDone)
        self.dropRoom(self.nameWalls, self.nameProps)
        self.spotlight.setPos(2, -1.95, 0.41)
        self.toon.setPos(Point3(1.5, -4, 0))
        self.toon.setH(120)
        if self.toonRotateSlider:
            self.toonRotateSlider.hide()
        self.ns.enter(self.toon, self.nameList, self.warp)
        self.nameShopOpening()

    def exitNameShop(self):
        self.notify.debug("exitNameShop")
        self.squishRoom(self.nameWalls)
        self.squishProp(self.nameProps)
        self.spotlight.setPos(1.18, -1.27, 0.41)
        self.ns.exit()
        self.ignore('NameShop-done')
        taskMgr.remove('nameShopOpeningTask')

    def rejectName(self):
        self.ns.rejectName(TTLocalizer.RejectNameText)

    def __handleNameShopDone(self):
        self.guiNextButton.hide()
        self.guiLastButton.hide()

        if self.ns.doneStatus == 'next':
            self.ns.hideAll()
            self.goToNextShop()
        elif self.ns.getDoneStatus() == 'last':
            self.ns.hideAll()
            self.goToLastShop()
        elif self.ns.getDoneStatus() == 'paynow':
            self.notify.debug("paynow?")
            self.doneStatus = 'paynow'
            base.transitions.fadeOut(finishIval=EventInterval(self.doneEvent))
        else:
            self.notify.debug("created")
            self.doneStatus = 'created'
            base.transitions.fadeOut(finishIval=EventInterval(self.doneEvent))


    def __handleNext(self):
        messenger.send('next')

    def __handleLast(self):
        messenger.send('last')

    def enterDone(self):
        base.discord.applyPreset('loading_game')
        pass

    def exitDone(self):
        pass

    def updateTopBar(self, choicesRemaining): #Updates the text at the top of the screen during PAG/StartShop and changes nextButton state
        self.guiTopBar['text'] = TTLocalizer.PickStartTitle[choicesRemaining]
        if choicesRemaining == 0:
            self.guiCheckButton['state'] = DGG.NORMAL
        else:
            self.guiCheckButton['state'] = DGG.DISABLED

    def create3DGui(self):
        self.proto = loader.loadModel('phase_3/models/makeatoon/tt_m_ara_mat_protoMachine')
        self.proto.setScale(0.2)
        self.proto.reparentTo(render)

    def setup3DPicker(self):
        self.accept('mouse1', self.mouseDown)
        self.accept('mouse1-up', self.mouseUp)
        self.pickerQueue = CollisionHandlerQueue()
        self.pickerTrav = CollisionTraverser('MousePickerTraverser')
        self.pickerTrav.setRespectPrevTransform(True)
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.pickerTrav.addCollider(self.pickerNP, self.pickerQueue)

    def mouseDown(self):
        self.notify.debug('Mouse 1 Down')
        mpos = base.mouseWatcherNode.getMouse()
        self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
        self.pickerTrav.traverse(render)
        if self.pickerQueue.getNumEntries() > 0:
            self.pickerQueue.sortEntries()
            self.pickedObj = self.pickerQueue.getEntry(0).getIntoNodePath()

    def mouseUp(self):
        self.notify.debug('Mouse 1 Up')

    def squishRoom(self, room):
        if not room.isEmpty():
            if self.roomSquishIval and self.roomSquishIval.isPlaying():
                self.roomSquishIval.finish()
            squishDuration = self.roomSquishActor.getDuration('squish')
            self.roomSquishIval = Sequence(Func(self.roomSquishActor.play, 'squish'), Wait(squishDuration), Func(room.hide))
            self.roomSquishIval.start()

    def squishProp(self, prop):
        if not prop.isEmpty():
            if self.propSquishIval and self.propSquishIval.isPlaying():
                self.propSquishIval.finish()
            squishDuration = self.propSquishActor.getDuration('propSquish')
            self.propSquishIval = Sequence(Func(self.propSquishActor.play, 'propSquish'), Wait(squishDuration), Func(prop.hide))
            self.propSquishIval.start()

    def dropRoom(self, walls, props):

        def propReparentTo(props):
            if not props.isEmpty():
                props.reparentTo(self.propJoint)

        def wallReparentTo(walls):
            if not walls.isEmpty():
                walls.reparentTo(self.squishJoint)

        if self.dropIval and self.dropIval.isPlaying():
            self.dropIval.finish()
        if not walls.isEmpty():
            walls.reparentTo(self.dropJoint)
            walls.show()
        if not props.isEmpty():
            props.reparentTo(self.dropJoint)
            props.show()
        dropDuration = self.roomDropActor.getDuration('drop')
        self.dropIval = Parallel(Sequence(Func(self.roomDropActor.play, 'drop'), Wait(dropDuration), Func(wallReparentTo, walls), Func(propReparentTo, props), Func(self.propSquishActor.pose, 'propSquish', 0), Func(self.roomSquishActor.pose, 'squish', 0)), Sequence(Wait(0.25), Func(self.smoke.show), Func(self.smoke.node().play), LerpColorScaleInterval(self.smoke, 0.5, Vec4(1, 1, 1, 0), startColorScale=Vec4(1, 1, 1, 1)), Func(self.smoke.hide)), Func(self.spotlightActor.play, 'spotlightShake'), Func(self.playRandomCrashSound))
        self.dropIval.start()

    def startFocusOutIval(self):
        if self.focusInIval.isPlaying():
            self.focusInIval.pause()
        if not self.focusOutIval.isPlaying():
            self.focusOutIval = LerpScaleInterval(self.spotlight, 0.25, self.spotlightFinalScale)
            self.focusOutIval.start()

    def startFocusInIval(self):
        if self.focusOutIval.isPlaying():
            self.focusOutIval.pause()
        if not self.focusInIval.isPlaying():
            self.focusInIval = LerpScaleInterval(self.spotlight, 0.25, self.spotlightOriginalScale)
            self.focusInIval.start()

    def cleanupFocusOutIval(self):
        if self.focusOutIval:
            self.focusOutIval.finish()
            del self.focusOutIval

    def cleanupFocusInIval(self):
        if self.focusInIval:
            self.focusInIval.finish()
            del self.focusInIval

    def cleanupDropIval(self):
        if self.dropIval:
            self.dropIval.finish()
            del self.dropIval

    def cleanupRoomSquishIval(self):
        if self.roomSquishIval:
            self.roomSquishIval.finish()
            del self.roomSquishIval

    def cleanupPropSquishIval(self):
        if self.propSquishIval:
            self.propSquishIval.finish()
            del self.propSquishIval

    def setToon(self, toon):
        self.toon = toon

    def setNextButtonState(self, state):
        self.guiNextButton['state'] = state

    def playRandomCrashSound(self):
        index = random.randint(0, len(self.crashSounds) - 1)
        base.playSfx(self.crashSounds[index], volume=self.sfxVolume)

    def rotateToonLeft(self, event):
        taskMgr.add(self.rotateToonLeftTask, 'rotateToonLeftTask')

    def rotateToonLeftTask(self, task):
        self.toon.setH(self.toon.getH() + self.hprDelta)
        return task.cont

    def stopToonRotateLeftTask(self, event):
        taskMgr.remove('rotateToonLeftTask')

    def rotateToonRight(self, event):
        taskMgr.add(self.rotateToonRightTask, 'rotateToonRightTask')

    def rotateToonRightTask(self, task):
        self.toon.setH(self.toon.getH() - self.hprDelta)
        return task.cont

    def stopToonRotateRightTask(self, event):
        taskMgr.remove('rotateToonRightTask')

    def rotateToonSlider(self, slider):
        value = slider['value']
        self.lastRot = value + self.defaultH
        dec = Decimal(self.lastRot - self.defaultH)
        self.toonRotateSliderRotationText['text'] = str(round(dec, 1))

        self.rotateToon()

    def rotateToon(self):
        hpr = self.toon.getHpr()
        self.toon.setHpr(self.lastRot, hpr[1], hpr[2])

    def createRandomToon(self):
        if self.toon:
            self.toon.stopBlink()
            self.toon.stopLookAroundNow()
            self.toon.delete()
        self.dna = ToonDNA.ToonDNA()
        self.dna.newToonRandom(gender='f', stage=1)
        self.toon = Toon.Toon()
        self.toon.setDNA(self.dna)
        self.toon.setNameVisible(0)
        self.toon.startBlink()
        self.toon.startLookAround()
        self.toon.reparentTo(render)
        self.toon.setPos(self.toonPosition)
        self.toon.setHpr(self.toonHpr)
        self.toon.setScale(self.toonScale)
        self.toon.loop('neutral')
        self.setNextButtonState(DGG.NORMAL)
        self.setToon(self.toon)
        messenger.send('MAT-newToonCreated')
