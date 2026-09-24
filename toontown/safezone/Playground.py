from direct.interval.IntervalGlobal import *
from pandac.PandaModules import *
from toontown.toonbase.ToonBaseGlobal import *
from direct.directnotify import DirectNotifyGlobal
from toontown.shader import FogGlobals
from toontown.shader.ToontownFog import ToontownFog
from toontown.hood import Place # Make sure to replace all (battleplace.battleplace) with (place.place) when invasion is done
from toontown.battle import BattlePlace # Use for TTC Invasion
from direct.showbase import DirectObject
from direct.fsm import StateData
from direct.fsm import ClassicFSM, State
from direct.fsm import State
from direct.task import Task
from toontown.quest3.base import QuestGlobals
from toontown.toon import DeathForceAcknowledge
from toontown.toon import HealthForceAcknowledge
from toontown.toon.npc import NPCToons
from toontown.toon.gui.ScaledToonHeadFrame import MiniScaledToonHeadFrame
from toontown.tutorial import TutorialForceAcknowledge
from toontown.toon import NPCForceAcknowledge
from toontown.trolley import Trolley
from toontown.toontowngui import TTDialog
from toontown.toonbase import ToontownGlobals
from toontown.toon.Toon import teleportDebug
from toontown.toonbase import TTLocalizer
from direct.gui import DirectLabel
from otp.distributed.TelemetryLimiter import RotationLimitToH, TLGatherAllAvs
from toontown.quest import Quests
from toontown.battle import BattleParticles
from toontown.dna.DNAParser import DNABulkLoader

class Playground(BattlePlace.BattlePlace):
    notify = DirectNotifyGlobal.directNotify.newCategory('Playground')

    def __init__(self, loader, parentFSM, doneEvent):
        BattlePlace.BattlePlace.__init__(self, loader, doneEvent)
        self.tfaDoneEvent = 'tfaDoneEvent'
        self.fog = None
        self.fsm = ClassicFSM.ClassicFSM('Playground', [
            State.State('start',
                        self.enterStart,
                        self.exitStart, [
                            'walk',
                            'deathAck',
                            'doorIn',
                            'tunnelIn']),
            State.State('walk',
                        self.enterWalk,
                        self.exitWalk, [
                            'drive',
                            'sit',
                            'stickerBook',
                            'TFA',
                            'DFA',
                            'trialerFA',
                            'trolley',
                            'final',
                            'doorOut',
                            'options',
                            'quest',
                            'purchase',
                            'stopped',
                            'fishing',
                            'battle',
                            'WaitForBattle',
                            'pet']),
            State.State('pet',
                        self.enterPet,
                        self.exitPet, [
                            'walk',
                            'trialerFA'
                        ]),
            State.State('stickerBook',
                        self.enterStickerBook,
                        self.exitStickerBook, [
                            'walk',
                            'DFA',
                            'TFA',
                            'trolley',
                            'final',
                            'doorOut',
                            'quest',
                            'purchase',
                            'stopped',
                            'fishing',
                            'trialerFA']),
            State.State('sit',
                        self.enterSit,
                        self.exitSit, [
                            'walk',
                            'DFA',
                            'trialerFA']),
            State.State('drive',
                        self.enterDrive,
                        self.exitDrive, [
                            'walk',
                            'DFA',
                            'trialerFA']),
            State.State('trolley',
                        self.enterTrolley,
                        self.exitTrolley, [
                            'walk']),
            State.State('doorIn',
                        self.enterDoorIn,
                        self.exitDoorIn, [
                            'walk']),
            State.State('doorOut',
                        self.enterDoorOut,
                        self.exitDoorOut, [
                            'walk']),
            State.State('TFA',
                        self.enterTFA,
                        self.exitTFA, [
                            'TFAReject',
                            'DFA']),
            State.State('TFAReject',
                        self.enterTFAReject,
                        self.exitTFAReject, [
                            'walk']),
            State.State('trialerFA',
                        self.enterTrialerFA,
                        self.exitTrialerFA, [
                            'trialerFAReject',
                            'DFA']),
            State.State('trialerFAReject',
                        self.enterTrialerFAReject,
                        self.exitTrialerFAReject, [
                            'walk']),
            State.State('DFA',
                        self.enterDFA,
                        self.exitDFA, [
                            'DFAReject',
                            'NPCFA',
                            'HFA']),
            State.State('DFAReject',
                        self.enterDFAReject,
                        self.exitDFAReject, [
                            'walk']),
            State.State('NPCFA',
                        self.enterNPCFA,
                        self.exitNPCFA, [
                            'NPCFAReject',
                            'HFA']),
            State.State('NPCFAReject',
                        self.enterNPCFAReject,
                        self.exitNPCFAReject, [
                            'walk']),
            State.State('HFA',
                        self.enterHFA,
                        self.exitHFA, [
                            'HFAReject',
                            'teleportOut',
                            'tunnelOut']),
            State.State('HFAReject',
                        self.enterHFAReject,
                        self.exitHFAReject, [
                            'walk']),
            State.State('deathAck',
                        self.enterDeathAck,
                        self.exitDeathAck, [
                            'teleportIn']),
            State.State('teleportIn',
                        self.enterTeleportIn,
                        self.exitTeleportIn, [
                            'walk',
                            'popup',
                            'Movie']),
            State.State('Movie',
                        self.enterMovie,
                        self.exitMovie, [
                            'walk']),
            State.State('popup',
                        self.enterPopup,
                        self.exitPopup, [
                            'walk']),
            State.State('teleportOut',
                        self.enterTeleportOut,
                        self.exitTeleportOut, [
                            'deathAck',
                            'teleportIn']),
            State.State('died',
                        self.enterDied,
                        self.exitDied, [
                            'final']),
            State.State('tunnelIn',
                        self.enterTunnelIn,
                        self.exitTunnelIn, [
                            'walk']),
            State.State('tunnelOut',
                        self.enterTunnelOut,
                        self.exitTunnelOut, [
                            'final']),
            State.State('quest',
                        self.enterQuest,
                        self.exitQuest, [
                            'walk']),
            State.State('purchase',
                        self.enterPurchase,
                        self.exitPurchase, [
                            'walk']),
            State.State('stopped',
                        self.enterStopped,
                        self.exitStopped, [
                            'walk']),
            State.State('fishing',
                        self.enterFishing,
                        self.exitFishing, [
                            'walk']),
            State.State('final',
                        self.enterFinal,
                        self.exitFinal, [
                            'start']),
           State.State('WaitForBattle', self.enterWaitForBattle, self.exitWaitForBattle, ['battle', 'walk']),
           State.State('battle', self.enterBattle, self.exitBattle, ['walk', 'teleportOut', 'died'])], 
            'start', 'final')
        self.parentFSM = parentFSM
        self.tunnelOriginList = []
        self.trolleyDoneEvent = 'trolleyDone'
        self.hfaDoneEvent = 'hfaDoneEvent'
        self.npcfaDoneEvent = 'npcfaDoneEvent'
        self.dialog = None
        self.deathAckBox = None
        self.screen = None

    def enter(self, requestStatus):
        self.fsm.enterInitialState()
        messenger.send('enterPlayground')
        self.accept('doorDoneEvent', self.handleDoorDoneEvent)
        self.accept('DistributedDoor_doorTrigger', self.handleDoorTrigger)
        base.playMusic(self.loader.music, looping=1, volume=0.8)
        self.loader.geom.reparentTo(render)
        for i in self.loader.nodeList:
            self.loader.enterAnimatedProps(i)

        self._telemLimiter = TLGatherAllAvs('Playground', RotationLimitToH)

        def __lightDecorationOn__():
            geom = base.cr.playGame.hood.loader.geom
            self.loader.hood.eventLights = geom.findAllMatches('**/*light*')
            self.loader.hood.eventLights += geom.findAllMatches('**/*lamp*')
            self.loader.hood.eventLights += geom.findAllMatches('**/prop_snow_tree*')
            self.loader.hood.eventLights += geom.findAllMatches('**/prop_tree*')
            self.loader.hood.eventLights += geom.findAllMatches('**/*christmas*')
            for light in self.loader.hood.eventLights:
                light.setColorScaleOff(0)

        newsManager = base.cr.newsManager
        newsManager = base.cr.newsManager
        if newsManager:
            holidayId = base.cr.newsManager.getDecorationHolidayId()
            # Halloween Event
            if ToontownGlobals.HALLOWEEN == holidayId and self.loader.hood.spookySkyFile:
                lightsOff = Sequence(
                    LerpColorScaleInterval(base.cr.playGame.hood.loader.geom, 0.1, Vec4(0.55, 0.55, 0.65, 1)),
                    Func(self.loader.hood.startSpookySky), Func(__lightDecorationOn__))
                lightsOff.start()
            elif ToontownGlobals.APRIL_FOOLS == holidayId and ZoneUtil.getHoodId(
                    requestStatus['zoneId']) == 3000 and self.loader.hood.spookySkyFile:
                # We enable the silly little darkness in the Brrrgh during APril Toons for erfit..
                lightsOff = Sequence(
                    LerpColorScaleInterval(base.cr.playGame.hood.loader.geom, 0.1, Vec4(0.55, 0.55, 0.65, 1)),
                    Func(self.loader.hood.startSpookySky), Func(__lightDecorationOn__))
                lightsOff.start()
            elif ToontownGlobals.CHRISTMAS == holidayId and self.loader.hood.snowySkyFile:
                lightsOff = Sequence(
                    LerpColorScaleInterval(base.cr.playGame.hood.loader.geom, 0.1, Vec4(0.7, 0.7, 0.8, 1)),
                    Func(self.loader.hood.startSnowySky), Func(__lightDecorationOn__))
                lightsOff.start()
                self.snowEvent = BattleParticles.loadParticleFile('snowdisk.ptf')
                self.snowEvent.setPos(0, 30, 10)
                # 2 and 3 are only for the blizzard event and should be removed
                self.snowEvent2 = BattleParticles.loadParticleFile('snowdisk.ptf')
                self.snowEvent2.setPos(0, 10, 10)
                self.snowEvent3 = BattleParticles.loadParticleFile('snowdisk.ptf')
                self.snowEvent3.setPos(0, 20, 5)
                self.snowEventRender = base.cr.playGame.hood.loader.geom.attachNewNode('snowRender')
                self.snowEventRender.setDepthWrite(2)
                self.snowEventRender.setBin('fixed', 1)
                self.snowEvent.start(camera, self.snowEventRender)
                # 2 and 3 are only for the blizzard event and should be removed
                self.snowEvent2.start(camera, self.snowEventRender)
                self.snowEvent3.start(camera, self.snowEventRender)
            else:
                self.loader.hood.startSky()
                lightsOn = LerpColorScaleInterval(base.cr.playGame.hood.loader.geom, 0.1, Vec4(1, 1, 1, 1))
                lightsOn.start()
        else:
            self.loader.hood.startSky()
            lightsOn = LerpColorScaleInterval(base.cr.playGame.hood.loader.geom, 0.1, Vec4(1, 1, 1, 1))
            lightsOn.start()
        NametagGlobals.setWant2dNametags(True)
        self.zoneId = requestStatus['zoneId']
        self.tunnelOriginList = base.cr.hoodMgr.addLinkTunnelHooks(self, self.loader.nodeList, self.zoneId)
        how = requestStatus['how']
        if how == 'teleportIn':
            how = 'deathAck'
        self.fsm.request(how, [requestStatus])

        # Configure fog
        assert self.fog is None  # if this is thrown, we haven't cleaned up our fog from a previous playground load.
        self.fog = ToontownFog(FogGlobals.zoneId2FogAttrs.get(self.zoneId), 'Playground Fog-%s' % self.zoneId)
        self.fog.attachFog([render])

    def exit(self):
        self.ignoreAll()
        messenger.send('exitPlayground')
        self._telemLimiter.destroy()
        del self._telemLimiter
        for node in self.tunnelOriginList:
            node.removeNode()

        if self.screen:
            self.screen.delete()

        self.loader.geom.reparentTo(hidden)

        def __lightDecorationOff__():
            for light in self.loader.hood.eventLights:
                light.reparentTo(hidden)

        newsManager = base.cr.newsManager
        NametagGlobals.setWant2dNametags(False)
        for i in self.loader.nodeList:
            self.loader.exitAnimatedProps(i)

        self.loader.hood.stopSky()
        self.loader.music.stop()

    def load(self):
        BattlePlace.BattlePlace.load(self)
        self.parentFSM.getStateNamed('playground').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('playground').removeChild(self.fsm)
        del self.parentFSM
        del self.fsm
        if self.dialog:
            self.dialog.cleanup()
            self.dialog = None
        if self.deathAckBox:
            self.deathAckBox.cleanup()
            self.deathAckBox = None
        TTDialog.cleanupDialog('globalDialog')
        self.ignoreAll()
        BattlePlace.BattlePlace.unload(self)

    def enterMovie(self, teleportIn=0):
        base.localAvatar.b_setAnimState('Neutral', 1.0)
        base.localAvatar.setTeleportAvailable(0)
        self.ignore('teleportQuery')
        base.localAvatar.startSleepWatch(self.__handleFallingAsleepMovie)
        NametagGlobals.setMasterArrowsOn(0)
        self.fsm.request('walk')
     #   if QuestGlobals.isInTutorial(base.localAvatar) and self.loader.hood.id == ToontownGlobals.ToontownCentral:
      #      self.playPlaygroundTut()
     #   else:
      #      # Safety net: if we somehow entered Movie without a tutorial to run, bail back to walk
       #     self.fsm.request('walk')

    def exitMovie(self):
        base.localAvatar.stopSleepWatch()
        self.accept('teleportQuery', self.handleTeleportQuery)
        base.localAvatar.setTeleportAvailable(1)
        NametagGlobals.setMasterArrowsOn(1)

    def __handleFallingAsleepMovie(self, task):
        messenger.send('wakeup')
        return Task.done

    def showTreasurePoints(self, points):
        self.hideDebugPointText()
        for i in range(len(points)):
            p = points[i]
            self.showDebugPointText(str(i), p)

            # Remove Fog
            self.fog.removeFog()
            self.fog = None

    def showDropPoints(self, points):
        self.hideDebugPointText()
        for i in range(len(points)):
            p = points[i]
            self.showDebugPointText(str(i), p)

    def showPaths(self):
        pass

    def hidePaths(self):
        self.hideDebugPointText()

    def showPathPoints(self, paths, waypoints = None):
        self.hideDebugPointText()
        lines = LineSegs()
        lines.setColor(1, 0, 0, 1)
        from toontown.classicchars import CCharPaths
        for name, pointDef in list(paths.items()):
            self.showDebugPointText(name, pointDef[0])
            for connectTo in pointDef[1]:
                toDef = paths[connectTo]
                fromP = pointDef[0]
                toP = toDef[0]
                lines.moveTo(fromP[0], fromP[1], fromP[2] + 2.0)
                wpList = CCharPaths.getWayPoints(name, connectTo, paths, waypoints)
                for wp in wpList:
                    lines.drawTo(wp[0], wp[1], wp[2] + 2.0)
                    self.showDebugPointText('*', wp)

                lines.drawTo(toP[0], toP[1], toP[2] + 2.0)

        self.debugText.attachNewNode(lines.create())

    def hideDebugPointText(self):
        if hasattr(self, 'debugText'):
            children = self.debugText.getChildren()
            for i in range(children.getNumPaths()):
                children[i].removeNode()

    def showDebugPointText(self, text, point):
        if not hasattr(self, 'debugText'):
            self.debugText = self.loader.geom.attachNewNode('debugText')
            self.debugTextNode = TextNode('debugTextNode')
            self.debugTextNode.setTextColor(1, 0, 0, 1)
            self.debugTextNode.setAlign(TextNode.ACenter)
            self.debugTextNode.setFont(ToontownGlobals.getSignFont())
        self.debugTextNode.setText(text)
        np = self.debugText.attachNewNode(self.debugTextNode.generate())
        np.setPos(point[0], point[1], point[2])
        np.setScale(4.0)
        np.setBillboardPointEye()

    def enterTrolley(self):
        base.localAvatar.laffMeter.start()
        base.localAvatar.b_setAnimState('off', 1)
        base.localAvatar.cantLeaveGame = 1
        self.accept(self.trolleyDoneEvent, self.handleTrolleyDone)
        self.trolley = Trolley.Trolley(self, self.fsm, self.trolleyDoneEvent)
        self.trolley.load()
        self.trolley.enter()

    def exitTrolley(self):
        base.localAvatar.laffMeter.stop()
        base.localAvatar.cantLeaveGame = 0
        self.ignore(self.trolleyDoneEvent)
        self.trolley.unload()
        self.trolley.exit()
        del self.trolley

    def detectedTrolleyCollision(self):
        self.fsm.request('trolley')

    def handleTrolleyDone(self, doneStatus):
        self.notify.debug('handling trolley done event')
        mode = doneStatus['mode']
        if mode == 'reject':
            self.fsm.request('walk')
        elif mode == 'exit':
            self.fsm.request('walk')
        elif mode == 'minigame':
            self.doneStatus = {'loader': 'minigame',
             'where': 'minigame',
             'hoodId': self.loader.hood.id,
             'zoneId': doneStatus['zoneId'],
             'shardId': None,
             'minigameId': doneStatus['minigameId']}
            messenger.send(self.doneEvent)
        else:
            self.notify.error('Unknown mode: ' + mode + ' in handleTrolleyDone')
        return

    def debugStartMinigame(self, zoneId, minigameId):
        self.doneStatus = {'loader': 'minigame',
         'where': 'minigame',
         'hoodId': self.loader.hood.id,
         'zoneId': zoneId,
         'shardId': None,
         'minigameId': minigameId}
        messenger.send(self.doneEvent)
        return

    def enterTFACallback(self, requestStatus, doneStatus):
        self.tfa.exit()
        del self.tfa
        doneStatusMode = doneStatus['mode']
        if doneStatusMode == 'complete':
            self.requestLeave(requestStatus)
        elif doneStatusMode == 'incomplete':
            self.fsm.request('TFAReject')
        else:
            self.notify.error('Unknown mode: %s' % doneStatusMode)

    def enterDFACallback(self, requestStatus, doneStatus):
        self.dfa.exit()
        del self.dfa
        ds = doneStatus['mode']
        if ds == 'complete':
            self.fsm.request('NPCFA', [requestStatus])
        elif ds == 'incomplete':
            self.fsm.request('DFAReject')
        else:
            self.notify.error('Unknown done status for DownloadForceAcknowledge: ' + repr(doneStatus))

    def enterHFA(self, requestStatus):
        self.acceptOnce(self.hfaDoneEvent, self.enterHFACallback, [requestStatus])
        self.hfa = HealthForceAcknowledge.HealthForceAcknowledge(self.hfaDoneEvent)
        self.hfa.enter(1)

    def exitHFA(self):
        self.ignore(self.hfaDoneEvent)

    def enterHFACallback(self, requestStatus, doneStatus):
        self.hfa.exit()
        del self.hfa
        if doneStatus['mode'] == 'complete':
            if requestStatus.get('partyHat', 0):
                outHow = {'teleportIn': 'tunnelOut'}
            else:
                outHow = {'teleportIn': 'teleportOut',
                 'tunnelIn': 'tunnelOut',
                 'doorIn': 'doorOut'}
            self.fsm.request(outHow[requestStatus['how']], [requestStatus])
        elif doneStatus['mode'] == 'incomplete':
            self.fsm.request('HFAReject')
        else:
            self.notify.error('Unknown done status for HealthForceAcknowledge: ' + repr(doneStatus))

    def enterHFAReject(self):
        self.fsm.request('walk')

    def exitHFAReject(self):
        pass

    def enterNPCFA(self, requestStatus):
        self.acceptOnce(self.npcfaDoneEvent, self.enterNPCFACallback, [requestStatus])
        self.npcfa = NPCForceAcknowledge.NPCForceAcknowledge(self.npcfaDoneEvent)
        self.npcfa.enter()

    def exitNPCFA(self):
        self.ignore(self.npcfaDoneEvent)

    def enterNPCFACallback(self, requestStatus, doneStatus):
        self.npcfa.exit()
        del self.npcfa
        if doneStatus['mode'] == 'complete':
            self.fsm.request('HFA', [requestStatus])
        elif doneStatus['mode'] == 'incomplete':
            self.fsm.request('NPCFAReject')
        else:
            self.notify.error('Unknown done status for NPCForceAcknowledge: ' + repr(doneStatus))

    def enterNPCFAReject(self):
        self.fsm.request('walk')

    def exitNPCFAReject(self):
        pass

    def enterWalk(self, teleportIn = 0):
        if self.deathAckBox:
            self.ignore('deathAck')
            self.deathAckBox.cleanup()
            self.deathAckBox = None
        BattlePlace.BattlePlace.enterWalk(self, teleportIn)

    def enterDeathAck(self, requestStatus):
        self.deathAckBox = None
        self.fsm.request('teleportIn', [requestStatus])

    def exitDeathAck(self):
        if self.deathAckBox:
            self.ignore('deathAck')
            self.deathAckBox.cleanup()
            self.deathAckBox = None

    def _placeTeleportInPostZoneComplete(self, requestStatus):
        # see if someone else is already showing a dialog
        if self.dialog:
            x, y, z, h, p, r = base.cr.hoodMgr.getPlaygroundCenterFromId(self.loader.hood.id)

        # See if we're sad
        elif base.localAvatar.getHp() < 1:
            requestStatus['nextState'] = 'popup'
            x, y, z, h, p, r = base.cr.hoodMgr.getPlaygroundCenterFromId(self.loader.hood.id)
            self.accept('deathAck', self.__handleDeathAck, extraArgs=[requestStatus])
            self.deathAckBox = DeathForceAcknowledge.DeathForceAcknowledge(doneEvent='deathAck')

            # re-enable unites after getting back from battle if we don't have a timer already
            if not base.localAvatar.uniteTimerActive:
                base.localAvatar.unitesDisabled['realtime'] = False
                messenger.send(TTSCUniteStateChangedEvent)

        # Check to see if the toon has a tier zero quest
        elif QuestGlobals.isInTutorial(base.localAvatar) and self.loader.hood.id == ToontownGlobals.ToontownCentral:
            # camera sweep.
            requestStatus['nextState'] = 'Movie'
            x, y, z, h, p, r = base.cr.hoodMgr.getDropPoint(base.cr.hoodMgr.ToontownCentralInitialDropPoints)

        else:
            # ...this toon has completed their Flippy quest.
            # Choose a random location within the safezone to drop you.
            # We do this even if we plan to be teleporting to a toon,
            # because the gotoToon option may fail if the toon has moved on.
            requestStatus['nextState'] = 'walk'
            x, y, z, h, p, r = base.cr.hoodMgr.getPlaygroundCenterFromId(self.loader.hood.id)

        # toon may not be parented to hidden at this point, if say the boat or piano on-floor event has detected an
        # intersection (which seems to occur when Toon who lost a connection in battle re-enters in melodyland).
        # In that case, it would be parented to the moving platform, and for that case the coords below are wrong,
        # so before doing a setPos, reparent to hidden.
        base.localAvatar.detachNode()
        base.localAvatar.setPosHpr(render, x, y, z, h, p, r)
        BattlePlace.BattlePlace._placeTeleportInPostZoneComplete(self, requestStatus)

    def enterTeleportIn(self, requestStatus):
        BattlePlace.BattlePlace.enterTeleportIn(self, requestStatus)

    def __cleanupDialog(self, value):
        if self.dialog:
            self.dialog.cleanup()
            self.dialog = None
        if hasattr(self, 'fsm'):
            self.fsm.request('walk', [1])

    def __handleDeathAck(self, requestStatus):
        if self.deathAckBox:
            self.ignore('deathAck')
            self.deathAckBox.cleanup()
            self.deathAckBox = None
        self.fsm.request('walk', [1])

    def enterPopup(self, teleportIn = 0):
        if base.localAvatar.hp < 1:
            base.localAvatar.b_setAnimState('Sad', 1)
        else:
            base.localAvatar.b_setAnimState('neutral', 1.0)
        self.accept('teleportQuery', self.handleTeleportQuery)
        base.localAvatar.setTeleportAvailable(1)
        base.localAvatar.startSleepWatch(self.__handleFallingAsleepPopup)

    def exitPopup(self):
        base.localAvatar.stopSleepWatch()
        base.localAvatar.setTeleportAvailable(0)
        self.ignore('teleportQuery')

    def __handleFallingAsleepPopup(self, task):
        if hasattr(self, 'fsm'):
            self.fsm.request('walk')
            base.localAvatar.forceGotoSleep()
        return Task.done

    def enterTeleportOut(self, requestStatus):
        BattlePlace.BattlePlace.enterTeleportOut(self, requestStatus, self.__teleportOutDone)

    def __teleportOutDone(self, requestStatus):
        teleportDebug(requestStatus, 'Playground.__teleportOutDone(%s)' % (requestStatus,))
        if hasattr(self, 'activityFsm'):
            self.activityFsm.requestFinalState()
        hoodId = requestStatus['hoodId']
        zoneId = requestStatus['zoneId']
        avId = requestStatus['avId']
        shardId = requestStatus['shardId']
        if hoodId == self.loader.hood.hoodId and zoneId == self.loader.hood.hoodId and shardId == None:
            teleportDebug(requestStatus, 'same playground')
            self.fsm.request('deathAck', [requestStatus])
        elif hoodId == ToontownGlobals.MyEstate:
            teleportDebug(requestStatus, 'estate')
            self.getEstateZoneAndGoHome(requestStatus)
        else:
            teleportDebug(requestStatus, 'different hood/zone')
            self.doneStatus = requestStatus
            messenger.send(self.doneEvent)

    def exitTeleportOut(self):
        BattlePlace.BattlePlace.exitTeleportOut(self)

    def createPlayground(self, dnaFile):
        dnaBulk = DNABulkLoader(self.loader.dnaStore, (self.safeZoneStorageDNAFile,))
        dnaBulk.loadDNAFiles()
        node = loader.loadDNAFile(self.loader.dnaStore, dnaFile)
        if node.getNumParents() == 1:
            self.geom = NodePath(node.getParent(0))
            self.geom.reparentTo(hidden)
        else:
            self.geom = hidden.attachNewNode(node)
        self.makeDictionaries(self.loader.dnaStore)
        self.tunnelOriginList = base.cr.hoodMgr.addLinkTunnelHooks(self, self.nodeList, self.zoneId)
        self.geom.flattenMedium()
        gsg = base.win.getGsg()
        if gsg:
            self.geom.prepareScene(gsg)

    def makeDictionaries(self, dnaStore):
        self.nodeList = []
        for i in range(dnaStore.getNumDNAVisGroups()):
            groupFullName = dnaStore.getDNAVisGroupName(i)
            groupName = base.cr.hoodMgr.extractGroupName(groupFullName)
            groupNode = self.geom.find('**/' + groupFullName)
            if groupNode.isEmpty():
                self.notify.error('Could not find visgroup')
            self.nodeList.append(groupNode)

        self.removeLandmarkBlockNodes()
        self.loader.dnaStore.resetPlaceNodes()
        self.loader.dnaStore.resetDNAGroups()
        self.loader.dnaStore.resetDNAVisGroups()
        self.loader.dnaStore.resetDNAVisGroupsAI()

    def removeLandmarkBlockNodes(self):
        npc = self.geom.findAllMatches('**/suit_building_origin')
        for i in range(npc.getNumPaths()):
            npc.getPath(i).removeNode()

    def enterTFA(self, requestStatus):
        self.acceptOnce(self.tfaDoneEvent, self.enterTFACallback, [requestStatus])
        self.tfa = TutorialForceAcknowledge.TutorialForceAcknowledge(self.tfaDoneEvent)
        self.tfa.enter()

    def exitTFA(self):
        self.ignore(self.tfaDoneEvent)

    def enterTFAReject(self):
        self.fsm.request('walk')

    def exitTFAReject(self):
        pass

    def enterZone(self, zoneId):
        pass


    def playPlaygroundTut(self):
        # func so can be executed mid Seq
        def getInitPos():
            self.initPos = base.camera.getPos() + (0, 0, base.localAvatar.getClampedAvatarHeight())
            self.initHpr = base.camera.getHpr()

        self.loadTutorialHead() # load outside Seq
        self.initPos = (0,0,0)
        self.initHpr = (0,0,0)

        track1 = Sequence(
            Func(base.localAvatar.stopUpdateSmartCamera),
            Func(base.localAvatar.loop, 'neutral'),
            Func(base.localAvatar.stopChat),
            Func(base.localAvatar.expBar.hide),
            Wait(2),
            Func(getInitPos),
            LerpPosInterval(base.camera, duration=2, pos=(0, -22, 2), blendType="easeInOut" ), # zoom out
            Func(base.camera.wrtReparentTo, render),
            Func(self.tutorialFrame.show),
            Func(self.flippyHead.setLocalPageChat, "Say, I heard you graduated training! Con-grad-ulations!\x07Welcome to Toontown Central, let me show you around some of the most important landmarks."),
            Func(self.acceptOnce, 'doneChatPage', lambda event: track2.start())
        )

        track2 = Sequence(
            LerpPosHprInterval(base.camera, duration=3, pos=(-1.4, -5, 21), hpr=(225, 0,0), blendType="easeInOut"),
            Func(self.flippyHead.setLocalPageChat, "This is a Toon Headquarters, or Toon HQ. Outposts like these are set up all over Toontown!\x07Each one has HQ Officers inside to help Toons. This one happens to be where some of our best Resistance Rangers are stationed, like Lord Lowden Clear!\x07You'll visit the Rangers soon, so let's move on."),
            Func(self.acceptOnce, 'doneChatPage', lambda event: track3.start())
        )

        track3 = Sequence(
            LerpPosHprInterval(base.camera, duration=3, pos=(-57, -20.5, 15), hpr=(180, 0,0), blendType="easeInOut"),
            Func(self.flippyHead.setLocalPageChat, "Here's Toontown Central's Gag Shop! You can buy Gags inside, but that requires Jellybeans!\x07You can earn Jellybeans through battles, completing quests, fishing, playing table games, and trolley games!\x07Speaking of which..."),
            Func(self.acceptOnce, 'doneChatPage', lambda event: track4.start())
        )

        track4 = Sequence(
            LerpHprInterval(base.camera, duration=2, hpr=(150,0,0), blendType="easeInOut"),
            Func(self.flippyHead.setLocalPageChat, "The trolley! Hop on with some Toons or by yourself to play some Toontastic minigames while earning Jellybeans!\x07Now, I think those are the most important playground buildings...\x07Oh yes! How could I forget!"),
            Func(self.acceptOnce, 'doneChatPage', lambda event: track5.start())
        )

        track5 = Sequence(
            LerpHprInterval(base.camera, duration=2, hpr=(123,0,0), blendType="easeInOut"),
            Func(self.flippyHead.setLocalPageChat, "I'm here in Toon Hall! Please, come inside so I can give you a proper Toontown welcome!"),
            Func(self.acceptOnce, 'doneChatPage', lambda event: (print('track5 doneChatPage fired'), backToPlayer()))
        )

        # function so Seq isnt determined at start
        def backToPlayer():
            track = Sequence(
                Func(base.camera.wrtReparentTo, base.localAvatar),
                LerpPosHprInterval(base.camera, duration=2, pos=self.initPos, hpr=self.initHpr, blendType="easeInOut"),
                Func(self.flippyHead.delete),
                Func(self.tutorialFrame.destroy),
                Wait(1),
                Func(self.fsm.request, 'walk'),
                Func(base.localAvatar.startUpdateSmartCamera),
                Func(base.localAvatar.controlManager.enable),
                Func(base.localAvatar.startChat),
                Func(base.localAvatar.expBar.show)
            )
            track.start()

        track1.start()

    def loadTutorialHead(self):
        self.flippyHead = NPCToons.createLocalNPC(2001)
        self.tutorialFrame = MiniScaledToonHeadFrame(self.flippyHead, wantLookAround=False)
        self.tutorialFrame.reparentTo(base.a2dBottomLeft)
        self.tutorialFrame.setPos(0.2, 0, 0.3)
        self.tutorialFrame.hide()
