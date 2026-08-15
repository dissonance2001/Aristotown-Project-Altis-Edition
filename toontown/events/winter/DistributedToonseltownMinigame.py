import random
import traceback

from direct.distributed import DistributedObject
from direct.gui.DirectGui import OnscreenText
from direct.interval.IntervalGlobal import Sequence, Parallel, ActorInterval, LerpFunctionInterval, Wait, SoundInterval, ParticleInterval, Func, Track
from pandac.PandaModules import CollisionNode, CollisionTube, Vec4, TextNode, Point3

from toontown.battle import BattleParticles, MovieUtil
from toontown.toonbase import ToontownTimer, ToontownGlobals, TTLocalizer

teamScoreText = "Total Team Score: %s"
playerScoreText = "Your Score: %s"


class DistributedToonseltownMinigame(DistributedObject.DistributedObject):
    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.cr = cr
        self.totalScore = 0
        self.playerScore = 0
        self.teamScoreText = None
        self.playerScoreText = None
        self.isHoldingPresent = False
        self.treeCollision = None
        self.timer = None
        self.presents = {}
        self.presentsSeq = {}
        self.treePresents = []
        self.presentGUI = None
        self.presentGUISeq = None
        self.presentGUIPos = None
        self.presentThiefMusic = None
        self.scoreFlashSeqs = []
        self.cleanedUp = False
        self.model2Group = {
            1: '**/polySurface9',
            2: '**/polySurface35',
            3: '**/polySurface3',
            4: '**/polySurface5',
        }

    def disable(self):
        if getattr(base, 'toonselTownMinigameIsActive', False):
            self.startCleanup(True)
        DistributedObject.DistributedObject.disable(self)

    def delete(self):
        self._finishTracks()
        DistributedObject.DistributedObject.delete(self)

    def setupTree(self):
        self.destroyTree()
        model = loader.loadModel('phase_13/models/events/toonseltown/present_1')
        self.treeCollision = model.find(self.model2Group[1])
        if self.treeCollision.isEmpty():
            self.treeCollision = model
        else:
            self.treeCollision.wrtReparentTo(render)
            model.removeNode()
        self.treeCollision.setPos(-51.129, -19.366, 0.025)
        collNode = CollisionNode('TreeCol')
        collNode.setCollideMask(ToontownGlobals.WallBitmask)
        collTube = CollisionTube(0, 0, 0, 0.0, 0.0, 35, 35)
        collTube.setTangible(0)
        collNode.addSolid(collTube)
        self.treeCollision.attachNewNode(collNode)

    def setupGUI(self):
        self.destroyGui()
        self.timer = ToontownTimer.ToontownTimer()
        self.timer.posInTopRightCorner()
        self.timer.hide()
        self.teamScoreText = OnscreenText(parent=base.a2dTopLeft, text=teamScoreText % self.totalScore,
                                          font=ToontownGlobals.getMinnieFont(), fg=(1, 1, 1, 1),
                                          align=TextNode.ALeft, scale=0.1, style=3,
                                          pos=(0, -0.3), wordwrap=20)
        self.playerScoreText = OnscreenText(parent=base.a2dTopLeft, text=playerScoreText % self.playerScore,
                                            font=ToontownGlobals.getMinnieFont(), fg=(1, 1, 1, 1),
                                            align=TextNode.ALeft, scale=0.1, style=3,
                                            pos=(0, -0.4), wordwrap=20)
        self.teamScoreText.hide()
        self.playerScoreText.hide()
        self.generatePresentGUI()

    def generatePresentGUI(self):
        if self.presentGUI:
            self.presentGUI.removeNode()
        model = loader.loadModel('phase_13/models/events/toonseltown/present_1')
        self.presentGUI = model.find(self.model2Group[1])
        if self.presentGUI.isEmpty():
            self.presentGUI = model
        else:
            self.presentGUI.wrtReparentTo(base.a2dBottomLeft)
            model.removeNode()
        if self.presentGUI.getParent() != base.a2dBottomLeft:
            self.presentGUI.reparentTo(base.a2dBottomLeft)
        self.presentGUI.setScale(0.18)
        self.presentGUI.setPos(0.15, 0, 0.3)
        self.presentGUIPos = (0.15, 0, 0.3)
        self.presentGUI.setDepthWrite(1)
        self.presentGUI.setDepthTest(1)
        self.presentGUI.setTwoSided(True)
        self.presentGUI.hide()

    def handleEventStart(self, gameTime):
        self.cleanedUp = False
        base.toonselTownMinigameIsActive = True
        base.localAvatar.setTeleportAvailable(0)
        if self.timer:
            self.timer.setPos(-0.6, 0, -0.158)
            self.timer.show()
            self.timer.setTime(gameTime)
            self.timer.countdown(gameTime, self.stopTimer)
        if self.teamScoreText:
            self.teamScoreText.show()
        if self.playerScoreText:
            self.playerScoreText.show()
        self.playMusic()
        self.accept('enterTreeCol', self._handleTreeCollision)
        self.accept('localPieSplat', self.__localPieSplat)

    def __localPieSplat(self, pieCode, entry):
        if pieCode != ToontownGlobals.PieCodeWinterMinigame:
            return
        suitCol = entry.getIntoNodePath()
        suitIdStr = suitCol.getNetTag('winterSuitId')
        if not suitIdStr:
            return
        try:
            suitDoId = int(suitIdStr)
        except:
            return
        suit = self.getSuit(suitDoId)
        if not suit or suit.exploding or getattr(suit, 'snowballHitPending', False):
            return
        suit.snowballHitPending = True
        self.addToPlayerScore(ToontownGlobals.TsMinigameCogPoints)
        self.sendUpdate('playerHitCogWithSnowball', [suitDoId])

    def _handleTreeCollision(self, collision):
        if self.isHoldingPresent:
            self.sendUpdate('playerTouchedTree', [])

    def _handleTouchPresent(self, col):
        if self.isHoldingPresent:
            return
        name = col.getIntoNode().getName()
        try:
            presentId = int(name.replace('PresentCol', ''))
        except:
            return
        self.sendUpdate('playerTouchedFieldPresent', [presentId])

    def generateFieldPresent(self, presentId, x, y, z):
        if presentId in self.presents:
            self.destroyPresent(presentId)
        r = random.randint(1, 4)
        model = loader.loadModel('phase_13/models/events/toonseltown/present_' + str(r))
        present = model.find(self.model2Group[r])
        if present.isEmpty():
            present = model
        else:
            present.wrtReparentTo(self.cr.playGame.hood.loader.geom)
            model.removeNode()
        if present.getParent() != self.cr.playGame.hood.loader.geom:
            present.reparentTo(self.cr.playGame.hood.loader.geom)
        present.setScale(1.5)
        present.setPos(x, y, z)
        collNode = CollisionNode('PresentCol' + str(presentId))
        collNode.setCollideMask(ToontownGlobals.CameraBitmask | ToontownGlobals.WallBitmask)
        collTube = CollisionTube(0, 0, 0, 0.0, 0.0, 1.5, 1.5)
        collTube.setTangible(1)
        collNode.addSolid(collTube)
        present.attachNewNode(collNode)
        self.accept('enterPresentCol' + str(presentId), self._handleTouchPresent)
        self.presents[presentId] = present
        seq = Sequence(Parallel(
            Sequence(
                present.posInterval(1, (x, y, z + 0.5), blendType='easeInOut'),
                present.posInterval(1, (x, y, z), blendType='easeInOut'),
                present.posInterval(1, (x, y, z + 0.5), blendType='easeInOut'),
                present.posInterval(1, (x, y, z), blendType='easeInOut')),
            present.hprInterval(4, (360, 0, 0))))
        self.presentsSeq[presentId] = seq
        seq.loop()

    def destroyPresent(self, presentId):
        self.ignore('enterPresentCol' + str(presentId))
        seq = self.presentsSeq.pop(presentId, None)
        if seq:
            try:
                seq.finish()
            except:
                pass
        present = self.presents.pop(presentId, None)
        if present:
            present.removeNode()

    def generateTreePresent(self, x, y, z):
        r = random.randint(1, 4)
        model = loader.loadModel('phase_13/models/events/toonseltown/present_' + str(r))
        present = model.find(self.model2Group[r])
        if present.isEmpty():
            present = model
        else:
            present.wrtReparentTo(render)
            model.removeNode()
        if present.getParent() != render:
            present.reparentTo(render)
        present.setPos(x, y, z)
        present.setScale(1.5)
        self.treePresents.append(present)

    def showHoldingPresent(self):
        try:
            pickupSfx = base.loader.loadSfx('phase_3.5/audio/sfx/MG_maze_pickup.ogg')
            base.playSfx(pickupSfx, volume=1)
        except:
            pass
        if not self.presentGUI:
            self.generatePresentGUI()
        if self.presentGUISeq:
            try:
                self.presentGUISeq.finish()
            except:
                pass
        self.presentGUI.show()
        self.isHoldingPresent = True
        x, y, z = self.presentGUIPos
        self.presentGUISeq = Sequence(Parallel(
            Sequence(
                self.presentGUI.posInterval(2, (x, y, z + 0.05), blendType='easeInOut'),
                self.presentGUI.posInterval(2, (x, y, z), blendType='easeInOut'),
                self.presentGUI.posInterval(2, (x, y, z + 0.05), blendType='easeInOut'),
                self.presentGUI.posInterval(2, (x, y, z), blendType='easeInOut')),
            self.presentGUI.hprInterval(8, (360, 0, 0))))
        self.presentGUISeq.loop()

    def hideHoldingPresent(self):
        self.addToPlayerScore(ToontownGlobals.TsMinigamePresentPoints)
        try:
            dropSfx = base.loader.loadSfx('phase_3.5/audio/sfx/AV_collision.ogg')
            base.playSfx(dropSfx, volume=1)
        except:
            pass
        if self.presentGUI:
            self.presentGUI.hide()
        if self.presentGUISeq:
            try:
                self.presentGUISeq.finish()
            except:
                pass
            self.presentGUISeq = None
        self.isHoldingPresent = False

    def updateTotalScore(self, score):
        oldScore = self.totalScore
        self.totalScore = score
        if not self.teamScoreText:
            return
        if oldScore < score:
            color = Vec4(0, 1, 0, 1)
        elif oldScore > score:
            color = Vec4(1, 0, 0, 1)
        else:
            color = Vec4(1, 1, 1, 1)
        self.teamScoreText['text'] = teamScoreText % self.totalScore
        flash = Sequence(
            LerpFunctionInterval(self.setTotalScoreTextColor, 0.5, Vec4(1, 1, 1, 1), color),
            LerpFunctionInterval(self.setTotalScoreTextColor, 0.5, color, Vec4(1, 1, 1, 1)))
        self.scoreFlashSeqs.append(flash)
        flash.start()

    def addToPlayerScore(self, amount):
        self.playerScore += amount
        if not self.playerScoreText:
            return
        self.playerScoreText['text'] = playerScoreText % self.playerScore
        color = Vec4(0, 1, 0, 1)
        flash = Sequence(
            LerpFunctionInterval(self.setPlayerScoreTextColor, 0.5, Vec4(1, 1, 1, 1), color),
            LerpFunctionInterval(self.setPlayerScoreTextColor, 0.5, color, Vec4(1, 1, 1, 1)))
        self.scoreFlashSeqs.append(flash)
        flash.start()

    def setTotalScoreTextColor(self, color):
        if self.teamScoreText:
            self.teamScoreText['fg'] = color

    def setPlayerScoreTextColor(self, color):
        if self.playerScoreText:
            self.playerScoreText['fg'] = color

    def activateSuit(self, suitId):
        suit = self.getSuit(suitId)
        if suit:
            suit.request('Neutral')

    def getSuit(self, suitId):
        return self.cr.doId2do.get(suitId)

    def showWarningText(self):
        try:
            try:
                base.localAvatar.showHpString(TTLocalizer.TsMinigameCogsSpawn, duration=2, color=(1, 0, 0, 1))
            except TypeError:
                base.localAvatar.showHpString(TTLocalizer.TsMinigameCogsSpawn, duration=2, scale=0.4)
                hpText = getattr(base.localAvatar, 'hpText', None)
                if hpText:
                    hpText.setColorScale(1, 0, 0, 1)
        except:
            traceback.print_exc()

    def playMusic(self):
        try:
            loaderObj = base.cr.playGame.hood.loader
            if hasattr(loaderObj, 'music') and loaderObj.music:
                loaderObj.music.stop()
        except:
            pass
        if not self.presentThiefMusic:
            self.presentThiefMusic = base.loader.loadMusic('phase_13/audio/bgm/winter/christmas_present_thief.ogg')
        base.playMusic(self.presentThiefMusic, looping=1, volume=0.7)

    def stopMusic(self, leavingTS=False):
        if self.presentThiefMusic:
            try:
                self.presentThiefMusic.stop()
            except:
                pass
        if leavingTS:
            return
        try:
            loaderObj = base.cr.playGame.hood.loader
            if hasattr(loaderObj, 'music') and loaderObj.music:
                base.playMusic(loaderObj.music, looping=1, volume=0.7)
        except:
            pass

    def startCleanup(self, leavingTS=False):
        if self.cleanedUp:
            return
        self.cleanedUp = True
        base.toonselTownMinigameIsActive = False
        try:
            base.localAvatar.setTeleportAvailable(1)
        except:
            pass
        self.ignore('localPieSplat')
        self.ignore('enterTreeCol')
        self.destroyTree()
        self.stopMusic(leavingTS)
        self.destroyAllPresents()
        if self.timer:
            try:
                self.timer.stop()
            except:
                pass
            try:
                self.timer.destroy()
            except:
                pass
            self.timer = None
        self.destroyGui()

    def destroyAllPresents(self):
        for presentId in list(self.presents.keys()):
            self.destroyPresent(presentId)
        for present in self.treePresents:
            try:
                present.removeNode()
            except:
                pass
        self.treePresents = []

    def destroyTree(self):
        if self.treeCollision:
            try:
                self.treeCollision.removeNode()
            except:
                pass
            self.treeCollision = None

    def _finishTracks(self):
        for flash in self.scoreFlashSeqs:
            try:
                flash.finish()
            except:
                pass
        self.scoreFlashSeqs = []
        if self.presentGUISeq:
            try:
                self.presentGUISeq.finish()
            except:
                pass
            self.presentGUISeq = None

    def destroyGui(self):
        self._finishTracks()
        if self.teamScoreText:
            self.teamScoreText.removeNode()
            self.teamScoreText = None
        if self.playerScoreText:
            self.playerScoreText.removeNode()
            self.playerScoreText = None
        if self.presentGUI:
            self.presentGUI.removeNode()
            self.presentGUI = None

    def stopTimer(self):
        if self.timer:
            self.timer.stop()
            self.timer.hide()
