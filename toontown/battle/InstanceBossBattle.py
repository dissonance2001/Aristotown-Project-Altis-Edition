from pandac.PandaModules import *
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM, State
from otp.distributed.TelemetryLimiter import RotationLimitToH, TLGatherAllAvs
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownBattleGlobals
from toontown.battle import BattlePlace


class InstanceBossBattle(BattlePlace.BattlePlace):
    notify = DirectNotifyGlobal.directNotify.newCategory('InstanceBossBattle')

    def __init__(self, loader, parentFSM, doneEvent):
        BattlePlace.BattlePlace.__init__(self, loader, doneEvent)
        self.parentFSM = parentFSM
        self.controller = None
        self.teleportInPosHpr = (0, 0, 0, 0, 0, 0)
        self.fsm = ClassicFSM.ClassicFSM('InstanceBossBattle', [State.State('start', self.enterStart, self.exitStart, ['walk',
          'tunnelIn',
          'teleportIn',
          'movie']),
         State.State('battle', self.enterBattle, self.exitBattle, ['walk', 'died', 'movie']),
         State.State('finalBattle', self.enterFinalBattle, self.exitFinalBattle, ['walk',
          'stickerBook',
          'teleportOut',
          'died',
          'tunnelOut',
          'DFA',
          'battle',
          'movie',
          'ouch',
          'crane',
          'WaitForBattle',
          'squished']),
         State.State('movie', self.enterMovie, self.exitMovie, ['walk',
          'battle',
          'finalBattle',
          'died',
          'teleportOut']),
         State.State('ouch', self.enterOuch, self.exitOuch, ['walk',
          'battle',
          'finalBattle',
          'died',
          'crane']),
         State.State('crane', self.enterCrane, self.exitCrane, ['walk',
          'battle',
          'finalBattle',
          'died',
          'ouch',
          'squished']),
         State.State('walk', self.enterWalk, self.exitWalk, ['stickerBook',
          'teleportOut',
          'died',
          'tunnelOut',
          'DFA',
          'battle',
          'movie',
          'ouch',
          'crane',
          'finalBattle',
          'WaitForBattle']),
         State.State('stickerBook', self.enterStickerBook, self.exitStickerBook, ['walk',
          'DFA',
          'WaitForBattle',
          'movie',
          'battle']),
         State.State('WaitForBattle', self.enterWaitForBattle, self.exitWaitForBattle, ['battle', 'walk', 'movie']),
         State.State('DFA', self.enterDFA, self.exitDFA, ['DFAReject', 'teleportOut', 'tunnelOut']),
         State.State('DFAReject', self.enterDFAReject, self.exitDFAReject, ['walk']),
         State.State('teleportIn', self.enterTeleportIn, self.exitTeleportIn, ['walk']),
         State.State('teleportOut', self.enterTeleportOut, self.exitTeleportOut, ['teleportIn', 'final', 'WaitForBattle']),
         State.State('died', self.enterDied, self.exitDied, ['final']),
         State.State('tunnelIn', self.enterTunnelIn, self.exitTunnelIn, ['walk']),
         State.State('tunnelOut', self.enterTunnelOut, self.exitTunnelOut, ['final']),
         State.State('squished', self.enterSquished, self.exitSquished, ['finalBattle',
          'crane',
          'died',
          'teleportOut']),
         State.State('final', self.enterFinal, self.exitFinal, ['start'])], 'start', 'final')

    def getTaskZoneId(self):
        return base.cr.playGame.hood.id

    def enter(self, requestStatus, controller):
        self.zoneId = requestStatus['zoneId']
        BattlePlace.BattlePlace.enter(self)
        self.fsm.enterInitialState()
        self.controller = controller
        if self.controller:
            self.controller.d_avatarEnter()
        self._telemLimiter = TLGatherAllAvs('InstanceBossBattle', RotationLimitToH)
        base.localAvatar.inventory.setRespectInvasions(0)
        self.fsm.request(requestStatus['how'], [requestStatus])

    def exit(self):
        self.fsm.requestFinalState()
        base.localAvatar.inventory.setRespectInvasions(1)
        if self.controller:
            self.controller.d_avatarExit()
        self.controller = None
        self._telemLimiter.destroy()
        del self._telemLimiter
        BattlePlace.BattlePlace.exit(self)

    def enterBattle(self, event):
        messenger.send('toonEnteredBattle', ['changemusic'])
        base.localAvatar.isInBattle = True
        mult = 1
        if self.controller:
            mult = ToontownBattleGlobals.getBossBattleCreditMultiplier(self.controller.battleNumber)
        self.townBattle.enter(event, self.fsm.getStateNamed('battle'), bldg=1, creditMultiplier=mult)
        base.localAvatar.b_setAnimState('off', 1)
        base.localAvatar.setTeleportAvailable(0)
        base.localAvatar.cantLeaveGame = 1

    def exitBattle(self):
        base.localAvatar.isInBattle = False
        self.townBattle.exit()

    def enterFinalBattle(self):
        self.walkStateData.enter()
        self.walkStateData.fsm.request('walking')
        base.localAvatar.setTeleportAvailable(0)
        base.localAvatar.setTeleportAllowed(0)
        base.localAvatar.cantLeaveGame = 0
        base.localAvatar.book.hideButton()
        self.ignore(ToontownGlobals.StickerBookHotkey)
        self.ignore('enterStickerBook')
        self.ignore(ToontownGlobals.OptionsPageHotkey)

    def exitFinalBattle(self):
        self.walkStateData.exit()
        base.localAvatar.setTeleportAllowed(1)

    def enterMovie(self, requestStatus=None):
        base.localAvatar.setTeleportAvailable(0)

    def exitMovie(self):
        pass

    def enterOuch(self):
        base.localAvatar.setTeleportAvailable(0)
        base.localAvatar.laffMeter.start()

    def exitOuch(self):
        base.localAvatar.laffMeter.stop()

    def enterCrane(self):
        base.localAvatar.setTeleportAvailable(0)
        base.localAvatar.laffMeter.start()
        base.localAvatar.collisionsOn()

    def exitCrane(self):
        base.localAvatar.collisionsOff()
        base.localAvatar.laffMeter.stop()

    def enterWalk(self, teleportIn=0):
        BattlePlace.BattlePlace.enterWalk(self, teleportIn)
        self.ignore('teleportQuery')
        base.localAvatar.setTeleportAvailable(0)
        base.localAvatar.setTeleportAllowed(0)
        base.localAvatar.book.hideButton()
        self.ignore(ToontownGlobals.StickerBookHotkey)
        self.ignore('enterStickerBook')
        self.ignore(ToontownGlobals.OptionsPageHotkey)
        self.ignore(self.walkDoneEvent)

    def exitWalk(self):
        BattlePlace.BattlePlace.exitWalk(self)
        base.localAvatar.setTeleportAllowed(1)

    def enterStickerBook(self, page=None):
        BattlePlace.BattlePlace.enterStickerBook(self, page)
        self.ignore('teleportQuery')
        base.localAvatar.setTeleportAvailable(0)

    def enterSit(self):
        BattlePlace.BattlePlace.enterSit(self)
        self.ignore('teleportQuery')
        base.localAvatar.setTeleportAvailable(0)

    def enterTeleportIn(self, requestStatus):
        base.localAvatar.detachNode()
        base.localAvatar.setPosHpr(*self.teleportInPosHpr)
        BattlePlace.BattlePlace.enterTeleportIn(self, requestStatus)

    def enterTeleportOut(self, requestStatus):
        BattlePlace.BattlePlace.enterTeleportOut(self, requestStatus, self.__teleportOutDone)

    def __teleportOutDone(self, requestStatus):
        hoodId = requestStatus['hoodId']
        if hoodId == ToontownGlobals.MyEstate:
            self.getEstateZoneAndGoHome(requestStatus)
        else:
            self.doneStatus = requestStatus
            messenger.send(self.doneEvent)

    def enterSquished(self):
        base.localAvatar.laffMeter.start()
        base.localAvatar.b_setAnimState('Flattened')

    def handleSquishDone(self, extraArgs=[]):
        base.cr.playGame.getPlace().setState('walk')

    def exitSquished(self):
        taskMgr.remove(base.localAvatar.uniqueName('finishSquishTask'))
        base.localAvatar.laffMeter.stop()
