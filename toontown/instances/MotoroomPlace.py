from toontown.toonbase.ToonBaseGlobal import *
import math
from random import Random
from toontown.building import MotoroomInstanceGlobals
from toontown.building import ToonInterior
from toontown.building.interior.props.LavaLamp import LavaLamp, hexToPCol
from toontown.hood import Place
from toontown.toonbase import ToontownGlobals
from panda3d.core import AmbientLight, BitMask32, CollisionNode, CollisionPlane, ColorAttrib, MaterialAttrib, Plane, Point3, PointLight, TransparencyAttrib, Vec3


class MotoroomPlace(ToonInterior.ToonInterior):
    def __init__(self, loader, parentFSMState, doneEvent):
        ToonInterior.ToonInterior.__init__(
            self, loader, parentFSMState, doneEvent)
        self.geom = None
        self.lavaLamp = None
        self.floorCollision = None
        self.floorZ = None
        self.pacesetterSky = None
        self.entryXYH = None
        self.roomLightNodes = []
        self.oreoRoot = None
        self.oreoNodes = []
        self.oreoTaskName = 'motoroomFloatingOreos-%s' % id(self)
        self.sakamoreoNameTaskName = 'motoroomSakamoreoName-%s' % id(self)
        self.entryApplyTaskNames = (
            'motoroomEntryApplyA-%s' % id(self),
            'motoroomEntryApplyB-%s' % id(self))

    def load(self):
        ToonInterior.ToonInterior.load(self)
        self.geom = loader.loadModel(MotoroomInstanceGlobals.MODEL_PATH)
        self.geom.reparentTo(render)
        self.geom.setTwoSided(True)
        self.geom.setScale(.875)
        self._setupRoomEffects()
        self._setupRoomLighting()
        self._setupStageLightBeams()
        self._setupPacesetterView()
        self._setupFloatingOreos()
        self._setupFloorCollision()
        self._loadSpawnReference()
        self._setupLavaLamp()
        self._startSakamoreoNameFix()

    def _setupRoomEffects(self):
        render.setColorScale(*hexToPCol('FFFFFF'))

        patterns = (
            '**/lights*',
            '**/stagelight_*',
            '**/spotlight_*',
            '**/circle_lights',
            '**/lights_pole*',
            '**/ceiling_lights',
            '**/lower_lights_ceiling',
        )

        for pattern in patterns:
            matches = self.geom.findAllMatches(pattern)
            for index in range(matches.getNumPaths()):
                node = matches.getPath(index)
                node.setColorScaleOff(1)
                node.setLightOff(100)
                node.setTwoSided(True)


    def _setupRoomLighting(self):
        ambient = AmbientLight('motoroom_ambient')
        ambient.setColor((1.10, 1.10, 1.18, 1.0))
        ambientNode = render.attachNewNode(ambient)
        render.setLight(ambientNode)
        self.roomLightNodes.append(ambientNode)

        lightSpecs = (
            ('**/ceiling_lights', (0.52, 0.54, 0.66, 1.0), Vec3(1.0, 0.012, 0.0012)),
            ('**/lower_lights_ceiling', (0.42, 0.45, 0.58, 1.0), Vec3(1.0, 0.014, 0.0015)),
            ('**/circle_lights', (0.34, 0.37, 0.50, 1.0), Vec3(1.0, 0.016, 0.0018)),
        )

        for index, spec in enumerate(lightSpecs):
            pattern, color, attenuation = spec
            locator = self.geom.find(pattern)
            if locator.isEmpty():
                continue

            pos = locator.getPos(render)
            try:
                bounds = locator.getTightBounds(render)
                if bounds:
                    pos = (bounds[0] + bounds[1]) * 0.5
            except:
                pass

            point = PointLight('motoroom_point_%d' % index)
            point.setColor(color)
            point.setAttenuation(attenuation)
            pointNode = render.attachNewNode(point)
            pointNode.setPos(render, pos)
            render.setLight(pointNode)
            self.roomLightNodes.append(pointNode)

    def _getStageLensColor(self, lens, lensIndex):
        fallbackColors = (
            (0.10, 0.22, 1.00),
            (1.00, 0.26, 0.03),
            (1.00, 0.04, 0.04),
            (0.10, 1.00, 0.12),
            (1.00, 0.06, 0.55),
        )
        color = None
        geomPaths = lens.findAllMatches('**/+GeomNode')
        for pathIndex in range(geomPaths.getNumPaths()):
            geomPath = geomPaths.getPath(pathIndex)
            geomNode = geomPath.node()
            for geomIndex in range(geomNode.getNumGeoms()):
                state = geomNode.getGeomState(geomIndex)
                try:
                    materialAttrib = state.getAttrib(MaterialAttrib.getClassSlot())
                except:
                    materialAttrib = None
                if materialAttrib:
                    material = materialAttrib.getMaterial()
                    if material:
                        for getterName in ('getEmission', 'getBaseColor', 'getDiffuse', 'getAmbient'):
                            getter = getattr(material, getterName, None)
                            if not getter:
                                continue
                            try:
                                candidate = getter()
                            except:
                                continue
                            high = max(candidate[0], candidate[1], candidate[2])
                            low = min(candidate[0], candidate[1], candidate[2])
                            if high > 0.02 and high - low > 0.08:
                                color = (candidate[0], candidate[1], candidate[2])
                                break
                        if color is not None:
                            break
                try:
                    colorAttrib = state.getAttrib(ColorAttrib.getClassSlot())
                except:
                    colorAttrib = None
                if colorAttrib:
                    try:
                        candidate = colorAttrib.getColor()
                        high = max(candidate[0], candidate[1], candidate[2])
                        low = min(candidate[0], candidate[1], candidate[2])
                        if high > 0.02 and high - low > 0.08:
                            color = (candidate[0], candidate[1], candidate[2])
                    except:
                        pass
                if color is not None:
                    break
            if color is not None:
                break

        if color is None:
            color = fallbackColors[lensIndex] if lensIndex < len(fallbackColors) else (1.0, 1.0, 1.0)

        high = max(color[0], color[1], color[2])
        if high > 1.0:
            color = (color[0] / high, color[1] / high, color[2] / high)
        return color

    def _setupStageLightBeams(self):
        sourceRoom = loader.loadModel('phase_6/models/areas/ttcc_int_mplayer_boss')
        if not sourceRoom or sourceRoom.isEmpty():
            print('MOTOROOM STAGELIGHTS: source room missing')
            return

        created = 0
        for lensIndex in range(5):
            sourceFixture = sourceRoom.find('**/stagelight_%d' % lensIndex)
            targetFixture = self.geom.find('**/stagelight_%d' % lensIndex)
            targetLens = self.geom.find('**/spotlight_%d' % lensIndex)

            if sourceFixture.isEmpty() or targetFixture.isEmpty() or targetLens.isEmpty():
                continue

            sourceLens = sourceFixture.find('**/spotlight_%d' % lensIndex)
            if sourceLens.isEmpty():
                sourceLens = sourceFixture.find('**/spotlight_*')
            if sourceLens.isEmpty():
                continue

            sourceBeam = sourceLens.find('**/spotlight_beam_%d' % lensIndex)
            if sourceBeam.isEmpty():
                sourceBeam = sourceLens.find('**/spotlight_beam_*')
            if sourceBeam.isEmpty():
                continue

            beam = sourceBeam.copyTo(targetLens)
            beam.setMat(sourceBeam.getMat(sourceLens))
            beam.setName('motoroom_spotlight_beam_%d' % lensIndex)

            color = self._getStageLensColor(targetLens, lensIndex)
            beam.setColorScaleOff(1)
            beam.setLightOff(100)
            beam.setColor(color[0], color[1], color[2], 1.0)
            beam.setTransparency(TransparencyAttrib.MAlpha, 1)
            beam.setAlphaScale(0.18)
            beam.setDepthWrite(False)
            beam.setTwoSided(True)
            beam.show()
            created += 1

        sourceRoom.removeNode()
        print('MOTOROOM STAGELIGHTS: created', created)

    def _copyToRender(self, node):
        copied = node.copyTo(render)
        copied.setMat(node.getMat(render))
        return copied

    def _setupPacesetterView(self):
        exportedWindows = self.geom.findAllMatches('**/bg_glass*')
        exportedSky = self.geom.find('**/sky')

        for index in range(exportedWindows.getNumPaths()):
            window = exportedWindows.getPath(index)
            window.show()
            window.setTransparency(TransparencyAttrib.MAlpha, 100)
            window.setColorScale(0.48, 0.56, 0.78, 0.45, 100)
            window.setTwoSided(True)

        sourceRoom = loader.loadModel('phase_8/models/areas/ttcc_psetter_bossRoom')
        if sourceRoom and not sourceRoom.isEmpty():
            sourceRoom.reparentTo(render)
            sourceSky = sourceRoom.find('**/sky')
            if not sourceSky.isEmpty():
                self.pacesetterSky = self._copyToRender(sourceSky)
                self.pacesetterSky.show()
                self.pacesetterSky.setColorScaleOff(100)
                self.pacesetterSky.setLightOff(100)
                self.pacesetterSky.setTwoSided(True)
            sourceRoom.removeNode()

        if self.pacesetterSky is not None:
            if not exportedSky.isEmpty():
                exportedSky.hide()
        elif not exportedSky.isEmpty():
            exportedSky.show()
            exportedSky.setColorScaleOff(100)
            exportedSky.setLightOff(100)
            exportedSky.setTwoSided(True)

    def _setupFloatingOreos(self):
        source = loader.loadModel('phase_8/models/props/motoroom_oreo')
        if not source or source.isEmpty():
            print('MOTOROOM OREOS: source model missing')
            return

        sourceNode = source.find('**/Sketchfab_model')
        if sourceNode.isEmpty():
            sourceNode = source.find('**/Cookies')
        if sourceNode.isEmpty():
            sourceNode = source

        try:
            roomBounds = self.geom.getTightBounds(render)
        except:
            roomBounds = None

        if not roomBounds:
            source.removeNode()
            print('MOTOROOM OREOS: room bounds missing')
            return

        roomCenter = (roomBounds[0] + roomBounds[1]) * 0.5
        windows = self.geom.findAllMatches('**/bg_glass*')
        windowData = []
        seen = set()

        for index in range(windows.getNumPaths()):
            window = windows.getPath(index)
            try:
                bounds = window.getTightBounds(render)
            except:
                bounds = None
            if not bounds:
                continue

            center = (bounds[0] + bounds[1]) * 0.5
            key = (round(center.getX(), 1), round(center.getY(), 1), round(center.getZ(), 1))
            if key in seen:
                continue
            seen.add(key)

            outward = Vec3(center - roomCenter)
            outward.setZ(0.0)
            if outward.length() < 0.01:
                continue
            outward.normalize()
            side = Vec3(-outward.getY(), outward.getX(), 0.0)
            half = (bounds[1] - bounds[0]) * 0.5
            sideExtent = abs(side.getX()) * half.getX() + abs(side.getY()) * half.getY()
            if sideExtent < 2.0:
                sideExtent = max(half.getX(), half.getY(), 2.0)
            zExtent = max(half.getZ(), 2.0)
            windowData.append((center, outward, side, sideExtent, zExtent))

        if not windowData:
            source.removeNode()
            print('MOTOROOM OREOS: no usable windows found')
            return

        self.oreoRoot = render.attachNewNode('motoroom_floating_oreos')
        rng = Random(120826)

        for center, outward, side, sideExtent, zExtent in windowData:
            for cookieIndex in range(6):
                depth = rng.uniform(12.0, 58.0)
                basePos = Point3(center)
                basePos += side * rng.uniform(-0.82, 0.82) * sideExtent
                basePos += Vec3(0.0, 0.0, rng.uniform(-0.78, 0.78) * zExtent)
                basePos += outward * depth

                oreo = sourceNode.copyTo(self.oreoRoot)
                oreo.setMat(sourceNode.getMat(source))
                oreo.setPos(render, basePos)
                scale = max(18.0, 22.0 + depth * 0.48 + rng.uniform(-6.0, 6.0))
                oreo.setScale(scale)
                oreo.setTwoSided(True)

                h = rng.uniform(-180.0, 180.0)
                p = rng.uniform(-180.0, 180.0)
                r = rng.uniform(-180.0, 180.0)
                oreo.setHpr(render, h, p, r)

                self.oreoNodes.append((
                    oreo, basePos, side, outward,
                    rng.uniform(0.0, math.pi * 2.0),
                    rng.uniform(12.0, 20.0),
                    rng.uniform(0.5, 1.8),
                    rng.uniform(0.4, 1.4),
                    rng.uniform(0.14, 0.28),
                    h, p, r,
                    rng.uniform(-4.0, 4.0),
                    rng.uniform(-2.4, 2.4),
                    rng.uniform(-3.2, 3.2)))

        source.removeNode()
        taskMgr.remove(self.oreoTaskName)
        taskMgr.add(self._updateFloatingOreos, self.oreoTaskName)
        print('MOTOROOM OREOS: created', len(self.oreoNodes))

    def _updateFloatingOreos(self, task):
        t = task.time
        for data in self.oreoNodes:
            oreo, basePos, side, outward, phase, sideAmp, zAmp, depthAmp, speed, h, p, r, hSpeed, pSpeed, rSpeed = data
            if oreo.isEmpty():
                continue

            pos = Point3(basePos)
            pos -= side * (math.sin(t * speed * 1.35 + phase) * sideAmp)
            pos += Vec3(0.0, 0.0, math.sin(t * speed * 0.73 + phase * 1.7) * zAmp)
            pos += outward * (math.sin(t * speed * 0.51 + phase * 0.43) * depthAmp)
            oreo.setPos(render, pos)
            oreo.setHpr(
                render,
                h + t * hSpeed,
                p + t * pSpeed,
                r + t * rSpeed)

        return task.cont

    def _cleanupFloatingOreos(self):
        taskMgr.remove(self.oreoTaskName)
        self.oreoNodes = []
        if self.oreoRoot:
            try:
                self.oreoRoot.removeNode()
            except:
                pass
            self.oreoRoot = None

    def _getFloorZ(self):
        names = ('floor2', 'floor2.001', 'ground')

        for name in names:
            node = self.geom.find('**/%s' % name)
            if node.isEmpty():
                continue

            try:
                bounds = node.getTightBounds(render)
                if bounds:
                    low = bounds[0].getZ()
                    high = bounds[1].getZ()
                    print('MOTOROOM FLOOR BOUNDS:', name, 'LOW=', low, 'HIGH=', high)
                    return low + 0.15
            except:
                try:
                    bounds = node.getTightBounds()
                    if bounds:
                        lowPoint = render.getRelativePoint(node, bounds[0])
                        highPoint = render.getRelativePoint(node, bounds[1])
                        print('MOTOROOM FLOOR BOUNDS:', name, 'LOW=', lowPoint.getZ(), 'HIGH=', highPoint.getZ())
                        return lowPoint.getZ() + 0.15
                except:
                    pass

        return -1.500

    def _setupFloorCollision(self):
        self.floorZ = self._getFloorZ()
        floorNode = CollisionNode('motoroom_floor_plane')
        floorNode.setFromCollideMask(BitMask32.allOff())
        floorNode.setIntoCollideMask(ToontownGlobals.FloorBitmask)
        floorNode.addSolid(CollisionPlane(
            Plane(Vec3(0.0, 0.0, 1.0), Point3(0.0, 0.0, self.floorZ))))
        self.floorCollision = render.attachNewNode(floorNode)

    def _loadSpawnReference(self):
        spawn = self.geom.find('**/front_entrance')
        if spawn.isEmpty():
            spawn = self.geom.find('**/elevator_origin')

        if not spawn.isEmpty():
            pos = spawn.getPos(render)
            hpr = spawn.getHpr(render)
            self.entryXYH = (pos.getX(), pos.getY(), hpr.getX())
            return

        reference = loader.loadModel(
            'phase_8/models/areas/motoroom_spawn_reference.bam')
        if not reference or reference.isEmpty():
            return

        spawn = reference.find('**/front_entrance')
        if spawn.isEmpty():
            spawn = reference.find('**/elevator_origin')

        if not spawn.isEmpty():
            pos = spawn.getPos(reference)
            hpr = spawn.getHpr(reference)
            self.entryXYH = (pos.getX(), pos.getY(), hpr.getX())

        reference.removeNode()

    def _setupLavaLamp(self):
        try:
            self.lavaLamp = LavaLamp(colorIndex=3)
        except:
            self.lavaLamp = None
            return

        locator = self.geom.find('**/lavalamp')
        if locator.isEmpty():
            locator = self.geom.find('**/lavalamp_0')

        self.lavaLamp.reparentTo(render)
        if locator.isEmpty():
            self.lavaLamp.setPosHpr(
                render,
                -43.547, 15.078, -0.875,
                177.820, 0.0, 0.0)
        else:
            self.lavaLamp.setMat(render, locator.getMat(render))

        collisionNodes = self.lavaLamp.findAllMatches('**/+CollisionNode')
        collisionPaths = []
        for index in range(collisionNodes.getNumPaths()):
            collisionPaths.append(collisionNodes.getPath(index))

        for collisionPath in collisionPaths:
            collisionPath.removeNode()

    def _getEntryTransform(self):
        return (-57.298, 42.204, -4.602, -89.755)

    def _applyEntryTransform(self):
        if not hasattr(base, 'localAvatar') or not base.localAvatar:
            return

        x, y, z, h = self._getEntryTransform()
        base.localAvatar.setPosHpr(render, x, y, z, h, 0.0, 0.0)

        try:
            base.localAvatar.d_broadcastPositionNow()
        except:
            pass

        print('[Motoroom Spawn Applied] (%.3f, %.3f, %.3f, %.3f)' % (
            x, y, z, h))

    def _applyEntryTransformTask(self, task):
        self._applyEntryTransform()
        return task.done

    def _scheduleEntryTransform(self):
        self._applyEntryTransform()
        for taskName in self.entryApplyTaskNames:
            taskMgr.remove(taskName)
        taskMgr.doMethodLater(
            0.20, self._applyEntryTransformTask,
            self.entryApplyTaskNames[0])
        taskMgr.doMethodLater(
            0.75, self._applyEntryTransformTask,
            self.entryApplyTaskNames[1])

    def _placeTeleportInPostZoneComplete(self, requestStatus):
        Place.Place._placeTeleportInPostZoneComplete(self, requestStatus)
        self._scheduleEntryTransform()

    def teleportInDone(self):
        Place.Place.teleportInDone(self)
        self._scheduleEntryTransform()

    def _clearSakamoreoShopkeeperTitle(self, task):
        try:
            from toontown.toon.DistributedNPCToonBase import DistributedNPCToonBase
            npcs = base.cr.doFindAllInstances(DistributedNPCToonBase)
        except:
            return task.again

        for npc in npcs:
            try:
                if npc.getName() == 'Sakamoreo':
                    npc.npcType = ''
                    npc.setDisplayName(npc.getName())
            except:
                pass
        return task.again

    def _startSakamoreoNameFix(self):
        taskMgr.remove(self.sakamoreoNameTaskName)
        taskMgr.doMethodLater(
            0.25,
            self._clearSakamoreoShopkeeperTitle,
            self.sakamoreoNameTaskName)

    def _stopSakamoreoNameFix(self):
        taskMgr.remove(self.sakamoreoNameTaskName)

    def unload(self):
        self._stopSakamoreoNameFix()
        self._cleanupFloatingOreos()
        for taskName in self.entryApplyTaskNames:
            taskMgr.remove(taskName)

        if self.lavaLamp:
            try:
                self.lavaLamp.cleanup()
            except:
                try:
                    self.lavaLamp.removeNode()
                except:
                    pass
            self.lavaLamp = None

        if self.floorCollision:
            try:
                self.floorCollision.removeNode()
            except:
                pass
            self.floorCollision = None

        if self.pacesetterSky:
            try:
                self.pacesetterSky.removeNode()
            except:
                pass
            self.pacesetterSky = None

        for roomLightNode in self.roomLightNodes:
            try:
                render.clearLight(roomLightNode)
            except:
                pass
            try:
                roomLightNode.removeNode()
            except:
                pass
        self.roomLightNodes = []

        render.clearColorScale()

        if self.geom:
            self.geom.removeNode()
            self.geom = None

        ToonInterior.ToonInterior.unload(self)

    def enterTeleportIn(self, requestStatus):
        Place.Place.enterTeleportIn(self, requestStatus)
