# -*- coding: utf-8 -*-
from direct.directnotify import DirectNotifyGlobal
from direct.gui.DirectGui import *
from direct.gui import DirectGuiGlobals as DGG
from pandac.PandaModules import *

from toontown.shtiker import ShtikerPage
from toontown.toon import Toon
from toontown.toon import ToonProfileGlobals as TPG
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals

if not hasattr(TTLocalizer, 'ToonProfilePageTitle'):
    TTLocalizer.ToonProfilePageTitle = 'Profile'


class ToonProfilePage(ShtikerPage.ShtikerPage):
    notify = DirectNotifyGlobal.directNotify.newCategory('ToonProfilePage')

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)
        self.poseIndex = 0
        self.nameplateIndex = 0
        self.backgroundIndex = 0
        self.previewToon = None
        self.previewPoseRoot = None
        self.previewBackground = None
        self.previewNameplate = None
        self.previewNameText = None
        self.backgroundModel = None
        self.nameplateModel = None
        self.selectorGui = None
        self.loaded = False

    def load(self):
        if self.loaded:
            return
        self.loaded = True
        self.backgroundModel = loader.loadModel('phase_3.5/models/gui/profile/background')
        self.nameplateModel = loader.loadModel('phase_3.5/models/gui/profile/nameplates')
        self.selectorGui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')

        self.title = DirectLabel(
            parent=self, relief=None, text=TTLocalizer.ToonProfilePageTitle,
            text_font=ToontownGlobals.getToonFont(), text_scale=0.105,
            text_fg=(0.03, 0.03, 0.03, 1), pos=(0, 0, 0.62))

        self.previewRoot = DirectFrame(parent=self, relief=None, pos=(-0.43, 0, 0))
        self.previewBackground = DirectFrame(
            parent=self.previewRoot, relief=None, pos=(0, 0, 0.31),
            image_scale=(0.165, 1, 0.095), scale=(0.68, 1, 0.68),
            sortOrder=1)

        self.previewNameplate = DirectFrame(
            parent=self.previewRoot, relief=None, pos=(0, 0, -0.04),
            image_scale=0.50, sortOrder=5)
        self.previewNameText = DirectLabel(
            parent=self.previewRoot, relief=None, text='',
            text_font=ToontownGlobals.getToonFont(), text_scale=0.050,
            text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
            pos=(0, 0, -0.035), sortOrder=6)

        self.previewToonRoot = self.previewRoot.attachNewNode('toonProfilePreviewToonRoot')
        self.previewToonRoot.setPos(0, -0.01, -0.38)

        self._makeSelector('Profile Background', 0.40, self.changeBackground, 'background')
        self._makeSelector('Profile Nameplate', 0.08, self.changeNameplate, 'nameplate')
        self._makeSelector('Profile Pose', -0.24, self.changePose, 'pose')

        buttonModel = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
        buttonGeom = (
            buttonModel.find('**/ChtBx_OKBtn_UP'),
            buttonModel.find('**/ChtBx_OKBtn_DN'),
            buttonModel.find('**/ChtBx_OKBtn_Rllvr'))
        self.applyButton = DirectButton(
            parent=self, relief=None, image=buttonGeom, image_scale=(0.66, 1, 0.82),
            text='Apply', text_font=ToontownGlobals.getToonFont(),
            text_scale=0.050, text_pos=(0, -0.017),
            pos=(0.36, 0, -0.54), command=self.applySelection)
        self.resetButton = DirectButton(
            parent=self, relief=None, image=buttonGeom, image_scale=(0.66, 1, 0.82),
            text='Reset', text_font=ToontownGlobals.getToonFont(),
            text_scale=0.050, text_pos=(0, -0.017),
            pos=(0.67, 0, -0.54), command=self.resetSelection)
        buttonModel.removeNode()

        self.statusLabel = DirectLabel(
            parent=self, relief=None, text='', text_font=ToontownGlobals.getToonFont(),
            text_scale=0.036, text_fg=(0.1, 0.45, 0.1, 1), pos=(0.515, 0, -0.64))

    def _makeSelector(self, title, z, command, prefix):
        DirectLabel(
            parent=self, relief=None, text=title,
            text_font=ToontownGlobals.getToonFont(), text_scale=0.058,
            text_fg=(0.03, 0.03, 0.03, 1), pos=(0.49, 0, z + 0.12))

        arrowImage = (
            self.selectorGui.find('**/Horiz_Arrow_UP'),
            self.selectorGui.find('**/Horiz_Arrow_DN'),
            self.selectorGui.find('**/Horiz_Arrow_Rllvr'),
            self.selectorGui.find('**/Horiz_Arrow_UP'))

        left = DirectButton(
            parent=self, relief=None, image=arrowImage,
            image3_color=Vec4(1, 1, 1, 0.5),
            scale=(-0.92, 0.92, 0.92), pos=(0.16, 0, z),
            command=command, extraArgs=[-1])
        right = DirectButton(
            parent=self, relief=None, image=arrowImage,
            image3_color=Vec4(1, 1, 1, 0.5),
            scale=(0.92, 0.92, 0.92), pos=(0.82, 0, z),
            command=command, extraArgs=[1])

        outer = DirectFrame(
            parent=self, relief=DGG.RAISED,
            borderWidth=(0.018, 0.018),
            frameColor=(0.0, 0.53, 0.84, 1),
            frameSize=(-0.245, 0.245, -0.078, 0.078),
            pos=(0.49, 0, z))
        value = DirectLabel(
            parent=outer, relief=DGG.FLAT,
            frameColor=(0.98, 0.98, 0.98, 1),
            frameSize=(-0.212, 0.212, -0.050, 0.050),
            text='', text_font=ToontownGlobals.getToonFont(), text_scale=0.045,
            text_fg=(0.05, 0.05, 0.05, 1), text_wordwrap=13,
            pos=(0, -0.01, -0.008))

        setattr(self, prefix + 'LeftButton', left)
        setattr(self, prefix + 'RightButton', right)
        setattr(self, prefix + 'ValueFrame', outer)
        setattr(self, prefix + 'ValueLabel', value)

    def enter(self):
        ShtikerPage.ShtikerPage.enter(self)
        self._readCurrentSelection()
        self.statusLabel['text'] = ''
        self.refreshPreview()
        eventName = base.localAvatar.uniqueName('toonProfileChange')
        self.accept(eventName, self._profileUpdated)

    def exit(self):
        self.ignore(base.localAvatar.uniqueName('toonProfileChange'))
        ShtikerPage.ShtikerPage.exit(self)

    def unload(self):
        self.loaded = False
        self.ignoreAll()
        self._destroyPreviewToon()
        if self.backgroundModel:
            self.backgroundModel.removeNode()
            self.backgroundModel = None
        if self.nameplateModel:
            self.nameplateModel.removeNode()
            self.nameplateModel = None
        if self.selectorGui:
            self.selectorGui.removeNode()
            self.selectorGui = None
        ShtikerPage.ShtikerPage.unload(self)

    def _readCurrentSelection(self):
        poseId = getattr(base.localAvatar, 'profilePose', TPG.DEFAULT_POSE)
        nameplateId = getattr(base.localAvatar, 'profileNameplate', TPG.DEFAULT_NAMEPLATE)
        backgroundId = getattr(base.localAvatar, 'profileBackground', TPG.DEFAULT_BACKGROUND)
        self.poseIndex = self._indexForId(TPG.POSES, TPG.normalisePoseId(poseId))
        self.nameplateIndex = self._indexForId(TPG.NAMEPLATES, TPG.normaliseNameplateId(nameplateId))
        self.backgroundIndex = self._indexForId(TPG.BACKGROUNDS, TPG.normaliseBackgroundId(backgroundId))

    def _indexForId(self, entries, itemId):
        for index in range(len(entries)):
            if entries[index]['id'] == itemId:
                return index
        return 0

    def changePose(self, direction):
        self.poseIndex = (self.poseIndex + direction) % len(TPG.POSES)
        self.statusLabel['text'] = ''
        self.refreshPreview()

    def changeNameplate(self, direction):
        self.nameplateIndex = (self.nameplateIndex + direction) % len(TPG.NAMEPLATES)
        self.statusLabel['text'] = ''
        self.refreshPreview()

    def changeBackground(self, direction):
        self.backgroundIndex = (self.backgroundIndex + direction) % len(TPG.BACKGROUNDS)
        self.statusLabel['text'] = ''
        self.refreshPreview()

    def resetSelection(self):
        self.poseIndex = self._indexForId(TPG.POSES, TPG.DEFAULT_POSE)
        self.nameplateIndex = self._indexForId(TPG.NAMEPLATES, TPG.DEFAULT_NAMEPLATE)
        self.backgroundIndex = self._indexForId(TPG.BACKGROUNDS, TPG.DEFAULT_BACKGROUND)
        self.statusLabel['text'] = ''
        self.refreshPreview()

    def applySelection(self):
        poseId = TPG.POSES[self.poseIndex]['id']
        nameplateId = TPG.NAMEPLATES[self.nameplateIndex]['id']
        backgroundId = TPG.BACKGROUNDS[self.backgroundIndex]['id']
        try:
            base.localAvatar.setToonProfile(poseId, nameplateId, backgroundId)
            base.localAvatar.requestToonProfile(poseId, nameplateId, backgroundId)
            self.statusLabel['text'] = 'Profile applied!'
        except Exception as error:
            self.notify.warning('Unable to apply Toon Profile: %s' % error)
            self.statusLabel['text'] = 'Unable to apply profile.'

    def _profileUpdated(self, *args):
        self._readCurrentSelection()
        self.refreshPreview()

    def refreshPreview(self):
        if not self.loaded:
            return
        pose = TPG.POSES[self.poseIndex]
        nameplate = TPG.NAMEPLATES[self.nameplateIndex]
        background = TPG.BACKGROUNDS[self.backgroundIndex]

        self.poseValueLabel['text'] = pose['name']
        self.nameplateValueLabel['text'] = nameplate['name']
        self.backgroundValueLabel['text'] = background['name']

        backgroundNode = self.backgroundModel.find('**/%s' % background['node'])
        if backgroundNode.isEmpty():
            backgroundNode = self.backgroundModel.find('**/default')
        self.previewBackground['image'] = backgroundNode

        nameplateNode = self.nameplateModel.find('**/%s' % nameplate['node'])
        if nameplateNode.isEmpty():
            nameplateNode = self.nameplateModel.find('**/default_med_blue')
        scale = nameplate.get('scale', (1, 1, 1))
        position = nameplate.get('position', (0, 0, 0.13))
        self.previewNameplate['image'] = nameplateNode
        self.previewNameplate['image_scale'] = (0.50 * scale[0], 0.50, 0.50 * scale[2])
        self.previewNameplate.setPos(position[0], position[1], -0.17 + position[2])
        self.previewNameText['text'] = base.localAvatar.getName()
        self.previewNameText.setPos(0, 0, -0.035)

        self._generatePreviewToon(pose['id'])

    def _destroyPreviewToon(self):
        if self.previewToon:
            try:
                self.previewToon.cleanup()
            except:
                pass
            try:
                self.previewToon.removeNode()
            except:
                pass
            self.previewToon = None
        if self.previewPoseRoot:
            try:
                self.previewPoseRoot.removeNode()
            except:
                pass
            self.previewPoseRoot = None

    def _generatePreviewToon(self, poseId):
        self._destroyPreviewToon()
        try:
            toon = Toon.Toon()
            toon.setDNAString(base.localAvatar.style.makeNetString())
            toon.getGeomNode().setDepthWrite(1)
            toon.getGeomNode().setDepthTest(1)
            toon.getGeomNode().setTwoSided(True)

            neutralBounds = self._getNeutralBounds(toon)
            TPG.applyPose(toon, poseId, self.notify)

            bodyCenteredPose = poseId == 27
            posedFit = TPG.usesPosedPanelFit(poseId) or poseId == 40
            if posedFit and not bodyCenteredPose:
                self._fitSelectedPoseOnBookPage(toon, neutralBounds, 0.42)
                if poseId == 44 and self.previewPoseRoot:
                    self.previewPoseRoot.setZ(
                        self.previewPoseRoot.getZ() + 0.04)
            else:
                self._fitGeometry(toon, 0.42, neutralBounds)
                toon.reparentTo(self.previewToonRoot)
                self._centerPoseOnNeutral(toon, self.previewToonRoot, (0, 0, 0))
                if poseId == 27:
                    toon.setZ(toon.getZ() + 0.25)
                if poseId == 43:
                    toon.setZ(toon.getZ() + 0.04)
            self.previewToon = toon
        except Exception as error:
            self.notify.warning('Unable to build Toon Profile preview: %s' % error)

    def _fitSelectedPoseOnBookPage(self, toon, neutralBounds, dimension):
        poseRoot = self.previewToonRoot.attachNewNode('toonProfileBookPoseRoot')
        scaleRoot = poseRoot.attachNewNode('toonProfileBookScaleRoot')
        offsetRoot = scaleRoot.attachNewNode('toonProfileBookOffsetRoot')
        facingRoot = offsetRoot.attachNewNode('toonProfileBookFacingRoot')
        facingRoot.setH(180)
        toon.reparentTo(facingRoot)

        p1 = Point3()
        p2 = Point3()
        try:
            scaleRoot.calcTightBounds(p1, p2)
        except:
            toon.reparentTo(self.previewToonRoot)
            self._fitGeometry(toon, dimension, neutralBounds)
            self.previewPoseRoot = None
            return

        posedSize = p2 - p1
        posedBiggest = max(posedSize[0], posedSize[2])
        if posedBiggest <= 0:
            posedBiggest = 1.0

        neutralBiggest = posedBiggest
        if neutralBounds is not None:
            neutralSize = neutralBounds[1] - neutralBounds[0]
            candidate = max(neutralSize[0], neutralSize[2])
            if candidate > 0:
                neutralBiggest = candidate

        neutralScale = dimension / neutralBiggest
        posedFitScale = dimension / posedBiggest
        finalScale = min(neutralScale, posedFitScale)

        posedCenter = (p1 + p2) / 2.0
        offsetRoot.setPos(-posedCenter[0], -posedCenter[1], -posedCenter[2])
        scaleRoot.setScale(finalScale)
        poseRoot.setPos(0, 2, -0.02)
        self.previewPoseRoot = poseRoot

    def _getPoseBodyCenter(self, geom, relativeTo):
        props = getattr(geom, '_toonProfilePoseProps', [])
        stashedProps = []
        for prop in props:
            try:
                prop.stash()
                stashedProps.append(prop)
            except:
                pass

        try:
            p1 = Point3()
            p2 = Point3()
            geom.calcTightBounds(p1, p2)
            localCenter = (p1 + p2) / 2.0
            try:
                return relativeTo.getRelativePoint(geom, localCenter)
            except:
                return geom.getMat(relativeTo).xformPoint(localCenter)
        except:
            return None
        finally:
            for prop in stashedProps:
                try:
                    prop.unstash()
                except:
                    pass

    def _centerPoseOnNeutral(self, geom, relativeTo, basePos):
        geom.setPos(basePos[0], basePos[1], basePos[2])
        bodyCenter = self._getPoseBodyCenter(geom, relativeTo)
        if bodyCenter is None:
            return

        neutralCenter = Point3(basePos[0], basePos[1] + 2.0,
                               basePos[2] - 0.02)
        correction = neutralCenter - bodyCenter
        currentPos = geom.getPos(relativeTo)
        geom.setPos(relativeTo,
                    currentPos[0] + correction[0],
                    currentPos[1],
                    currentPos[2] + correction[2])

    def _getNeutralBounds(self, geom):
        try:
            geom.pose('neutral', 0)
        except:
            try:
                geom.loop('neutral')
            except:
                pass

        p1 = Point3()
        p2 = Point3()
        try:
            geom.calcTightBounds(p1, p2)
            return (Point3(p1), Point3(p2))
        except:
            return None

    def _fitGeometry(self, geom, dimension, referenceBounds=None, includePoseProps=False):
        if referenceBounds is not None:
            p1 = Point3(referenceBounds[0])
            p2 = Point3(referenceBounds[1])
        else:
            props = getattr(geom, '_toonProfilePoseProps', [])
            stashedProps = []
            if not includePoseProps:
                for prop in props:
                    try:
                        prop.stash()
                        stashedProps.append(prop)
                    except:
                        pass

            p1 = Point3()
            p2 = Point3()
            try:
                geom.calcTightBounds(p1, p2)
            finally:
                for prop in stashedProps:
                    try:
                        prop.unstash()
                    except:
                        pass

        d = p2 - p1
        biggest = max(d[0], d[2])
        if biggest == 0:
            return

        scale = dimension / biggest
        mid = (p1 + d / 2.0) * scale
        geomXform = hidden.attachNewNode('toonProfileGeomXform')
        for child in geom.getChildren():
            child.reparentTo(geomXform)
        geomXform.setPosHprScale(-mid[0], -mid[1] + 2, -mid[2] - 0.02,
                                180, 0, 0, scale, scale, scale)
        geomXform.reparentTo(geom)
