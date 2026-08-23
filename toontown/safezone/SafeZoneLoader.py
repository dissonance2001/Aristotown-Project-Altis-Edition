from pandac.PandaModules import *
from toontown.toonbase.ToonBaseGlobal import *
from toontown.distributed.ToontownMsgTypes import *
from toontown.hood import ZoneUtil
from direct.directnotify import DirectNotifyGlobal
from toontown.hood import Place
from direct.showbase import DirectObject
from direct.fsm import StateData
from direct.fsm import ClassicFSM, State
from direct.fsm import State
from direct.task import Task
from toontown.launcher import DownloadForceAcknowledge
from toontown.toon import HealthForceAcknowledge
from toontown.toon.Toon import teleportDebug
from toontown.tutorial import TutorialForceAcknowledge
from toontown.toonbase.ToontownGlobals import *
from toontown.building import ToonInterior
from toontown.hood import QuietZoneState
from toontown.dna.DNAParser import *
from direct.stdpy.file import *
from toontown.town import TownBattle

class SafeZoneLoader(StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('SafeZoneLoader')

    def __init__(self, hood, parentFSMState, doneEvent):
        StateData.StateData.__init__(self, doneEvent)
        self.hood = hood
        self.parentFSMState = parentFSMState
        self.fsm = ClassicFSM.ClassicFSM('SafeZoneLoader', [State.State('start', self.enterStart, self.exitStart, ['quietZone', 'playground', 'toonInterior']),
         State.State('playground', self.enterPlayground, self.exitPlayground, ['quietZone']),
         State.State('toonInterior', self.enterToonInterior, self.exitToonInterior, ['quietZone']),
         State.State('quietZone', self.enterQuietZone, self.exitQuietZone, ['playground', 'toonInterior']),
         State.State('golfcourse', self.enterGolfcourse, self.exitGolfcourse, ['quietZone', 'playground']),
         State.State('final', self.enterFinal, self.exitFinal, ['start'])], 'start', 'final')
        self.placeDoneEvent = 'placeDone'
        self.place = None
        self.playgroundClass = None
        self.townBattleDoneEvent = 'town-battle-done'
        self.kudosBoardTouching = False
        self.kudosBoardTouchTaskName = 'kudosBoardTouch-%s' % id(self)
        self.kudosBoardControlsLocked = False

    def load(self):
        self.music = base.loader.loadMusic(self.musicFile)
        self.activityMusic = base.loader.loadMusic(self.activityMusicFile)
        self.createSafeZone(self.dnaFile)
        self.parentFSMState.addChild(self.fsm)
        self.townBattle = TownBattle.TownBattle(self.townBattleDoneEvent)
        self.townBattle.load()

    def unload(self):
        self.stopKudosBoardInteraction()
        self.parentFSMState.removeChild(self.fsm)
        del self.parentFSMState
        self.geom.removeNode()
        del self.geom
        del self.fsm
        del self.hood
        del self.nodeList
        del self.playgroundClass
        del self.music
        del self.activityMusic
        del self.holidayPropTransforms
        self.deleteAnimatedProps()
        self.ignoreAll()
        ModelPool.garbageCollect()
        TexturePool.garbageCollect()

    def enter(self, requestStatus):
        self.fsm.enterInitialState()
        messenger.send('enterSafeZone')
        self.setState(requestStatus['where'], requestStatus)

    def exit(self):
        messenger.send('exitSafeZone')

    def setState(self, stateName, requestStatus):
        self.fsm.request(stateName, [requestStatus])

    def createSafeZone(self, dnaFile):
        if self.safeZoneStorageDNAFile:
            dnaBulk = DNABulkLoader(self.hood.dnaStore, (self.safeZoneStorageDNAFile,))
            dnaBulk.loadDNAFiles()
        node = loadDNAFile(self.hood.dnaStore, dnaFile)
        if node.getNumParents() == 1:
            self.geom = NodePath(node.getParent(0))
            self.geom.reparentTo(hidden)
        else:
            self.geom = hidden.attachNewNode(node)
        self.makeDictionaries(self.hood.dnaStore)
        self.createAnimatedProps(self.nodeList)
        self.createKudosBoard()
        self.holidayPropTransforms = {}
        npl = self.geom.findAllMatches('**/=DNARoot=holiday_prop')
        for i in range(npl.getNumPaths()):
            np = npl.getPath(i)
            np.setTag('transformIndex', repr(i))
            self.holidayPropTransforms[i] = np.getNetTransform()
        gsg = base.win.getGsg()
        if gsg:
            self.geom.prepareScene(gsg)
        self.geom.flattenMedium()

    def createKudosBoard(self):
        placements = {
            ToontownCentral: ((27.704, -42.685, 4.025), (134.023, 0.0, 0.0), 'ttcc_ext_ttc_kudosboard.png'),
            DonaldsDock: ((2.691, 178.833, 3.281), (-19.623, 0.0, 0.0), 'ttcc_ext_bb_kudosboard.png'),
            YeOlde: ((32.270, 44.393, -6.974), (-63.965, 0.0, 0.0), 'ttcc_ext_yott_kudosboard.png'),
            DaisyGardens: ((-19.239, 82.249, 0.025), (-24.761, 0.0, 0.0), 'ttcc_ext_dg_kudosboard.png'),
            MinniesMelodyland: ((71.344, 33.380, -14.498), (-66.793, 0.0, 0.0), 'ttcc_ext_mml_kudosboard.png'),
            TheBrrrgh: ((-148.572, -74.862, 6.175), (109.773, 0.0, 0.0), 'ttcc_ext_tb_kudosboard.png'),
            OutdoorZone: ((-7.216, -171.365, -0.143), (227.297, 0.0, 0.0), 'ttcc_ext_aa_kudosboard.png'),
            DonaldsDreamland: ((-44.987, -33.449, -15.688), (98.051, 0.0, 0.0), 'ttcc_ext_ddl_kudosboard.png')
        }
        placement = placements.get(self.hood.hoodId)
        if placement is None:
            self.kudosBoard = None
            return
        self.kudosBoard = loader.loadModel('phase_4/models/props/ttcc_ext_kudosboard')
        if self.kudosBoard.isEmpty():
            self.notify.warning('Could not load Kudo Board model')
            self.kudosBoard = None
            return
        texture = loader.loadTexture('phase_4/maps/kudos/' + placement[2])
        if texture:
            boardNodes = self.kudosBoard.findAllMatches('**/board')
            if boardNodes.getNumPaths() == 0:
                self.notify.warning('Could not find Kudo Board texture node: board')
            else:
                for i in range(boardNodes.getNumPaths()):
                    boardNodes.getPath(i).setTexture(texture, 1)
        else:
            self.notify.warning('Could not load Kudo Board texture: %s' % placement[2])
        self.kudosBoard.reparentTo(self.geom)
        self.kudosBoard.setPos(*placement[0])
        self.kudosBoard.setHpr(*placement[1])
        self.kudosBoardInteractionPos = Point3(*placement[0])

    def startKudosBoardInteraction(self):
        taskMgr.remove(self.kudosBoardTouchTaskName)
        self.kudosBoardTouching = False
        self.accept('kudosBoardGuiClosed', self.unlockKudosBoardControls)
        taskMgr.doMethodLater(
            0.25,
            self.__checkKudosBoardTouch,
            self.kudosBoardTouchTaskName
        )

    def stopKudosBoardInteraction(self):
        taskMgr.remove(self.kudosBoardTouchTaskName)
        self.kudosBoardTouching = False
        if hasattr(base, 'localAvatar') and base.localAvatar:
            if hasattr(base.localAvatar, 'closeKudosBoardGui'):
                base.localAvatar.closeKudosBoardGui()
        self.unlockKudosBoardControls()
        self.ignore('kudosBoardGuiClosed')

    def __checkKudosBoardTouch(self, task):
        if not hasattr(base, 'localAvatar') or base.localAvatar is None:
            return Task.again
        if not hasattr(self, 'kudosBoardInteractionPos'):
            return Task.done

        toonPos = base.localAvatar.getPos(render)
        dx = toonPos[0] - self.kudosBoardInteractionPos[0]
        dy = toonPos[1] - self.kudosBoardInteractionPos[1]
        dz = toonPos[2] - self.kudosBoardInteractionPos[2]
        distanceSquared = dx * dx + dy * dy

        if distanceSquared <= 16.0 and abs(dz) <= 10.0:
            if not self.kudosBoardTouching:
                self.kudosBoardTouching = True
                self.openKudosBoardGui()
        elif distanceSquared >= 36.0 or abs(dz) > 14.0:
            self.kudosBoardTouching = False

        return Task.again

    def openKudosBoardGui(self):
        if not hasattr(base, 'localAvatar') or base.localAvatar is None:
            return
        if getattr(base.localAvatar, 'kudosBoardGui', None):
            return
        if hasattr(base.localAvatar, 'disableAvatarControls'):
            base.localAvatar.disableAvatarControls()
            self.kudosBoardControlsLocked = True
        base.localAvatar.requestKudosBoard()

    def unlockKudosBoardControls(self):
        if not self.kudosBoardControlsLocked:
            return
        self.kudosBoardControlsLocked = False
        if hasattr(base, 'localAvatar') and base.localAvatar:
            if hasattr(base.localAvatar, 'enableAvatarControls'):
                base.localAvatar.enableAvatarControls()

    def makeDictionaries(self, dnaStore):
        self.nodeList = []
        for i in range(dnaStore.getNumDNAVisGroups()):
            groupFullName = dnaStore.getDNAVisGroupName(i)
            groupName = base.cr.hoodMgr.extractGroupName(groupFullName)
            groupNode = self.geom.find('**/' + groupFullName)
            if groupNode.isEmpty():
                self.notify.error('Could not find visgroup')
            groupNode.flattenMedium()
            self.nodeList.append(groupNode)

        self.removeLandmarkBlockNodes()
        self.hood.dnaStore.resetPlaceNodes()
        self.hood.dnaStore.resetDNAGroups()
        self.hood.dnaStore.resetDNAVisGroups()
        self.hood.dnaStore.resetDNAVisGroupsAI()

    def removeLandmarkBlockNodes(self):
        npc = self.geom.findAllMatches('**/suit_building_origin')
        for i in range(npc.getNumPaths()):
            npc.getPath(i).removeNode()

    def enterStart(self):
        pass

    def exitStart(self):
        pass

    def enterPlayground(self, requestStatus):
        self.acceptOnce(self.placeDoneEvent, self.handlePlaygroundDone)
        self.place = self.playgroundClass(self, self.fsm, self.placeDoneEvent)
        self.place.load()
        self.place.enter(requestStatus)
        base.cr.playGame.setPlace(self.place)
        self.startKudosBoardInteraction()

    def exitPlayground(self):
        self.stopKudosBoardInteraction()
        self.ignore(self.placeDoneEvent)
        self.place.exit()
        self.place.unload()
        self.place = None
        base.cr.playGame.setPlace(self.place)

    def handlePlaygroundDone(self):
        status = self.place.doneStatus
        teleportDebug(status, 'handlePlaygroundDone, doneStatus=%s' % (status,))
        if ZoneUtil.getBranchZone(status['zoneId']) == self.hood.hoodId and status['shardId'] == None:
            teleportDebug(status, 'same branch')
            self.fsm.request('quietZone', [status])
        else:
            self.doneStatus = status
            teleportDebug(status, 'different hood')
            messenger.send(self.doneEvent)

    def enterToonInterior(self, requestStatus):
        self.acceptOnce(self.placeDoneEvent, self.handleToonInteriorDone)
        self.place = ToonInterior.ToonInterior(self, self.fsm.getStateNamed('toonInterior'), self.placeDoneEvent)
        base.cr.playGame.setPlace(self.place)
        self.place.load()
        self.place.enter(requestStatus)

    def exitToonInterior(self):
        self.ignore(self.placeDoneEvent)
        self.place.exit()
        self.place.unload()
        self.place = None
        base.cr.playGame.setPlace(self.place)

    def handleToonInteriorDone(self):
        status = self.place.doneStatus
        if ZoneUtil.getBranchZone(status['zoneId']) == self.hood.hoodId and status['shardId'] == None:
            self.fsm.request('quietZone', [status])
        else:
            self.doneStatus = status
            messenger.send(self.doneEvent)

    def enterQuietZone(self, requestStatus):
        self.quietZoneDoneEvent = uniqueName('quietZoneDone')
        self.acceptOnce(self.quietZoneDoneEvent, self.handleQuietZoneDone)
        self.quietZoneStateData = QuietZoneState.QuietZoneState(self.quietZoneDoneEvent)
        self.quietZoneStateData.load()
        self.quietZoneStateData.enter(requestStatus)

    def exitQuietZone(self):
        self.ignore(self.quietZoneDoneEvent)
        del self.quietZoneDoneEvent
        self.quietZoneStateData.exit()
        self.quietZoneStateData.unload()
        self.quietZoneStateData = None

    def handleQuietZoneDone(self):
        status = self.quietZoneStateData.getRequestStatus()
        if status['where'] == 'estate':
            self.doneStatus = status
            messenger.send(self.doneEvent)
        else:
            self.fsm.request(status['where'], [status])

    def enterFinal(self):
        pass

    def exitFinal(self):
        pass

    def createAnimatedProps(self, nodeList):
        self.animPropDict = {}
        for i in nodeList:
            animPropNodes = i.findAllMatches('**/animated_prop_*')
            numAnimPropNodes = animPropNodes.getNumPaths()
            for j in range(numAnimPropNodes):
                animPropNode = animPropNodes.getPath(j)
                if animPropNode.getName().startswith('animated_prop_generic'):
                    className = 'GenericAnimatedProp'
                else:
                    className = animPropNode.getName()[14:-8]
                symbols = {}
                base.cr.importModule(symbols, 'toontown.hood', [className])
                classObj = getattr(symbols[className], className)
                animPropObj = classObj(animPropNode)
                animPropList = self.animPropDict.setdefault(i, [])
                animPropList.append(animPropObj)

            interactivePropNodes = i.findAllMatches('**/interactive_prop_*')
            numInteractivePropNodes = interactivePropNodes.getNumPaths()
            for j in range(numInteractivePropNodes):
                interactivePropNode = interactivePropNodes.getPath(j)
                className = 'GenericAnimatedProp'
                symbols = {}
                base.cr.importModule(symbols, 'toontown.hood', [className])
                classObj = getattr(symbols[className], className)
                interactivePropObj = classObj(interactivePropNode)
                animPropList = self.animPropDict.get(i)
                if animPropList is None:
                    animPropList = self.animPropDict.setdefault(i, [])
                animPropList.append(interactivePropObj)

    def deleteAnimatedProps(self):
        for zoneNode, animPropList in list(self.animPropDict.items()):
            for animProp in animPropList:
                animProp.delete()

        del self.animPropDict

    def enterAnimatedProps(self, zoneNode):
        for animProp in self.animPropDict.get(zoneNode, ()):
            animProp.enter()

    def exitAnimatedProps(self, zoneNode):
        for animProp in self.animPropDict.get(zoneNode, ()):
            animProp.exit()

    def enterGolfcourse(self, requestStatus):
        base.transitions.fadeOut(t=0)

    def exitGolfcourse(self):
        pass
        
    def townBattleDoneEvent(self):
        pass
