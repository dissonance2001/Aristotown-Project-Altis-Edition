from panda3d.core import ConfigVariableBool, CollisionEntry
from direct.showbase.MessengerGlobal import messenger
from direct.task.TaskManagerGlobal import taskMgr

from toontown.hood import Place, ZoneUtil
from toontown.toonbase import ToontownGlobals


class BattlePlace(Place.Place):
    def __init__(self, loader, doneEvent):
        Place.Place.__init__(self, loader, doneEvent)
        self.playingSong = None

    def load(self, gagMult = 1, countInvasions = False):
        Place.Place.load(self)
        # Check the battle credit multiplier, update if necessary
        base.localAvatar.inventory.setBattleCreditMult(gagMult, countInvasions = countInvasions)

    def unload(self):
        Place.Place.unload(self)

    def setState(self, state, battleEvent=None):
        if battleEvent:
            if not self.request(state, battleEvent):
                self.notify.warning("fsm.request('%s') returned 0 (zone id %s, avatar pos %s)." % (state, self.zoneId, base.localAvatar.getPos(render)))
        elif not self.request(state):
            self.notify.warning("fsm.request('%s') returned 0 (zone id %s, avatar pos %s)." % (state, self.zoneId, base.localAvatar.getPos(render)))

    def enterWalk(self, flag = 0):
        Place.Place.enterWalk(self, flag)
        self.accept('enterBattle', self.handleBattleEntry)

    def exitWalk(self):
        Place.Place.exitWalk(self)
        self.ignore('enterBattle')

    def enterWaitForBattle(self):
        base.localAvatar.b_setAnimState('Neutral', 1)

    def exitWaitForBattle(self):
        pass

    def enterBattle(self, event):
        base.localAvatar.setTeleportAllowed(0)
        
        # Let the Friends List Manager operate during battle.
        # This is what allows for toons to click on avatars during
        # a battle.
        self.enterFLM()

        overrideMusicFlag = 0
        if ConfigVariableBool('want-qa-regression', False).getValue():
            self.notify.info('QA-REGRESSION: COGBATTLE: Enter Battle')
        # If music is currently playing, force stop it and reset it
        # This is a bugfix for the infamous music bug.
        if base.musicMgr.isMusicPlaying(self.loader.music):
            base.musicMgr.stopMusic(self.loader.music)
            self.playingSong = self.loader.music
        if hasattr(self.loader, 'factoryExtMusic'):
            if base.musicMgr.isMusicPlaying(self.loader.factoryExtMusic):
                base.musicMgr.stopMusic(self.loader.factoryExtMusic)
                self.playingSong = self.loader.factoryExtMusic
                overrideMusicFlag = 1
        if hasattr(self.loader, 'lobbyMusic'):
            if base.musicMgr.isMusicPlaying(self.loader.lobbyMusic):
                base.musicMgr.stopMusic(self.loader.lobbyMusic)
                self.playingSong = self.loader.lobbyMusic

        # Start the battle tunes
        if overrideMusicFlag:
            base.musicMgr.playMusic(self.loader.factoryExtBattleMusic, looping=1, volume=0.9)
        elif self.loader.battleMusic != 'None':
            base.musicMgr.playMusic(self.loader.battleMusic, looping=1, volume=0.9)

        self.enterTownBattle(event)
        # Make sure the toon's anim state gets reset
        base.localAvatar.b_setAnimState('Neutral', 1)
        # A query for a teleport location might come along while we're
        # in battle, which is acceptable.  We should handle it, so
        # friends can teleport to us to help us out.
        # We can't put this handler in the TownBattle object, because
        # it doesn't know what zone or hood we're in.
        self.accept('teleportQuery', self.handleTeleportQuery)
        # Disable leaving and allow teleports coming in
        base.localAvatar.setTeleportAvailable(1)
        messenger.send('levelEnterBattle')

    def enterTownBattle(self, event):
        self.loader.townBattle.enter(event, 'battle', isStreet= True)

    def exitBattle(self):
        base.localAvatar.setTeleportAllowed(1)
        self.loader.townBattle.exit()
        if self.loader.battleMusic != 'None':
            base.musicMgr.stopMusic(self.loader.battleMusic)
        try:
            base.musicMgr.playMusic(self.playingSong, looping=1, volume=0.8)
        except:
            pass  # Hacky fix for facilities, since it overrides the music
        base.localAvatar.setTeleportAvailable(0)
        self.ignore('teleportQuery')
        messenger.send('levelExitBattle')

    def handleBattleEntry(self):
        self.request('Battle')

    def enterFallDown(self, extraArgs = []):
        # exitWalk hides the laffmeter, so start it here
        base.cr.gameGui.laffMeter.start()
        # Play the 'slip backwards' animation
        base.localAvatar.b_setAnimState('FallDown', callback=self.handleFallDownDone, extraArgs=extraArgs)

    def handleFallDownDone(self):
        # Put place back in walk state after squish is done
        base.cr.playGame.getPlace().setState('Walk')

    def exitFallDown(self):
        base.cr.gameGui.laffMeter.stop()

    def enterSquished(self):
        # exitWalk hides the laffmeter, so start it here
        base.cr.gameGui.laffMeter.start()
        # Play the 'squish' animation
        base.localAvatar.b_setAnimState('Squish')
        # Put toon back in walk state after a couple seconds
        taskMgr.doMethodLater(2.0, self.handleSquishDone, base.localAvatar.uniqueName('finishSquishTask'))

    def handleSquishDone(self, extraArgs = []):
        # put place back in walk state after squish is done
        base.cr.playGame.getPlace().setState('Walk')

    def exitSquished(self):
        taskMgr.remove(base.localAvatar.uniqueName('finishSquishTask'))
        base.cr.gameGui.laffMeter.stop()

    def enterZone(self, newZone):
        """
        Puts the toon in the indicated zone.  newZone may either be a
        CollisionEntry object as determined by a floor polygon, or an
        integer zone id.  It may also be None, to indicate no zone.
        """
        if isinstance(newZone, CollisionEntry):
            # Get the name of the collide node
            try:
                newZoneId = int(newZone.getIntoNode().getName())
                townLoader = base.cr.playGame.getPlace().loader
                groupNode = townLoader.zoneDict.get(newZoneId)
                if groupNode is not None:
                    fadeOutSeq = townLoader.fadeOutDict.get(groupNode)
                    if fadeOutSeq is not None:
                        if fadeOutSeq.isPlaying():
                            self.notify.info(f'Skipping collision with node in zone {newZoneId} because it was fading out.')
                            return
            except Exception:
                self.notify.warning('Invalid floor collision node in street: %s' % newZone.getIntoNode().getName())
                return
        else:
            newZoneId = newZone
        self.doEnterZone(newZoneId)

    def doEnterZone(self, newZoneId):
        """
        Puts the Toon in the indicated zone, which is an integer
        number.  This is overridden in Street.py to implement
        zone-based visibility of geometry.
        """
        if newZoneId != self.zoneId:
            # Tell the server that we changed zones
            if newZoneId is not None:
                if hasattr(self, 'zoneVisDict'):
                    visList = self.zoneVisDict[newZoneId]
                else:
                    visList = base.cr.playGame.getPlace().loader.zoneVisDict[newZoneId]
                base.cr.sendSetZoneMsg(newZoneId, visList)
                self.notify.debug('Entering Zone %d' % newZoneId)
            # The new zone is now old
            self.zoneId = newZoneId

    def genDNAFileName(self, zoneId):
        zoneId = ZoneUtil.getTrueZoneId(zoneId, zoneId)
        hoodId = ZoneUtil.getCanonicalHoodId(zoneId)
        hood = ToontownGlobals.dnaMap[hoodId]
        phase = ToontownGlobals.streetPhaseMap[hoodId]
        if zoneId == 20000:
            phase = 4
        if hoodId == zoneId:
            zoneId = 'sz'
        return 'phase_%s/dna/%s_%s.pdna' % (phase, hood, zoneId)
