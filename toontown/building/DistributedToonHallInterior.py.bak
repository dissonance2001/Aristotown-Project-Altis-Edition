import random

from toontown.toonbase.ToonBaseGlobal import *
from toontown.toonbase import ToontownGlobals
from toontown.dna.DNAParser import DNADoor
from DistributedToonInterior import DistributedToonInterior
from direct.directnotify import DirectNotifyGlobal
from toontown.building import ToonInteriorColors
from toontown.hood import ZoneUtil
from toontown.toon.DistributedNPCToonBase import DistributedNPCToonBase
from pandac.PandaModules import DecalEffect


class DistributedToonHallInterior(DistributedToonInterior):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedToonHallInterior')

    def setup(self):
        self.dnaStore = base.cr.playGame.dnaStore
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)

        self.interior = loader.loadModel(
            'phase_3.5/models/modules/cc_m_ara_int_toonhall'
        )
        self.interior.reparentTo(render)

        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.colors = ToonInteriorColors.colors[hoodId]
        self.replaceRandomInModel(self.interior)

        doorModelName = 'door_double_round_ul'
        if doorModelName[-1:] == 'r':
            doorModelName = doorModelName[:-1] + 'l'
        else:
            doorModelName = doorModelName[:-1] + 'r'

        door = self.dnaStore.findNode(doorModelName)
        doorOrigin = self.interior.find('**/door_origin;+s')

        if doorOrigin.isEmpty():
            self.notify.warning(
                'The Clash Toon Hall model has no door_origin node.'
            )
        else:
            doorNP = door.copyTo(doorOrigin)
            doorOrigin.setScale(0.8, 0.8, 0.8)
            doorOrigin.setPos(doorOrigin, 0, -0.025, 0)

            color = self.randomGenerator.choice(self.colors['TI_door'])
            DNADoor.setupDoor(
                doorNP,
                self.interior,
                doorOrigin,
                self.dnaStore,
                str(self.block),
                color
            )

            doorFrame = doorNP.find('door_*_flat')
            if not doorFrame.isEmpty():
                doorFrame.wrtReparentTo(self.interior)
                doorFrame.setColor(color)

        self.setupClashFurniture()

        del self.colors
        del self.dnaStore
        del self.randomGenerator

        self.interior.flattenMedium()

        for npcToon in self.cr.doFindAllInstances(DistributedNPCToonBase):
            npcToon.initToonState()

    def setupClashFurniture(self):
        floorMainHall = self.interior.find('**/floor_mainhall_geom')
        if not floorMainHall.isEmpty():
            floorMainHall.node().setEffect(DecalEffect.make())

        clubDeskOrigin = self.interior.find('**/clubdesk_origin_0')
        if clubDeskOrigin.isEmpty():
            self.notify.warning('The Clash Toon Hall has no clubdesk_origin_0 node.')
        else:
            clubDesk = loader.loadModel('phase_4/models/props/ttcc_env_clubdesk')
            if clubDesk.isEmpty():
                self.notify.warning('Could not load the Clash club desk model.')
            else:
                clubDesk.reparentTo(clubDeskOrigin)
                clubDeskShadow = clubDesk.find('**/clubdesk_dropshadow')
                if not clubDeskShadow.isEmpty() and not floorMainHall.isEmpty():
                    clubDeskShadow.wrtReparentTo(floorMainHall)

        stoolModel = loader.loadModel('phase_5.5/models/estate/table_radioDesat')
        if stoolModel.isEmpty():
            self.notify.warning('Could not load the Clash Toon Hall stool model.')
            return

        stoolModel.setScale(50, 50, 24.1359)
        for stoolPart in stoolModel.findAllMatches('**/RADIOTABLE_*'):
            stoolPart.setColorScale(0.5451, 0.2706, 0.0745, 1.0)

        stoolOrigins = self.interior.findAllMatches('**/stool_origin_*')
        for stoolOrigin in stoolOrigins:
            stoolModel.instanceTo(stoolOrigin)

        stoolModel.removeNode()

    # Altis may still receive Silly Meter updates from its news manager.
    # Clash's Toon Hall does not use the TTR Silly Meter, so ignore them.
    def sillyMeterIsRunning(self, isRunning):
        pass

    def selectPhase(self, newPhase):
        pass

    def enterToon(self):
        self.toonhallView = (
            Point3(0, -5, 3),
            Point3(0, 12.0, 7.0),
            Point3(0.0, 10.0, 5.0),
            Point3(0.0, 10.0, 5.0),
            1
        )
        self.setupCollisions(2.5)
        self.firstEnter = 1
        self.accept('CamChangeColl-into', self.handleCloseToWall)

    def handleCloseToWall(self, collEntry):
        if self.firstEnter == 0:
            return

        interiorRopes = self.interior.find('**/*interior_ropes')
        if (not interiorRopes.isEmpty() and
                interiorRopes == collEntry.getIntoNodePath().getParent()):
            return

        self.restoreCam()
        self.accept('CamChangeColl-exit', self.handleAwayFromWall)

    def handleAwayFromWall(self, collEntry):
        if self.firstEnter == 1:
            self.cleanUpCollisions()
            self.setupCollisions(0.75)
            self.firstEnter = 0

    def setupCollisions(self, radius):
        r = base.localAvatar.getClampedAvatarHeight() * radius
        collisionSphere = CollisionSphere(0, 0, 0, r)
        collisionNode = CollisionNode('CamChangeColl')
        collisionNode.addSolid(collisionSphere)
        collisionNode.setFromCollideMask(ToontownGlobals.WallBitmask)
        collisionNode.setIntoCollideMask(BitMask32.allOff())

        self.camChangeNP = base.localAvatar.getPart(
            'torso', '1000'
        ).attachNewNode(collisionNode)

        self.cHandlerEvent = CollisionHandlerEvent()
        self.cHandlerEvent.addInPattern('%fn-into')
        self.cHandlerEvent.addOutPattern('%fn-exit')
        base.cTrav.addCollider(self.camChangeNP, self.cHandlerEvent)

    def cleanUpCollisions(self):
        if hasattr(self, 'camChangeNP'):
            base.cTrav.removeCollider(self.camChangeNP)
            self.camChangeNP.detachNode()
            del self.camChangeNP

        if hasattr(self, 'cHandlerEvent'):
            del self.cHandlerEvent

    def restoreCam(self):
        base.localAvatar.setCameraFov(settings['fieldofview'])

    def disable(self):
        base.localAvatar.removeCameraPosition()
        base.localAvatar.resetCameraPosition()
        self.restoreCam()
        self.ignoreAll()
        self.cleanUpCollisions()
        DistributedToonInterior.disable(self)

    def delete(self):
        DistributedToonInterior.delete(self)
