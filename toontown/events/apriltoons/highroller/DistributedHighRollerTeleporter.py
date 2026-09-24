import time

from direct.gui.OnscreenText import OnscreenText
from panda3d.core import *
from toontown.chat.constants.ChatGlobals import CFSpeech, CFTimeout
from otp.nametag import NametagGlobals
from otp.nametag.Nametag import Nametag
from direct.distributed.DistributedObject import DistributedObject
from direct.interval.IntervalGlobal import *

from toontown.chat.enums.ChatChannel import ChatChannel
from toontown.chat.enums.ChatContentType import ChatContentType
from toontown.chat.enums.ChatNpcPreset import ChatNpcPreset
from toontown.gui import TTDialog
from toontown.hood import ZoneUtil
from toontown.quest3.base import QuestGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.toonbase import ToontownGlobals
from toontown.cutscene import CutsceneLocalizer
from toontown.avatar import Avatar
from toontown.toon.OneTimeCutsceneGlobals import OneTimeCutscenes as OTC
from toontown.clashbattle.battle import BattleParticles
import random
from otp.nametag.Nametag import *

DefaultPosHpr = (-65.6, -17.579, -1.975, 149, 0, 0)
ZoneToPosHpr = {
    ToontownGlobals.ToontownCentral:   (-65.6, -17.579, -1.975, 149, 0, 0),
    ToontownGlobals.DonaldsDock:       (59.5, 108.45, 3.28, 116, 0, 0),
    ToontownGlobals.YeOlde:      (-15.05, -114.3, -7.0, 22, 0, 0),
    ToontownGlobals.DaisyGardens:      (-45.61, 275.14, 14.028, 22.8, 0, 0),
    ToontownGlobals.MinniesMelodyland: (-85.862, -84.032, 6.525, -39.55, 0, 0),
    ToontownGlobals.TheBrrrgh:         (17.98, -45.79, 6.192, 62.925, 0, 0),
    ToontownGlobals.OutdoorZone:       (-56.832, -55.39, 4.475, -157.817, -4, 0),
    ToontownGlobals.DonaldsDreamland:  (32.59, -26.976, -15.32, 50, 0, -2),
    ToontownGlobals.MajorPlayerLobby:  (-22.798, 2.952, 0.025, 0, 0, 0),
}
DuckPathBase = 'phase_13/models/events/apriltoons/highroller/char/cc_m_chr_ara_hr_prp_lowRoller'
DuckAnimDict = {
    'neutral': f'{DuckPathBase}-idle',
    'talk-short': f'{DuckPathBase}-talkshort',
    'talk-long': f'{DuckPathBase}-talklong',
}
DuckPosHpr = [
    (-2.5, 0, 0, -20, 0, 0),
    (2.5, 0, 0, 20, 0, 0),
]


@DirectNotifyCategory()
class HighRollerTeleporterDuck(Avatar.Avatar):
    def __init__(self, other=None):
        try:
            self.HRDuck_initialized
            return
        except:
            self.HRDuck_initialized = 1

        Avatar.Avatar.__init__(self)
        self.ignore('nametagAmbientLightChanged')
        self.talkSeq = None
        self.dialogueSfx = {}
        self.initDuck()

    def delete(self):
        if self.talkSeq:
            self.talkSeq.finish()
            self.talkSeq = None
        for dialogueSfx in self.dialogueSfx.values():
            dialogueSfx.stop()
        self.dialogueSfx = {}

        super().delete()

    def getNametagJoints(self):
        return []

    def initDuck(self):
        self.generateDuck()
        self.initializeNametag3d()
        self.setNameVisible(False)
        self.hideNametag2d()
        self.hideNametag3d()
        self.nametag.getNametag2d().setContents(Nametag.CSpeech)
        self.nametag.getNametag3d().setContents(Nametag.CSpeech)
        self.setName("Low Baller")
        self.setPickable(0)
        self.addActive()
        self.setHeight(3.4)
        self.nametag3d.setScale(1.25)
        self.dialogueSfx = {
            'short': loader.loadSfx('phase_13/audio/sfx/april_toons/highroller/cc_s_dlg_ara_hr_prp_lowRoller_short.ogg'),
            'long': loader.loadSfx('phase_13/audio/sfx/april_toons/highroller/cc_s_dlg_ara_hr_prp_lowRoller_long.ogg'),
        }

    def generateDuck(self):
        self.loadModel(DuckPathBase)
        self.loadAnims(DuckAnimDict)

    def say(self, message):
        self.setChatAbsolute(message, CFSpeech | CFTimeout)

    def setChatAbsolute(self, chatString, chatFlags, dialogue=None, interrupt=1, wantBalloonAnim=True, wantSound=True, logMessage=None):
        super().setChatAbsolute(chatString, chatFlags, dialogue=dialogue, interrupt=interrupt, wantBalloonAnim=wantBalloonAnim, wantSound=wantSound, logMessage=logMessage)

        if getattr(base, "cr", None):
            for message in chatString.split("\x07"):
                base.cr.chatManager.receiveChatMessage(ChatChannel.NPC, ChatNpcPreset.LowBaller, ChatContentType.Text, message, 0, self.getName())

        dialogueType = random.choice(['short', 'long'])
        if self.dialogueSfx:
            base.playSfx(self.dialogueSfx[dialogueType], volume=0.7, node=self)

        if self.talkSeq:
            self.talkSeq.finish()
        self.talkSeq = Sequence(ActorInterval(self, f'talk-{dialogueType}'), Func(self.loop, 'neutral'))
        self.talkSeq.start()


@DirectNotifyCategory()
class DistributedHighRollerTeleporter(DistributedObject):
    """
    A set of cute little ducks in each playground that will teleport you back and forth
    between Major Players (and High Roller's) lobby during april toons
    """

    def __init__(self, cr):
        super().__init__(cr)
        self.geom = None
        self.ducks = []
        self.dialog = None
        self.introSeqs = []
        self.introButtons = []
        self.teleportSeqs = []
        self.__ignoreAdvertisingTimestamp = 0
        self.__ignoreInteractTimestamp = 0

        # Music stuff
        self.musicPath = 'highroller_lowballer'
        self.playgroundMusicPath = None
        self.ballerMusic = None
        self.playgroundMusic = None

    def announceGenerate(self):
        super().announceGenerate()

        self.ballerMusic = base.musicMgr.loadMusic(self.musicPath)
        if self.inMajorPlayerLobby:
            self.playgroundMusicPath = 'majorplayer_lobby'
        else:
            self.playgroundMusicPath = base.cr.playGame.hood.loader.music
        self.playgroundMusic = base.musicMgr.loadMusic(self.playgroundMusicPath)

        self.setupModel()

    @property
    def posHpr(self):
        return ZoneToPosHpr.get(self.zoneId, DefaultPosHpr)

    @property
    def doneFirstInteraction(self):
        # We have a special interaction with the player if they haven't talked to the Ducks before
        return base.localAvatar.hasSeenCutscene(OTC.HighRoller_TeleportTutorial)

    @property
    def inTutorial(self):
        return QuestGlobals.isInTutorial(base.localAvatar)

    def setupModel(self):
        self.geom = NodePath('HighRollerTeleporter-Container')
        self.ducks = [HighRollerTeleporterDuck(), HighRollerTeleporterDuck()]
        for i, duck in enumerate(self.ducks):
            duck.getGeomNode().setScale(3.0)
            duck.setPosHpr(*DuckPosHpr[i])
            duck.reparentTo(self.geom)
            duck.loop('neutral')

        # Apply their position
        self.geom.setPosHpr(*self.posHpr)

        self.geom.reparentTo(render)
        self.initCollisions()

    def disable(self):
        self.ignoreAll()
        self.removeAllTasks()
        self.cleanupCollisions()
        base.musicMgr.stopMusic(self.ballerMusic)
        self.ballerMusic = None
        self.playgroundMusic = None
        for seq in self.introSeqs:
            seq.finish()
        self.introSeqs = []
        for seq in self.teleportSeqs:
            seq.finish()
        self.teleportSeqs = []
        for duck in self.ducks:
            duck.delete()
        self.ducks = []
        if self.geom:
            self.geom.removeNode()
            self.geom = None
        if self.dialog:
            self.dialog.cleanup()
            self.dialog = None
        for button in self.introButtons:
            button.destroy()
        self.introButtons = []

    """
    Collision management
    """

    def initCollisions(self):
        # General blocker, not for interaction
        self.bSphere = CollisionTube(0.0, 1.0, 0.0, 0.0, 1.0, 5.0, 3.25)
        self.bSphere.setTangible(1)
        self.bSphereNode = CollisionNode('duckBSphereNode')
        self.bSphereNode.addSolid(self.bSphere)
        self.bSphereNodePath = self.geom.attachNewNode(self.bSphereNode)
        self.bSphereNodePath.hide()
        self.bSphereNodePath.setPos(0, -1.4, 0)
        self.bSphereNodePath.setScale(1.6, 1.0, 1.0)
        self.bSphereNode.setCollideMask(ToontownGlobals.WallBitmask | ToontownGlobals.CameraBitmask)
        # Interact area
        self.cSphere = CollisionTube(0.0, 1.0, 0.0, 0.0, 1.0, 5.0, 3.25)
        self.cSphere.setTangible(0)
        self.cSphereNode = CollisionNode('duckCSphereNode')
        self.cSphereNode.addSolid(self.cSphere)
        self.cSphereNodePath = self.geom.attachNewNode(self.cSphereNode)
        self.cSphereNodePath.hide()
        self.cSphereNodePath.setPos(0, 1.8, 0)
        self.cSphereNodePath.setScale(1.3, 0.4, 0.5)
        self.cSphereNode.setCollideMask(ToontownGlobals.WallBitmask)
        self.accept('enter' + self.cSphereNode.getName(), self.onCollision)

        # Collision but music version
        self.mSphere = CollisionTube(0.0, 1.0, 0.0, 0.0, 1.0, 5.0, 6.5)
        self.mSphere.setTangible(0)
        self.mSphereNode = CollisionNode(f'mSphereNode-HighRollerTeleporter-ZONE{self.zoneId}')
        self.mSphereNode.addSolid(self.mSphere)
        self.mSphereNodePath = self.geom.attachNewNode(self.mSphereNode)
        self.mSphereNodePath.setPos(0, 1.8, 0)
        self.mSphereNodePath.setScale(1.1, 1.0, 1.0)
        self.mSphereNodePath.hide()
        self.mSphereNode.setCollideMask(ToontownGlobals.WallBitmask)
        self.accept('enter' + self.mSphereNode.getName(), self.startMusic)
        self.accept('exit' + self.mSphereNode.getName(), self.stopMusic)

    def startMusic(self, collEntry=None):
        if collEntry.getIntoNode().getName() != self.mSphereNode.getName():
            return

        place = base.cr.playGame.getPlace()
        if place and place.getState() in ('Walk', 'Stopped'):
            base.musicMgr.crossfadeIntoMusic(self.ballerMusic, duration=0.5, volume=1.0, musicCode=self.musicPath)

    def stopMusic(self, collEntry=None):
        if collEntry.getIntoNode().getName() != self.mSphereNode.getName():
            return

        place = base.cr.playGame.getPlace()
        if place and place.getState() in ('Walk', 'Stopped'):
            base.musicMgr.crossfadeIntoMusic(self.playgroundMusic, duration=0.5, volume=0.8,
                                             musicCode=base.cr.playGame.hood.loader.music)

    def cleanupCollisions(self):
        del self.bSphere
        del self.bSphereNode
        self.bSphereNodePath.removeNode()
        del self.bSphereNodePath

        del self.cSphere
        del self.cSphereNode
        self.cSphereNodePath.removeNode()
        del self.cSphereNodePath

        del self.mSphere
        del self.mSphereNode
        self.mSphereNodePath.removeNode()
        del self.mSphereNodePath

    def onCollision(self, _=None):
        # May have a timeout on interactions in some cases
        if not self.allowInteract:
            return

        if settings['interactkey']:
            self.accept('exit' + self.cSphereNode.getName(), self.handleCollisionSphereExit)
            self.accept('teleportBegin', self.handleCollisionSphereExit)
            self.accept(base.INTERACT, self.activate)
            if hasattr(self, "name"):
                text = ("Press " + str(base.INTERACT).upper() + " to interact with %s" %self.getName())
            else:
                text = "Press " + str(base.INTERACT).upper() + " to interact"

            self.enterText = OnscreenText(
                text = text,
                style = 3,
                scale = .09,
                parent = base.a2dBottomCenter,
                fg = (1, 0.9, 0.1, 1),
                pos = (0.0, 0.5)
            )
            self.enterText.setColorScale(1, 1, 1, 0)
            self.colorSeq = Sequence(
                LerpColorScaleInterval(self.enterText, .8, VBase4(1, 1, 1, 1)),
                LerpColorScaleInterval(self.enterText, .8, VBase4(.5, .6, 1, .9))).loop()
        else:
            self.activate()

    def activate(self):
        # May have a timeout on interactions in some cases
        if not self.allowInteract:
            return

        if settings['interactkey']:
            self.handleCollisionSphereExit()

        if self.inTutorial:
            self.handleTutorialInteraction()
        else:
            if not self.doneFirstInteraction:
                self.handleFirstInteraction()
            else:
                self.promptTeleport()

    def handleCollisionSphereExit(self, collEntry=None):
        self.ignore('exit' + self.cSphereNode.getName())
        self.ignore('teleportBegin')
        self.ignore(base.INTERACT)
        if hasattr(self, "colorSeq"):
            if self.colorSeq:
                self.colorSeq.finish()
                self.colorSeq = None
        if hasattr(self, "enterText"):
            self.enterText.removeNode()
            del self.enterText

    """
    Interaction handling
    """

    transitionLength = 1.0
    guiUseTime = 120

    @property
    def leftDuck(self):
        return self.ducks[0]

    @property
    def rightDuck(self):
        return self.ducks[1]

    @property
    def allowAdvertisement(self):
        return time.time() >= self.__ignoreAdvertisingTimestamp

    @property
    def allowInteract(self):
        return time.time() >= self.__ignoreInteractTimestamp

    @property
    def inMajorPlayerLobby(self):
        return self.zoneId == ToontownGlobals.MajorPlayerLobby

    @property
    def promptTeleportDialoguePool(self):
        if self.inMajorPlayerLobby:
            return CutsceneLocalizer.HighRollerTeleporterLobbyPromptTeleport
        return CutsceneLocalizer.HighRollerTeleporterPromptTeleport

    @property
    def acceptTeleportDialoguePool(self):
        if self.inMajorPlayerLobby:
            return CutsceneLocalizer.HighRollerTeleporterLobbyAcceptTeleport
        return CutsceneLocalizer.HighRollerTeleporterAcceptTeleport

    @property
    def denyTeleportDialoguePool(self):
        if self.inMajorPlayerLobby:
            return CutsceneLocalizer.HighRollerTeleporterLobbyDenyTeleport
        return CutsceneLocalizer.HighRollerTeleporterDenyTeleport

    @property
    def promptTeleportGUIDialogue(self):
        if self.inMajorPlayerLobby:
            return CutsceneLocalizer.HighRollerTeleporterLobbyGUIWantTeleport.format(ToontownGlobals.hoodNameMap[self.localAvPlayground][2])
        return CutsceneLocalizer.HighRollerTeleporterGUIWantTeleport

    @property
    def localAvPlayground(self):
        # Run through every "end of taskline" quest to check if they've completed it
        for playground, questReq in QuestGlobals.QuestHistoryForPlaygroundCompletion.items():
            if not base.localAvatar.hasCompletedQuestHistory(questReq):
                # If they haven't completed the end of taskline quest for a certain playground,
                # then that's the playground they're currently working on and should be teleported to
                return playground

        # They've done everything, just teleport them to DDL
        return ToontownGlobals.DonaldsDreamland

    @property
    def teleportLocation(self):
        # Teleport to the local av's corresponding playground if we're already in the lobby
        # Else, they need teleported to the lobby!
        if self.inMajorPlayerLobby:
            return self.localAvPlayground
        return ToontownGlobals.MajorPlayerLobby

    def setAdvertisementEnabled(self, enabled):
        self.__ignoreAdvertisingTimestamp = 0 if enabled else 99999999999999999

    def clearDuckChat(self):
        for duck in self.ducks:
            duck.clearChat()

    def randomDuckSay(self, dialogue, clearChat=True):
        if clearChat:
            self.clearDuckChat()

        duck = random.choice(self.ducks)
        duck.setChatAbsolute(dialogue, CFSpeech | CFTimeout)

    def duckSay(self, duck, dialogue):
        self.clearDuckChat()
        duck.say(dialogue)

    def advertise(self, dialogueIndex):
        # We may want to place a timeout on advertisements for some actions.
        # Don't do anything if we're in the middle of one
        if not self.allowAdvertisement:
            return

        self.randomDuckSay(CutsceneLocalizer.HighRollerTeleporterAdvertising[dialogueIndex])

    def handleTutorialInteraction(self):
        self.__ignoreAdvertisingTimestamp = time.time() + 10.0
        self.__ignoreInteractTimestamp = time.time() + 5.0
        self.randomDuckSay(random.choice(CutsceneLocalizer.HighRollerTeleporterPreTutorial))

    def handleFirstInteraction(self):
        if self.inMajorPlayerLobby:
            # This is a very specific interaction, where the player has never interacted with
            # the ducks before, but has found themselves in major player's lobby.
            # In this case, we should just give them a basic brush-off.
            self.randomDuckSay(CutsceneLocalizer.HighRollerTeleporterLobbyNotInteracted)
            self.__ignoreInteractTimestamp = time.time() + 5.0
            return

        self.setAdvertisementEnabled(False)

        dlg = CutsceneLocalizer.HighRollerTeleporterFirstInteract
        # Everything else is good to go, let's lock them down and start a funny sequence.
        base.cr.playGame.getPlace().setState('Stopped')
        base.localAvatar.lockControlsForEntry()

        from toontown.menu.MainMenuGui import MainMenuButton
        introButton = MainMenuButton(
            parent=aspect2d,
            relief=None,
            text='Oh Yeah',
            pos=(0.25, 0, -0.7),
            scale=1.6,
            command=self.handleFirstInteractSecondHalf,
        )
        introButton.hide()
        introButton2 = MainMenuButton(
            parent=aspect2d,
            relief=None,
            text='Definitely',
            pos=(-0.25, 0, -0.7),
            scale=1.6,
            command=self.handleFirstInteractSecondHalf,
        )
        introButton2.hide()
        self.introButtons = [introButton, introButton2]

        introSeq = Sequence(
            camera.posQuatInterval(
                self.transitionLength,
                Vec3(-5, 9, 4.5), Vec3(-150, -2, 0),
                other=self.geom, blendType='easeOut',
                name=self.uniqueName('lerpCamera')
            ),
            Wait(0.5),
            Func(self.duckSay, self.leftDuck, dlg[0]),
            Wait(3.5),
            Func(self.duckSay, self.rightDuck, dlg[1]),
            Wait(3.5),
            Func(self.duckSay, self.leftDuck, dlg[2]),
            Wait(2.0),
            Func(self.duckSay, self.leftDuck, dlg[3]),
            Wait(5.0),
            Func(self.duckSay, self.rightDuck, dlg[4]),
            Wait(4.5),
            Func(self.duckSay, self.leftDuck, dlg[5]),
            Wait(3.5),
            Func(self.duckSay, self.rightDuck, dlg[6]),
            Wait(3.5),
            Func(self.duckSay, self.leftDuck, dlg[7]),
            Wait(4.2),
            Func(self.duckSay, self.rightDuck, dlg[8]),
            Wait(1.5),
            Func(introButton.show),
            Func(introButton2.show),
        )
        introSeq.start()
        self.introSeqs.append(introSeq)

    def handleFirstInteractSecondHalf(self):
        dlg = CutsceneLocalizer.HighRollerTeleporterFirstInteract

        for button in self.introButtons:
            button.hide()

        def cleanup():
            # Tell the server we've now seen this cutscene
            base.localAvatar.requestAddSeenCutscene(OTC.HighRoller_TeleportTutorial)

            base.cr.playGame.getPlace().setState('Walk')
            base.localAvatar.unlockControlsForEntry()
            for iButton in self.introButtons:
                iButton.destroy()
            self.introButtons = []

            self.setAdvertisementEnabled(True)

        # Toon nods
        base.localAvatar.doEmote(17, 1.0, 0, None, [])

        introSeq = Sequence(
            Wait(0.5),
            Func(self.duckSay, self.leftDuck, dlg[9]),
            Wait(2.5),
            Func(self.duckSay, self.rightDuck, dlg[10]),
            Wait(3.5),
            Func(self.duckSay, self.leftDuck, dlg[11]),
            Wait(4.1),
            Func(cleanup),
        )
        introSeq.start()
        self.introSeqs.append(introSeq)

    def promptTeleport(self):
        self.randomDuckSay(random.choice(self.promptTeleportDialoguePool))
        self.openGui()
        self.setAdvertisementEnabled(False)

    def handleTeleportAccepted(self):
        # Use the left duck here because the toon may be blocking the right duck. Makes it cleaner.
        self.duckSay(self.leftDuck, random.choice(self.acceptTeleportDialoguePool))
        self.sendUpdate('requestTeleport', [])

    def handleTeleportDenied(self):
        self.randomDuckSay(random.choice(self.denyTeleportDialoguePool))
        self.__ignoreAdvertisingTimestamp = time.time() + 10.0

    def handleToonTeleport(self, avId):
        # Received from server, says a toon has decided to teleport.
        toon = base.cr.doId2do.get(avId)
        if not toon:
            return

        particleNode = render.attachNewNode(f'DistHighRollerTeleporter-particleNode-{toon.doId}')
        particleNode.setPos(toon.getPos(render))
        BattleParticles.loadParticles()
        particleEffect = BattleParticles.loadParticleFile('highRollerTeleporter.ptf')
        tpSfx = loader.loadSfx('phase_12/audio/sfx/SA_scabbard.ogg')

        def handleTeleport(toon=toon):
            if not toon.isLocal():
                return

            toon.getGeomNode().setColorScale(1, 1, 1, 1)
            toon.nametag3d.setColorScale(1, 1, 1, 1)
            toon.clearTransparency()
            base.localAvatar.unlockControlsForEntry()
            base.localAvatar.magicTeleportInitiate(ZoneUtil.getHoodId(self.teleportLocation), self.teleportLocation, quick=1)

        tpSeq = Sequence(
            Parallel(
                SoundInterval(tpSfx, startTime=1.5, node=particleNode),
                ParticleInterval(particleEffect, particleNode, duration=4.0, cleanup=True,
                                 softStopT=-1.5, renderParent=render),
                Sequence(
                    Wait(0.5),
                    Func(toon.setTransparency, 1),
                    Parallel(
                        LerpColorScaleInterval(toon.getGeomNode(), 1.0, (1, 1, 1, 0), blendType='easeIn'),
                        LerpColorScaleInterval(toon.nametag3d, 1.0, (1, 1, 1, 0), blendType='easeIn'),
                    ),
                    Wait(2.5),
                    Func(handleTeleport),
                ),
            ),
            Func(particleNode.removeNode),
        )
        self.teleportSeqs.append(tpSeq)
        tpSeq.start()

    def openGui(self):
        base.cr.playGame.getPlace().setState('Stopped')
        base.localAvatar.lockControlsForEntry()
        camera.posQuatInterval(
            self.transitionLength,
            Vec3(-5, 9, 4.5), Vec3(-150, -2, 0),
            other=self.geom, blendType='easeOut',
            name=self.uniqueName('lerpCamera')
        ).start()
        taskMgr.doMethodLater(self.transitionLength, self.__createGui, self.uniqueName('openBoardGUI'))
        taskMgr.doMethodLater(self.guiUseTime, self.closeGui, self.uniqueName('boardAntisleep'))

    def __createGui(self, task=None):
        def guiResponse(value):
            self.closeGui(doingTeleport=value >= 1)
            self.handleTeleportAccepted() if value >= 1 else self.handleTeleportDenied()

        base.transitions.fadeScreen(0.5)
        self.dialog = TTDialog.TTDialog(
            style=TTDialog.TwoChoice,
            text=self.promptTeleportGUIDialogue,
            text_wordwrap=18.5,
            command=guiResponse)

        self.dialog.show()

        if task is not None:
            return task.done

    def closeGui(self, task=None, doingTeleport=False):
        base.transitions.noFade()
        if not doingTeleport:
            base.cr.playGame.getPlace().setState('Walk')
            base.localAvatar.unlockControlsForEntry()
        self.ignore('escape')
        if self.dialog:
            self.dialog.cleanup()
            self.dialog = None
        taskMgr.remove(self.uniqueName('boardAntisleep'))
        if task is not None:
            return task.done
