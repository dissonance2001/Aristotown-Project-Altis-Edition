from __future__ import absolute_import
from pandac.PandaModules import *
from toontown.hood import Place, ZoneUtil
from toontown.toon import Toon
from toontown.toonbase import ToontownGlobals

class BattlePlace(Place.Place):

    def __init__(self, loader, doneEvent):
        Place.Place.__init__(self, loader, doneEvent)

    def load(self):
        Place.Place.load(self)
        Toon.loadBattleAnims()

    def setState(self, state, battleEvent = None):
        if battleEvent:
            if not self.fsm.request(state, [battleEvent]):
                self.notify.warning("fsm.request('%s') returned 0 (zone id %s, avatar pos %s)." % (state, self.zoneId, base.localAvatar.getPos(render)))
        elif not self.fsm.request(state):
            self.notify.warning("fsm.request('%s') returned 0 (zone id %s, avatar pos %s)." % (state, self.zoneId, base.localAvatar.getPos(render)))

    def enterWalk(self, flag = 0):
        base.localAvatar.isInBattle = False
        Place.Place.enterWalk(self, flag)
        self.accept('enterBattle', self.handleBattleEntry)

    def exitWalk(self):
        Place.Place.exitWalk(self)
        self.ignore('enterBattle')

    def enterWaitForBattle(self):
        messenger.send('toonEnteredBattle', ['changemusic'])
        base.localAvatar.isInBattle = True
        base.localAvatar.b_setAnimState('neutral', 1)

    def exitWaitForBattle(self):
        pass

    def enterBattle(self, event):
        messenger.send('toonEnteredBattle', ['changemusic'])
        base.localAvatar.isInBattle = True
        if base.config.GetBool('want-qa-regression', 0):
            self.notify.info('QA-REGRESSION: COGBATTLE: Enter Battle')
        self.loader.music.stop()
        base.playMusic(self.loader.battleMusic, looping=1, volume=0.9)
        self.enterTownBattle(event)
        self.enterFLM()
        base.localAvatar.b_setAnimState('off', 1)
        self.accept('teleportQuery', self.handleTeleportQuery)
        base.localAvatar.setTeleportAvailable(1)
        base.localAvatar.cantLeaveGame = 1

    def enterTownBattle(self, event):
        self.loader.townBattle.enter(event, self.fsm.getStateNamed('battle'))

    def exitBattle(self):
        # base.localAvatar.makeUnCooldown()
        # base.localAvatar.makeUnBurned()
        # base.localAvatar.makeUnDamageOvertime()
        # base.localAvatar.makeUnBurned()
        # base.localAvatar.makeUnGroupDamageDown()
        # base.localAvatar.makeUnGagBoost()
        # base.localAvatar.makeUnCooldown()
        # base.localAvatar.makeUnMarkedWood()
        # base.localAvatar.makeUnInkDrain()
        # base.localAvatar.makeUnHidden()
        # base.localAvatar.makeUnCollectCalled()
        # base.localAvatar.makeUnNoDodge()
        # base.localAvatar.makeUnConfused()
        # base.localAvatar.makeUnMandatoryToll()
        # base.localAvatar.makeUnCheer()
        # base.localAvatar.makeUnDamageUp()
        # base.localAvatar.makeUnDamageUpGovernaught()
        # base.localAvatar.makeUnDamageDown()
        # base.localAvatar.makeUnDamageUp()
        # base.localAvatar.makeUnEncore()
        # base.localAvatar.makeUnWinded()
        # base.localAvatar.makeUnBombed()
        # base.localAvatar.makeUnGagBan()
        # base.localAvatar.makeUnVulnerable()
        # base.localAvatar.makeUnSnapped()
        base.localAvatar.isInBattle = False
        self.loader.townBattle.exit()
        self.loader.battleMusic.stop()
        base.playMusic(self.loader.music, looping=1, volume=0.8)
        base.localAvatar.cantLeaveGame = 0
        base.localAvatar.setTeleportAvailable(0)
        self.ignore('teleportQuery')

    def handleBattleEntry(self):
        messenger.send('toonEnteredBattle', ['changemusic'])
        base.localAvatar.isInBattle = True
        self.fsm.request('battle')

    def enterFallDown(self, extraArgs = []):
        base.localAvatar.laffMeter.start()
        base.localAvatar.b_setAnimState('FallDown', callback=self.handleFallDownDone, extraArgs=extraArgs)

    def handleFallDownDone(self):
        base.cr.playGame.getPlace().setState('walk')

    def exitFallDown(self):
        base.localAvatar.laffMeter.stop()

    def enterSquished(self):
        base.localAvatar.laffMeter.start()
        base.localAvatar.b_setAnimState('Squish')
        taskMgr.doMethodLater(2.0, self.handleSquishDone, base.localAvatar.uniqueName('finishSquishTask'))

    def handleSquishDone(self, extraArgs = []):
        base.cr.playGame.getPlace().setState('walk')

    def exitSquished(self):
        taskMgr.remove(base.localAvatar.uniqueName('finishSquishTask'))
        base.localAvatar.laffMeter.stop()

    def enterZone(self, newZone):
        if isinstance(newZone, CollisionEntry):
            try:
                newZoneId = int(newZone.getIntoNode().getName())
            except:
                self.notify.warning('Invalid floor collision node in street: %s' % newZone.getIntoNode().getName())
                return
        else:
            newZoneId = newZone
        self.doEnterZone(newZoneId)

    def doEnterZone(self, newZoneId):
        if newZoneId != self.zoneId:
            if newZoneId != None:
                if hasattr(self, 'zoneVisDict'):
                    visList = self.zoneVisDict[newZoneId]
                else:
                    visList = base.cr.playGame.getPlace().loader.zoneVisDict[newZoneId]
                base.cr.sendSetZoneMsg(newZoneId, visList)
                self.notify.debug('Entering Zone %d' % newZoneId)
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