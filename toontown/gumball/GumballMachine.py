from direct.actor.Actor import Actor
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectFrame
from direct.interval.IntervalGlobal import Sequence, Parallel, Func, Wait, LerpPosInterval, LerpScaleInterval, LerpColorScaleInterval, LerpHprInterval
from pandac.PandaModules import CardMaker, CollisionNode, CollisionTube, TextNode, TransparencyAttrib, Vec3
from toontown.gumball.GumballMachineGUI import GumballMachineGUI
from toontown.toonbase import ToontownGlobals

class GumballMachine(Actor):
    TRANSITION_LENGTH = 1.0

    def __init__(self, interior):
        Actor.__init__(self)
        self.interior = interior
        self.gui = None
        self.promptText = None
        self.redeemTrack = None
        self.redeemVisualTrack = None
        self.redeemVisualNodes = []
        self.redeemGuiStartPos = None
        self.openTrack = None
        self.opening = False
        self.avatarLocked = False
        self.gumballMusic = None
        self.previousMusic = None
        self.previousMusicTime = 0.0
        self.previousMusicVolume = 0.7
        self.redeemSfx = None
        self.idleSfx = None
        self.fanfareSfx = None
        self.drumrollSfx = None
        self.collisionName = 'GBMCollision-%s' % id(self)
        self.hasClashModel = False
        self._loadModel()
        self._loadAudio()
        self._placeMachine()
        self._setupCollision()

    def _loadModel(self):
        try:
            self.loadModel('phase_3.5/models/char/ttcc_prp_gumballMachine-zero')
            if not self.isEmpty() and not self.getGeomNode().isEmpty():
                self.hasClashModel = True
                self.loadAnims({'idle': 'phase_3.5/models/char/ttcc_prp_gumballMachine-idle', 'activate': 'phase_3.5/models/char/ttcc_prp_gumballMachine-activate', 'redeem': 'phase_3.5/models/char/ttcc_prp_gumballMachine-redeem'})
                self.setBlend(frameBlend=getattr(base, 'wantSmoothAnims', False))
                self.loop('idle')
                return
        except:
            pass
        cm = CardMaker('gumballMachineFallback')
        cm.setFrame(-1.4, 1.4, 0, 3.3)
        card = self.attachNewNode(cm.generate())
        card.setColor(0.15, 0.55, 0.75, 1)
        card.setTransparency(TransparencyAttrib.MAlpha)
        text = TextNode('gumballMachineFallbackText')
        text.setFont(ToontownGlobals.getSignFont())
        text.setAlign(TextNode.ACenter)
        text.setText('GUMBALLS')
        text.setTextColor(1, 0.9, 0.15, 1)
        textNp = self.attachNewNode(text)
        textNp.setPos(0, -0.02, 2.55)
        textNp.setScale(0.38)


    def _loadAudioFile(self, path, music=False):
        candidates = ['resources/' + path, path]
        for candidate in candidates:
            try:
                if music:
                    sound = base.loader.loadMusic(candidate)
                else:
                    sound = base.loader.loadSfx(candidate)
                if sound and sound.length() > 0:
                    return sound
            except:
                pass
        return None

    def _loadAudio(self):
        self.gumballMusic = self._loadAudioFile('phase_3.5/audio/bgm/HQ_gumball.ogg', True)
        self.redeemSfx = self._loadAudioFile('phase_3.5/audio/sfx/ttcc_prp_gumballMachine-redeem.ogg')
        self.idleSfx = self._loadAudioFile('phase_3.5/audio/sfx/ttcc_prp_gumballMachine-idle.ogg')
        self.drumrollSfx = self._loadAudioFile('phase_5/audio/sfx/SZ_MM_drumroll.ogg')
        self.fanfareSfx = self._loadAudioFile('phase_5/audio/sfx/SZ_MM_fanfare.ogg')
        if not self.fanfareSfx:
            self.fanfareSfx = self._loadAudioFile('phase_3.5/audio/sfx/SZ_MM_fanfare.ogg')
        self._startIdleSfx()

    def _startIdleSfx(self):
        if not self.idleSfx:
            return
        try:
            self.idleSfx.stop()
        except:
            pass
        try:
            self.idleSfx.setLoop(1)
            self.idleSfx.setVolume(0.65)
            self.idleSfx.play()
        except:
            pass

    def _stopIdleSfx(self):
        if self.idleSfx:
            try:
                self.idleSfx.stop()
            except:
                pass

    def _startMusic(self):
        self.previousMusic = None
        self.previousMusicTime = 0.0
        self.previousMusicVolume = 0.7
        try:
            place = base.cr.playGame.getPlace()
            previous = getattr(getattr(place, 'loader', None), 'activityMusic', None)
            if previous and previous is not self.gumballMusic:
                self.previousMusic = previous
                try:
                    self.previousMusicTime = previous.getTime()
                except:
                    self.previousMusicTime = 0.0
                try:
                    self.previousMusicVolume = previous.getVolume()
                except:
                    self.previousMusicVolume = 0.7
                try:
                    previous.stop()
                except:
                    pass
        except:
            pass
        if self.gumballMusic:
            try:
                self.gumballMusic.stop()
            except:
                pass
            try:
                base.playMusic(self.gumballMusic, looping=1, volume=1.0)
            except:
                try:
                    self.gumballMusic.setLoop(1)
                    self.gumballMusic.play()
                except:
                    pass

    def _stopMusic(self, restore=True):
        if self.gumballMusic:
            try:
                self.gumballMusic.stop()
            except:
                pass
        previous = self.previousMusic
        previousTime = self.previousMusicTime
        previousVolume = self.previousMusicVolume
        self.previousMusic = None
        self.previousMusicTime = 0.0
        self.previousMusicVolume = 0.7
        if restore and previous:
            try:
                base.playMusic(previous, looping=1, volume=previousVolume)
                try:
                    previous.setTime(previousTime)
                except:
                    pass
            except:
                try:
                    previous.setLoop(1)
                    previous.setVolume(previousVolume)
                    previous.play()
                    previous.setTime(previousTime)
                except:
                    pass

    def _placeMachine(self):
        locator = self.interior.interior.find('**/gumballMachine_locator')
        if not locator.isEmpty():
            self.reparentTo(locator)
            self.setPosHpr(0, 0, 0, 0, 0, 0)
        else:
            self.reparentTo(self.interior.interior)
            self.setPosHpr(6.8, 8.6, 0, 150, 0, 0)
        if not self.hasClashModel:
            self.setScale(0.75)

    def _setupCollision(self):
        if self.hasClashModel:
            tube = CollisionTube(0, 0, 15, 0, 0, 5, 0.65)
        else:
            tube = CollisionTube(0, 0, 0.3, 0, 0, 2.8, 1.35)
        tube.setTangible(1)
        node = CollisionNode(self.collisionName)
        node.addSolid(tube)
        node.setCollideMask(ToontownGlobals.WallBitmask)
        self.collision = self.attachNewNode(node)
        if self.hasClashModel:
            self.collision.setScale(1.6, 1, 1)
            self.collision.setPos(-0.25, -1.5, -5)
        self.accept('enter' + self.collisionName, self._enterCollision)
        self.accept('exit' + self.collisionName, self._exitCollision)

    def _enterCollision(self, entry):
        if self.gui or self.opening:
            return
        if getattr(base, 'wantInteractKey', False):
            self.accept(base.INTERACT, self.openGUI)
            self.promptText = OnscreenText(text='Press %s to interact with the Gumball Machine' % str(base.INTERACT).upper(), style=3, scale=0.09, parent=base.a2dBottomCenter, fg=(1, 0.9, 0.1, 1), pos=(0, 0.5))
        else:
            self.openGUI()

    def _exitCollision(self, entry=None):
        self.ignore(getattr(base, 'INTERACT', 'shift'))
        if self.promptText:
            self.promptText.removeNode()
            self.promptText = None

    def getOffers(self):
        from toontown.gumball import GumballGlobals
        return GumballGlobals.getOffers(getattr(self.interior, 'zoneId', 0))

    def _lockAvatar(self):
        self.avatarLocked = True
        try:
            base.cr.playGame.getPlace().setState('Stopped')
        except:
            pass
        try:
            base.localAvatar.disableControls()
        except:
            try:
                base.localAvatar.controlManager.disableControls()
            except:
                pass
        try:
            base.localAvatar.stopUpdateSmartCamera()
        except:
            pass
        try:
            base.localAvatar.stop()
        except:
            pass

    def _unlockAvatar(self):
        if not self.avatarLocked:
            return
        self.avatarLocked = False
        try:
            base.cr.playGame.getPlace().setState('Walk')
        except:
            pass
        try:
            base.localAvatar.enableControls()
        except:
            try:
                base.localAvatar.controlManager.enableControls()
            except:
                pass
        try:
            base.localAvatar.startUpdateSmartCamera()
        except:
            pass

    def openGUI(self, entry=None):
        self._exitCollision()
        if self.gui or self.opening:
            return
        self.opening = True
        self._lockAvatar()
        self._startMusic()
        if self.hasClashModel:
            try:
                self.loop('idle')
            except:
                pass
        try:
            camIval = camera.posQuatInterval(self.TRANSITION_LENGTH, Vec3(0, -4, 1.1), Vec3(0, 7, 0), other=self, blendType='easeOut', name='gumballMachineCamera-%s' % id(self))
        except:
            camIval = Wait(self.TRANSITION_LENGTH)
        self.openTrack = Sequence(camIval, Func(self._finishOpenGUI))
        self.openTrack.start()

    def _finishOpenGUI(self):
        self.openTrack = None
        if not self.opening:
            return
        self.gui = GumballMachineGUI(self)
        self.opening = False

    def closeGUI(self, restoreMusic=True):
        self.opening = False
        self._cancelRedeemVisual()
        if self.openTrack:
            self.openTrack.finish()
            self.openTrack = None
        if self.gui:
            gui = self.gui
            self.gui = None
            gui.destroy()
        if self.hasClashModel:
            try:
                self.loop('idle')
            except:
                pass
        self._stopMusic(restoreMusic)
        self._unlockAvatar()

    def requestPurchase(self, offerId):
        if not self.interior:
            return
        self.interior.sendUpdate('requestGumballPurchase', [int(offerId)])

    def purchaseResult(self, status, offerId, resolvedType, endTimestamp):
        if self.gui:
            self.gui.purchaseResult(status, offerId, resolvedType, endTimestamp)
        if int(status) == 0:
            self.doBoosterRedeemSequence(int(resolvedType))

    def _safeAnimDuration(self, animName):
        try:
            return max(0.1, self.getDuration(animName))
        except:
            return 0.1

    def _fadeScreen(self, alpha, duration=0.0):
        try:
            base.transitions.fadeScreen(alpha, t=duration)
        except TypeError:
            try:
                base.transitions.fadeScreen(alpha)
            except:
                pass
        except:
            pass

    def _noFade(self):
        try:
            base.transitions.noFade()
        except:
            pass

    def _playDrumroll(self):
        if self.drumrollSfx:
            try:
                self.drumrollSfx.stop()
            except:
                pass
            try:
                base.playSfx(self.drumrollSfx)
            except:
                try:
                    self.drumrollSfx.play()
                except:
                    pass

    def _playFanfare(self):
        if self.fanfareSfx:
            try:
                self.fanfareSfx.stop()
            except:
                pass
            try:
                base.playSfx(self.fanfareSfx)
            except:
                try:
                    self.fanfareSfx.play()
                except:
                    pass

    def _destroyRedeemNode(self, node):
        if not node:
            return
        try:
            node.destroy()
            return
        except:
            pass
        try:
            node.removeNode()
        except:
            pass

    def _finishRedeemVisual(self):
        self.redeemVisualTrack = None
        self.redeemVisualNodes = []
        self.redeemGuiStartPos = None

    def _cancelRedeemVisual(self):
        if self.redeemVisualTrack:
            try:
                self.redeemVisualTrack.pause()
            except:
                pass
            self.redeemVisualTrack = None
        for sound in (self.drumrollSfx, self.fanfareSfx):
            if sound:
                try:
                    sound.stop()
                except:
                    pass
        for node in self.redeemVisualNodes:
            self._destroyRedeemNode(node)
        self.redeemVisualNodes = []
        if self.gui and self.redeemGuiStartPos is not None:
            try:
                self.gui.setPos(self.redeemGuiStartPos)
            except:
                pass
        self.redeemGuiStartPos = None
        self._noFade()

    def doBoosterRedeemSequence(self, boosterType):
        if not self.gui:
            return
        self._cancelRedeemVisual()
        boosterName = 'Booster'
        try:
            from toontown.gumball import GumballGlobals
            boosterName = GumballGlobals.getBoosterName(boosterType)
        except:
            pass
        boosterNode = None
        try:
            boosterNode = self.gui._boosterNode(boosterType)
        except:
            boosterNode = None
        if boosterNode is not None:
            altModel = DirectFrame(parent=aspect2dp, relief=None, image=boosterNode, image_scale=1.0, scale=0.38, pos=(-2.0, -10.0, 0.0))
        else:
            altModel = DirectFrame(parent=aspect2dp, relief=None, text=boosterName, text_scale=0.14, text_fg=(1, 1, 1, 1), scale=0.38, pos=(-2.0, -10.0, 0.0))
        try:
            altModel.setBin('gui-popup', 155)
        except:
            pass
        altModel.hide()
        starburst = None
        try:
            starburst = loader.loadModel('phase_3.5/models/props/ttcc_gen_starburst')
            if starburst and not starburst.isEmpty():
                starburst.setScale(0.2)
                starburst.setPos(0, 0, 0)
                starburst.setColorScale(1, 1, 1, 0)
                starburst.reparentTo(aspect2dp)
                starburst.setBin('gui-popup', 150)
            else:
                starburst = None
        except:
            starburst = None
        textColor = (1.0, 0.7, 0.7, 1.0)
        purchaseText = OnscreenText(parent=aspect2dp, scale=0.14, pos=(0, -0.65), font=ToontownGlobals.getSignFont(), fg=textColor, text='You Purchased\n%s' % boosterName, mayChange=0)
        try:
            purchaseText.setBin('gui-popup', 160)
        except:
            pass
        purchaseText.hide()
        purchaseText.setColorScale(1, 1, 1, 0)
        self.redeemVisualNodes = [altModel, purchaseText]
        if starburst:
            self.redeemVisualNodes.append(starburst)
        self.redeemGuiStartPos = self.gui.getPos()
        guiStart = self.redeemGuiStartPos
        guiAway = (guiStart[0], guiStart[1], guiStart[2] + 4.0)
        self._fadeScreen(0.925, 1.0)
        revealParts = [
            Sequence(
                Func(altModel.show),
                LerpPosInterval(altModel, 0.7, (0, -10.0, 0), blendType='easeOut'),
                Wait(0.5),
                Func(self._playDrumroll),
                Wait(1.3),
                Func(self._playFanfare),
                Wait(3.3),
                Func(self._fadeScreen, 0.0, 0.45),
                LerpScaleInterval(altModel, 0.1, 0.44, blendType='easeIn'),
                LerpScaleInterval(altModel, 0.35, 0.01, blendType='easeOut'),
                Func(self._noFade),
                Func(self._destroyRedeemNode, altModel)
            ),
            Sequence(
                Wait(2.6),
                Func(purchaseText.show),
                LerpColorScaleInterval(purchaseText, 1.0, (1, 1, 1, 1), blendType='easeInOut'),
                Wait(1.8),
                LerpColorScaleInterval(purchaseText, 0.6, (1, 1, 1, 0), blendType='easeInOut'),
                Func(self._destroyRedeemNode, purchaseText)
            ),
            Sequence(
                LerpPosInterval(self.gui, 0.8, guiAway, blendType='easeInOut'),
                Wait(4.5),
                Func(self.gui.refresh),
                LerpPosInterval(self.gui, 0.8, guiStart, blendType='easeInOut')
            )
        ]
        if starburst:
            revealParts.append(
                Sequence(
                    Wait(2.6),
                    Parallel(
                        LerpHprInterval(starburst, 3.75, (starburst.getH(), 0, 360)),
                        Sequence(
                            LerpColorScaleInterval(starburst, 0.5, (1, 1, 1, 0.6)),
                            Wait(2.25),
                            LerpColorScaleInterval(starburst, 0.5, (1, 1, 1, 0))
                        )
                    ),
                    Func(self._destroyRedeemNode, starburst)
                )
            )
        self.redeemVisualTrack = Sequence(
            Parallel(*revealParts),
            Func(self._finishRedeemVisual)
        )
        self.redeemVisualTrack.start()

    def playRedeem(self):
        if not self.hasClashModel:
            return
        try:
            if self.redeemTrack:
                self.redeemTrack.finish()
            self._stopIdleSfx()
            redeemDuration = self._safeAnimDuration('redeem')
            activateDuration = self._safeAnimDuration('activate')
            seq = []
            if self.redeemSfx:
                seq.append(Func(self.redeemSfx.play))
            seq.extend([
                Func(self.play, 'redeem'),
                Wait(redeemDuration),
                Wait(1.0),
                Func(self.play, 'activate'),
                Wait(activateDuration),
                Func(self.loop, 'idle'),
                Func(self._startIdleSfx)
            ])
            self.redeemTrack = Sequence(*seq)
            self.redeemTrack.start()
        except:
            try:
                self.loop('idle')
            except:
                pass
            self._startIdleSfx()

    def destroy(self):
        self._exitCollision()
        self._cancelRedeemVisual()
        self._stopIdleSfx()
        self.ignoreAll()
        self.closeGUI(False)
        if self.openTrack:
            self.openTrack.finish()
            self.openTrack = None
        if self.redeemTrack:
            self.redeemTrack.finish()
            self.redeemTrack = None
        if hasattr(self, 'collision') and self.collision:
            self.collision.removeNode()
        self.interior = None
        self.cleanup()
