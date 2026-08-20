from __future__ import absolute_import
import random

from direct.gui.DirectGui import OnscreenImage, OnscreenText
from direct.interval.IntervalGlobal import Sequence, Parallel, Wait, Func, ActorInterval, LerpColorScaleInterval, LerpScaleInterval
from panda3d.core import Vec3, VBase4, Point3, TransparencyAttrib

from toontown.menu.MainMenuScreen import MainMenuScreen
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.toon import ToonDNA, Toon
from toontown.suit import SuitDNA, Suit


class MainMenuScreenHome(MainMenuScreen):
    logoSmallScale = Vec3(0.8, 0.8, 0.4)
    logoBigScale = Vec3(0.88, 0.88, 0.44)

    def createUI(self):
        if hasattr(base, 'discord'):
            try:
                base.discord.applyPreset('main_menu')
            except:
                pass
        base.camLens.setMinFov(52.0 / (4.0 / 3.0))
        base.transitions.fadeIn(1)

        logoImage = 'phase_3/maps/toontown-logo.png'
        self.iconTex = loader.loadTexture(logoImage)
        self.logo = OnscreenImage(image=self.iconTex, scale=self.logoSmallScale)
        self.logo.reparentTo(base.a2dTopCenter)
        self.logo.setTransparency(TransparencyAttrib.MAlpha)
        self.logo.setPos(0, 0, -0.5)

        clickText = getattr(TTLocalizer, 'MainMenuClickToEnter', 'Click to enter')
        self.clickText = OnscreenText(
            text=clickText,
            style=3,
            scale=.1,
            parent=base.aspect2d,
            font=ToontownGlobals.getBuildingNametagFont(),
            fg=(1.0, 1.0, 1.0, 1.0),
            pos=(0.0, 0, -0.02)
        )
        self.clickText.setColorScale(VBase4(1, 1, 1, 0))
        self.clickTextColorSeq = Sequence(
            LerpColorScaleInterval(self.clickText, 1, VBase4(1, 1, 1, 1), blendType='easeInOut'),
            LerpColorScaleInterval(self.clickText, 1, VBase4(.8, .8, .8, .8), blendType='easeInOut')
        )
        self.clickTextColorSeq.loop()
        self.logoSeq = Sequence(
            self.logo.scaleInterval(2, self.logoBigScale, blendType='easeInOut'),
            self.logo.scaleInterval(2, self.logoSmallScale, blendType='easeInOut')
        )
        self.logoSeq.loop()
        self.acceptOnce('mouse1', self.enterGame)
        self.uiItems.append(self.logo)
        self.uiItems.append(self.clickText)

        self.npc1 = self.generateToon()
        self.npc2 = self.generateRPS()
        self.npc3 = self.generateRPS()
        self.npc4 = self.generateToon()
        self.cog1 = self.generateSuit()
        self.cog2 = self.generateSuit()
        self.cog1.hideName()
        self.cog2.hideName()

        self.npc2.setPosHpr(50, 25, 4, 90, 0, 0)
        self.npc4.setPosHpr(50, 25, 4, 90, 0, 0)
        self.cog1.setPosHpr(10, 45, 4, 90, 0, 0)

        giantCog = Sequence()
        if random.random() <= (1.0 / 30.0):
            giantCog = Sequence(Wait(3.0), LerpScaleInterval(self.cog1, 0.3, 1.6, blendType='easeIn'))

        self.afkToons = Sequence(
            Wait(2),
            Parallel(
                self.npc1.posHprInterval(15, Point3(40, 23, 5), Point3(-90, 0, 0)),
                Sequence(Wait(2), self.cog2.posHprInterval(15, Point3(40, 23, 5), Point3(-90, 0, 0)))
            ),
            Wait(7),
            Parallel(
                self.npc2.posHprInterval(7, Point3(2.5, 20, 5), Point3(90, 0, 0)),
                self.npc3.posHprInterval(7, Point3(-2.5, 20, 5), Point3(-90, 0, 0))
            ),
            Parallel(Func(self.npc2.loop, 'neutral'), Func(self.npc3.loop, 'wave')),
            Wait(self.npc3.getDuration('wave')),
            Func(self.npc2.loop, 'walk'),
            Func(self.npc3.loop, 'walk'),
            Parallel(
                self.npc2.hprInterval(0.2, Point3(65, 0, 0)),
                self.npc3.hprInterval(0.2, Point3(-115, 0, 0))
            ),
            Parallel(Func(self.npc2.loop, 'neutral'), Func(self.npc3.loop, 'neutral')),
            Parallel(Func(self.npc2.loop, 'scientistGame'), Func(self.npc3.loop, 'scientistGame')),
            Wait(3),
            Func(self.cog1.setScale, 0.85),
            self.cog1.posHprInterval(2, Point3(0.7, 42, 4), Point3(90, 0, 0)),
            self.cog1.hprInterval(1.5, Point3(180, 0, 0)),
            Parallel(
                self.cog1.posHprInterval(3.5, Point3(0, 32, 4), Point3(180, 0, 0)),
                giantCog
            ),
            Parallel(
                Func(self.cog1.loop, 'neutral'),
                Func(self.npc2.loop, 'walk'),
                Func(self.npc3.loop, 'walk'),
                self.npc2.hprInterval(0.2, Point3(10, 0, 0)),
                self.npc3.hprInterval(0.2, Point3(-20, 0, 0))
            ),
            Parallel(
                Func(self.npc2.stopBlink),
                Func(self.npc3.stopBlink),
                Func(self.npc2.surpriseEyes),
                Func(self.npc3.surpriseEyes),
                Func(self.npc2.showSurpriseMuzzle),
                Func(self.npc3.showSurpriseMuzzle),
                ActorInterval(self.npc2, 'conked', startFrame=9, endFrame=50),
                ActorInterval(self.npc3, 'conked', startFrame=9, endFrame=50)
            ),
            Parallel(
                ActorInterval(self.npc2, 'conked', startFrame=70, endFrame=101),
                ActorInterval(self.npc3, 'conked', startFrame=70, endFrame=101)
            ),
            Parallel(
                Func(self.npc2.loop, 'walk'),
                Func(self.npc3.loop, 'walk'),
                self.npc2.hprInterval(0.3, Point3(-135, 0, 0)),
                self.npc3.hprInterval(0.3, Point3(130, 0, 0))
            ),
            Parallel(
                Func(self.npc2.loop, 'run'),
                Func(self.npc3.loop, 'run'),
                self.npc2.posHprInterval(5, Point3(40, 5, 5), Point3(-135, 0, 0)),
                self.npc3.posHprInterval(5, Point3(-40, 5, 4), Point3(130, 0, 0)),
                Parallel(
                    Func(self.cog1.loop, 'walk'),
                    Sequence(
                        self.cog1.posHprInterval(2, Point3(0, 20, 5), Point3(180, 0, 0)),
                        self.cog1.hprInterval(0.2, Point3(230, 0, 0)),
                        self.cog1.posHprInterval(8, Point3(40, 5, 5), Point3(230, 0, 0))
                    )
                ),
                Parallel(
                    Func(self.npc2.startBlink),
                    Func(self.npc3.startBlink),
                    Func(self.npc2.normalEyes),
                    Func(self.npc3.normalEyes),
                    Func(self.npc2.hideSurpriseMuzzle),
                    Func(self.npc3.hideSurpriseMuzzle)
                )
            ),
            Wait(7),
            self.npc4.posHprInterval(7, Point3(0, 23, 5), Point3(90, 0, 0)),
            Func(self.npc4.loop, 'slip-forward'),
            Wait(self.npc4.getDuration('slip-forward')),
            Func(self.npc4.loop, 'run'),
            self.npc4.posHprInterval(7, Point3(-40, 23, 5), Point3(90, 0, 0)),
            Wait(5)
        )
        self.afkToons.loop()

    def generateToon(self):
        subject = Toon.Toon()
        dna = ToonDNA.ToonDNA()
        dna.newToonRandom(int(random.random() * 571), 'f', 1)
        subject.setDNAString(dna.makeNetString())
        subject.setPosHpr(-50, 25, 4, -90, 0, 0)
        subject.reparentTo(render)
        subject.show()
        subject.loop('run')
        return subject

    def generateRPS(self):
        subject = Toon.Toon()
        dna = ToonDNA.ToonDNA()
        dna.newToonRandom(int(random.random() * 571), 'm', 1)
        dna.updateToonProperties(torso='ls', legs='m', gender='f')
        subject.setDNAString(dna.makeNetString())
        subject.setPosHpr(-50, 25, 4, -90, 0, 0)
        subject.reparentTo(render)
        subject.show()
        subject.loop('run')
        return subject

    def generateSuit(self):
        suitTypes = [
            'bgh', 'pph', 'ins', 'cbr', 'dl',
            'f', 'p', 'ym', 'mm', 'ds',
            'bf', 'b', 'dt', 'ac', 'bs',
            'sc', 'pp', 'tw', 'bc', 'nc',
            'cc', 'tm', 'nd', 'gh', 'ms', 'tf'
        ]
        suit = Suit.Suit()
        dna = SuitDNA.SuitDNA()
        dna.newSuit(random.choice(suitTypes))
        suit.setDNA(dna)
        suit.setPosHpr(-50, 25, 4, -90, 0, 0)
        suit.reparentTo(render)
        suit.show()
        suit.loop('walk')
        return suit

    def destroy(self):
        self.ignoreAll()
        if getattr(self, 'afkToons', None):
            self.afkToons.finish()
            self.afkToons = None
        if getattr(self, 'logoSeq', None):
            self.logoSeq.finish()
            self.logoSeq = None
        if getattr(self, 'clickTextColorSeq', None):
            self.clickTextColorSeq.finish()
            self.clickTextColorSeq = None
        for actorName in ('npc1', 'npc2', 'npc3', 'npc4', 'cog1', 'cog2'):
            actor = getattr(self, actorName, None)
            if actor:
                try:
                    actor.cleanup()
                except:
                    pass
                actor.removeNode()
                try:
                    actor.delete()
                except:
                    pass
                setattr(self, actorName, None)
        MainMenuScreen.destroy(self)

    def enterGame(self):
        if getattr(self, 'clickTextColorSeq', None):
            self.clickTextColorSeq.finish()
        Sequence(
            Parallel(
                self.clickText.posInterval(1, Point3(0, 0, -1), blendType='easeIn'),
                LerpColorScaleInterval(self.clickText, 1, VBase4(0, 0, 0, 0), blendType='easeIn'),
                self.logo.posInterval(1, Point3(0, 0, 1), blendType='easeIn'),
                LerpColorScaleInterval(self.logo, 1, VBase4(1, 1, 1, 0), blendType='easeIn'),
                base.camera.posHprInterval(1, Point3(-1.5, 18, 8), Point3(0, -3, 0), blendType='easeInOut')
            ),
            Func(self.doEnter)
        ).start()

    def doEnter(self):
        base.cr.mainmenu.request('Play')
