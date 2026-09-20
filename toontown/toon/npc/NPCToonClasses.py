    import random
from datetime import datetime
import time

from direct.actor.Actor import Actor
from direct.distributed import ClockDelta
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.showbase.MessengerGlobal import messenger
from direct.task.TaskManagerGlobal import Task, taskMgr
from panda3d.core import (ConfigVariableBool, Point3, Quat, TextNode, VBase4,
                          Vec3, VBase3)
from toontown.chat.constants.ChatGlobals import CFSpeech, CFTimeout

from toontown.nametag import Nametag, NametagGroup


from prisma.enums import ClubNameStatus
from otp.avatar.DistributedAvatar import DistributedAvatar
from toontown.battle import BattleProps, MovieUtil, SuitBattleGlobals
from toontown.battle import BattleSounds
from toontown.chat.enums.ChatChannel import ChatChannel
from toontown.chat.enums.ChatContentType import ChatContentType
from toontown.chat.enums.ChatNpcPreset import ChatNpcPreset
from toontown.gui.GUIGlobals import GUI_ICON_MODEL_PATH, GUI_TEXCARD_PREFIX
from toontown.inventory.enums.ItemEnums import ProfilePoseItemType, ChatStickersItemType, ItemType, FishingRodItemType
from toontown.chat.enums.ChatSystemMessagePreset import ChatSystemMessagePreset
from toontown.club import ClubLocalizer
from toontown.club.ClubEnums import ClubNotification
from toontown.club.DistributedClubManager import DistributedClubManager
from toontown.events.halloween.HalloweenPass import HalloweenPass
from toontown.events.halloween.HalloweenStoreGUI import HalloweenStoreGUI
from toontown.fishing.FishSellGUI import FishSellGUI
from toontown.toon.npc.shop.gui.NPCToonShopGUI import NPCToonShopGUI
from toontown.gui import TTDialog
from toontown.hood import ZoneUtil
from toontown.minigame.ClerkPurchase import ClerkPurchase
from toontown.quest import QuestParser
from toontown.quest3 import QuestLocalizer, QuestRejects
from toontown.quest3.base import QuestGlobals
from toontown.quest3.base.QuestChain import QuestChain
from toontown.quest3.base.QuestLine import QuestLine
from toontown.quest3.base.QuestReference import QuestId
from toontown.quest3.base.QuestText import QuestText
from toontown.quest3.gui.Quest3Choice import QuestChoice
from toontown.quest3.QuestEnums import QuestSource
from toontown.quest3.questlines.DirectiveQuestLine import DirectiveQuestLine
from toontown.quest3.objectives.VisitObjective import VisitObjective
from toontown.quest3.objectives.DeliverObjective import DeliverObjective
from toontown.quest3.objectives.ObtainObjective import ObtainObjective
from toontown.quest3.objectives.VisitHQOfficerObjective import VisitHQOfficerObjective
from toontown.quest3.objectives.DeliverGagObjective import DeliverGagObjective
from toontown.quest3.objectives.DeliverJellybeanObjective import DeliverJellybeanObjective
from toontown.racing.KartShopGlobals import KartShopGlobals
from toontown.racing.KartShopGui import KartShopGuiMgr
from toontown.toon import Experience
from toontown.toon.DistributedNPCToonBase import DistributedNPCToonBase
from toontown.toon.DistributedToon import DistributedToon
from toontown.toon.gui.ClubCreationGUI import ClubCreationGUI
from toontown.toon.gui.ClubNameRewriteGUI import ClubNameRewriteGUI
from toontown.toon.gui.ClubShopGUI import ClubShopGUI
from toontown.toon.npc import NPCToonLocalizer
from toontown.toon.npc.NPCToonConstants import *
from toontown.toon.TailorClothesGUI import TailorClothesGUI
from toontown.safezone.br.SnowmanSteve import SnowmanSteve
from toontown.toon.ToonDNA import ToonDNA
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.toonbase.CooldownManager import CooldownManager
from toontown.utils.ColorHelper import hexToPCol

from toontown.shop.ShopManager import ShopManager
from toontown.nametag.NametagFloat2d import NametagFloat2d
from toontown.nametag import NametagGlobals
from toontown.nametag.Nametag import Nametag
from toontown.nametag import Nametag2d
from toontown.nametag import Nametag3d

NPCToonClasses = {}


class NPCToonClass:
    """NPCToonClass: Decorator class used for the sole purpose of
    populating the NPCToonClasses global object with npc toon
    client representations.

    :param npcType: The NPCToonEnum value which to attach the
    desired class to.
    """

    def __init__(self, npcType: NPCToonEnum) -> None:
        self.npcType = npcType

    def __call__(self, cls) -> None:
        # Populate the repository with the type.
        NPCToonClasses[self.npcType] = cls
        return cls


@NPCToonClass(npcType=NPCToonEnum.REGULAR)
class DistributedNPCToon(DistributedNPCToonBase):
    def __init__(self, cr):
        super().__init__(cr)

        self.curQuestMovie = None
        self.questChoiceGui = None
        self.icon = None
        self.npc_id = None
        self.npc_toon = None
        self.npcType = TTLocalizer.NPCDefaultTag
        self.questNotifyTypes = [
            base.loader.loadModel('phase_3/models/gui/quest_exclaim.bam'),
            base.loader.loadModel('phase_3/models/gui/quest_exclaim_silver.bam'),
            base.loader.loadModel('phase_3/models/gui/quest_question.bam'),
            base.loader.loadModel('phase_3/models/gui/quest_question_silver.bam')
        ]
        for icon in self.questNotifyTypes:
            icon.setScale(4)
            icon.setZ(3)

    def setNpcId(self, npc_id):
        from toontown.toon.npc.NPCToons import NPCToonDict
        self.npc_id = npc_id
        self.npc_toon = NPCToonDict.get(npc_id)
        self.initPos()

    def initToonState(self):
        super().initToonState()
        self.initPos()

    def initPos(self):
        super().initPos()
        if not self.npc_toon:
            return

        # Set location
        if self.npc_toon.pos:
            while len(self.npc_toon.pos) < 4:
                self.npc_toon.pos.append(0)
            self.reparentTo(render)
            self.setPos(self.npc_toon.pos[0], self.npc_toon.pos[1], self.npc_toon.pos[2])
            self.setH(self.npc_toon.pos[3])

        # Tag
        if self.npc_toon.tag:
            self.npcType = self.npc_toon.tag
            self.setToonTag(self.npcType)

        # Name Wordwrap
        if self.npc_toon.nameWordwrap:
            self.nametag.setNameWordwrap(self.npc_toon.nameWordwrap)

        self.setAnimState("Neutral", 1.0)

    def allowedToTalk(self):
        return True

    def delayDelete(self):
        DistributedNPCToonBase.delayDelete(self)

        if self.curQuestMovie:
            curQuestMovie = self.curQuestMovie
            self.curQuestMovie = None
            curQuestMovie.timeout(fFinish=1)
            curQuestMovie.cleanup()

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        self.cleanupMovie()

        DistributedNPCToonBase.disable(self)

    def cleanupMovie(self):
        self.clearChat()
        self.ignore('chooseQuest')
        if self.questChoiceGui:
            self.questChoiceGui.destroy()
            self.questChoiceGui = None
        self.ignore(self.uniqueName('doneChatPage'))
        if self.curQuestMovie:
            self.curQuestMovie.timeout(fFinish=1)
            self.curQuestMovie.cleanup()
            self.curQuestMovie = None

    def handleCollisionSphereEnter(self, collEntry):
        base.cr.playGame.getPlace().request('Quest', self)
        self.sendUpdate('avatarEnter', [])
        self.nametag3d.setDepthTest(0)
        self.nametag3d.setBin('fixed', 0)

    def finishMovie(self, av, isLocalToon, elapsedTime):
        av.startLookAround()
        self.detectAvatars()
        if isLocalToon:
            self.cleanupMovie()
            self.startLookAround()
            self.initPos()
            self.showNametag2d()
            self.returnCamera()
            self.sendUpdate('setMovieDone', [])
            self.nametag3d.clearDepthTest()
            self.nametag3d.clearBin()

    def returnCamera(self):
        camera.wrtReparentTo(base.localAvatar)
        time = 0.5
        if self.previousCameraPosHpr:
            camera.posQuatInterval(
                time,
                self.previousCameraPosHpr[0], self.previousCameraPosHpr[1],
                other=base.localAvatar, blendType='easeInOut', name='npcCamTrack'
            ).start()
        else:
            avHeight = max(base.localAvatar.getHeight(), 3.0)
            scaleFactor = avHeight * 0.3333333333
            camera.posQuatInterval(
                1,
                (0, -9 * scaleFactor, avHeight), (0, 0, 0),
                other=base.localAvatar, blendType='easeInOut'
            ).start()

        base.localAvatar.lerpCameraFov(base.settings['fieldofview'], 1)

        def walk():
            base.cr.playGame.getPlace().setState('Walk')
            self.previousCameraPosHpr = []

        Sequence(Wait(time + .05), Func(walk)).start()

    def setupCamera(self, mode):
        camera.wrtReparentTo(render)
        if not self.previousCameraPosHpr:
            self.previousCameraPosHpr = [camera.getPos(base.localAvatar), camera.getHpr(base.localAvatar)]
        if mode == QUEST_MOVIE_QUEST_CHOICE:
            camera.posQuatInterval(1, (5, 9, self.getHeight() - 0.5), (155, -2, 0), other=self, blendType='easeInOut', name='npcCamTrack').start()
            base.localAvatar.lerpCameraFov(70, 1)
        else:
            camera.posQuatInterval(1, (-5, 9, self.getHeight() - 0.5), (-150, -2, 0), other=self, blendType='easeInOut', name='npcCamTrack').start()

    def setMovie(self, mode, npcId, avId, quests, timestamp, questId):
        isLocalToon = avId == base.localAvatar.doId
        if not isLocalToon:
            return

        questIds = [QuestId.fromStruct(questId) for questId in questId]

        if mode == QUEST_MOVIE_CLEAR:
            self.cleanupMovie()
            if isLocalToon:
                self.returnCamera()
            self.clearChat()
            self.startLookAround()
            self.detectAvatars()
            return

        if mode == QUEST_MOVIE_TIMEOUT:
            self.cleanupMovie()
            if isLocalToon:
                self.returnCamera()
            self.setPageNumber(0, -1)
            self.clearChat()
            self.startLookAround()
            self.detectAvatars()
            return

        av = base.cr.doId2do.get(avId)
        if av is None:
            self.notify.warning('Avatar %d not found in doId' % avId)
            return

        if mode == QUEST_MOVIE_REJECT:
            if isLocalToon:
                rejectString = QuestRejects.chooseQuestDialogReject(npcId)
                rejectString = QuestRejects.fillInQuestNames(rejectString, avName=av.getName(), av=av)
                if rejectString != '':
                    self.setChatAbsolute(rejectString, CFSpeech | CFTimeout)
                try:
                    base.cr.playGame.getPlace().setState('Walk')
                except AttributeError:
                    self.notify.warning("NPC %s (%s) 'NoneType' object has no attribute 'setState'" % (av.getName(), avId))
            return

        self.setupAvatars(av)

        fullString = ''
        toNpcId = None

        if isLocalToon:
            self.hideNametag2d()

        if mode == QUEST_MOVIE_COMPLETE:
            questId = questIds[0]
            questSource, chainId, objectiveId, subObjectiveId = questId.toStruct()
            scriptId = f'quest_complete_{questSource}_{chainId}_{objectiveId}_{subObjectiveId}'
            if isLocalToon:
                if QuestParser.questDefined(scriptId):
                    if self.curQuestMovie:
                        self.curQuestMovie.timeout()
                        self.curQuestMovie.cleanup()
                        self.curQuestMovie = None
                    self.curQuestMovie = QuestParser.NPCMoviePlayer(scriptId, av, self)
                    self.curQuestMovie.start()
                    return

                # OK, no quest script funny.
                # Set up the camera for the Boring Ques.t
                self.setupCamera(mode)

            # Get the NPC dialogue.
            questText = QuestLocalizer.getQuestText(questId)
            # If we are a kudos quest without dialogue, try going back one for the old ID
            if not questText.getDialogue()[0] and questSource == QuestSource.KudosQuest:
                questId.objectiveId -= 1 # objectiveId = 2, we want 1 (the old complete ID)
                questText = QuestLocalizer.getQuestText(questId)
            # If we still don't have one, the above failed and/or its some other unset dialogue
            if not questText.getDialogue()[0]:
                questText = QuestText(dialogue=("QuestText Undefined",))
            questDialogueList = questText.getDialogue()
            fullString += '\x07'.join(questDialogueList)

            # Set toNpcId.
            questObjective = QuestLine.getQuestObjectiveFromId(questId, quester=av).getObjectiveIndex(subObjectiveId)
            toNpcId = questObjective.getToNpcId()

        elif mode == QUEST_MOVIE_QUEST_CHOICE_CANCEL:
            if npcId in QuestLocalizer.QuestChoiceCancelUnique:
                fullString = QuestLocalizer.QuestChoiceCancelUnique[npcId]
            else:
                fullString = QuestLocalizer.QuestChoiceCancel

        elif mode == QUEST_MOVIE_INCOMPLETE:
            questSource, chainId, objectiveId, subObjectiveId = questIds[0].toStruct()
            scriptId = f'quest_incomplete_{questSource}_{chainId}_{objectiveId}_{subObjectiveId}'
            if isLocalToon:
                if QuestParser.questDefined(scriptId):
                    if self.curQuestMovie:
                        self.curQuestMovie.timeout()
                        self.curQuestMovie.cleanup()
                        self.curQuestMovie = None
                    self.curQuestMovie = QuestParser.NPCMoviePlayer(scriptId, av, self)
                    self.curQuestMovie.start()
                    return
                self.setupCamera(mode)

        elif mode == QUEST_MOVIE_ASSIGN:
            questSource, chainId, objectiveId, subObjectiveId = questIds[0].toStruct()
            scriptId = f'quest_complete_{questSource}_{chainId}_{objectiveId}_{subObjectiveId}'
            if isLocalToon:
                if QuestParser.questDefined(scriptId):
                    if self.curQuestMovie:
                        self.curQuestMovie.timeout()
                        self.curQuestMovie.cleanup()
                        self.curQuestMovie = None
                    self.curQuestMovie = QuestParser.NPCMoviePlayer(scriptId, av, self)
                    self.curQuestMovie.start()
                    return
                self.setupCamera(mode)

            # Get the NPC dialogue.
            questText = QuestLocalizer.getQuestText(questIds[0], assigned=True)
            if not questText.getDialogue()[0]:
                questText = QuestText(dialogue=("QuestText Undefined",))
            questDialogueList = questText.getDialogue()
            fullString += '\x07'.join(questDialogueList)

        elif mode == QUEST_MOVIE_QUEST_CHOICE:
            if isLocalToon:
                if npcId in QuestLocalizer.QuestChoiceUnique:
                    dialog = QuestLocalizer.QuestChoiceUnique[npcId]
                else:
                    dialog = QuestLocalizer.QuestChoice
                self.setupCamera(mode)
                if dialog != '':
                    self.setChatAbsolute(dialog, CFSpeech)
                self.acceptOnce('chooseQuest', self.sendChooseQuest)
                isSuit = self.npc_id in QuestGlobals.SUIT_NPC_IDS
                self.questChoiceGui = QuestChoice(suit=isSuit)
                self.questChoiceGui.setQuests(questIds, ChoiceTimeout)
            return

        fullString = QuestRejects.fillInQuestNames(fullString, avName=av.getName(), fromNpcId=npcId, toNpcId=toNpcId)
        if isLocalToon:
            self.acceptOnce(self.uniqueName('doneChatPage'), self.finishMovie, extraArgs=[av, isLocalToon])
            self.clearChat()
            self.setLocalPageChat(fullString, 1)

    def sendChooseQuest(self, questId=None):
        if self.questChoiceGui:
            self.questChoiceGui.destroy()
            self.questChoiceGui = None
        if questId is not None:
            # We chose a quest, so roll with it.
            self.sendUpdate('chooseQuest', [questId])
        else:
            # It seems that we have cancelled or timed out.
            self.sendUpdate('cancelChooseQuest')


@NPCToonClass(npcType=NPCToonEnum.PLANT)
class DistributedEmptyNPC(DistributedNPCToon):
    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)

        self.npcType = ''

        self.pendingResponse = False
        self.plantData = None

    def initToonState(self):
        npcOrigin = base.cr.playGame.hood.loader.geom
        if not npcOrigin.isEmpty():
            self.reparentTo(npcOrigin)
            self.initPos()
            self.__fixNametagVisibility()

    def __fixNametagVisibility(self):
        self.setNameVisible(False)
        self.hideNametag2d()
        self.hideNametag3d() # disabled right now to fix crash
        self.nametag.getNametag2d().setContents(Nametag.CSpeech)
        self.nametag.getNametag3d().setContents(Nametag.CSpeech)

    def startLookAround(self):
        return

    def generateToon(self):
        self.deleteDropShadow()
        return  # don't load in the toon

    def getDialogueArray(self):
        return self.dialogArray

    def setBottomItem(self, *args, **kwargs):
        return

    def setTopItem(self, *args, **kwargs):
        return

    def getShadowJoint(self):
        """
        :return: the shadow joint
        """
        if hasattr(self, 'shadowJoint'):
            return self.shadowJoint
        shadowJoint = NodePath('shadowJoint')

        self.shadowJoint = shadowJoint
        return shadowJoint

    def getNametagJoints(self):
        """
        :return: a list of CharacterJoints for each LOD (1000, 500, 250)
        """
        return []


class DistributedNPCClerk(DistributedNPCToonBase):
    def __init__(self, cr):
        DistributedNPCToonBase.__init__(self, cr)
        self.npcType = 'Gag Clerk'
        self.lastCollision = 0
        self.purchaseGui = None

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        self.destroyDialog()
        DistributedNPCToonBase.disable(self)

    def destroyDialog(self):
        self.ignoreAll()
        self.clearChat()
        taskMgr.remove(self.uniqueName('popupPurchaseGUI'))
        taskMgr.remove(self.uniqueName('lerpCamera'))

        if self.purchaseGui:
            self.purchaseGui.exit()
            self.purchaseGui.unload()
            self.purchaseGui = None

    def handleCollisionSphereEnter(self, collEntry):
        if self.lastCollision > time.time():
            return

        self.lastCollision = time.time() + 2.5

        if not base.localAvatar.getMoney():
            self.setChatAbsolute(TTLocalizer.ClerkNeedBeans, CFSpeech | CFTimeout)
            return

        self.d_setState(CLERK_GREETING)
        base.cr.playGame.getPlace().request('Purchase')
        camera.wrtReparentTo(render)
        camera.posQuatInterval(1, Vec3(-5, 9, self.getHeight() - 0.5), Vec3(-150, -2, 0), other=self, blendType='easeOut', name=self.uniqueName('lerpCamera')).start()
        taskMgr.doMethodLater(1.0, self.popupPurchaseGUI, self.uniqueName('popupPurchaseGUI'))

    def d_setInventory(self, inventory, money):
        self.sendUpdate('setInventory', [inventory, money])

    def d_setState(self, state):
        self.sendUpdate('setState', [0, state])

    def setState(self, avId, state):
        av = base.cr.doId2do.get(avId)

        if not av:
            return

        if state == CLERK_GOODBYE:
            self.setChatAbsolute(TTLocalizer.ClerkGoodbye, CFSpeech | CFTimeout)
        elif state == CLERK_GREETING:
            self.headsUp(av)
            self.setChatAbsolute(TTLocalizer.ClerkGreeting, CFSpeech | CFTimeout)
            return
        elif state == CLERK_TOOKTOOLONG:
            self.setChatAbsolute(TTLocalizer.ClerkTimeout, CFSpeech | CFTimeout)

        self.initToonState()

    def popupPurchaseGUI(self, task):
        self.clearChat()
        self.acceptOnce('purchaseClerkDone', self.__handlePurchaseDone)
        self.purchaseGui = ClerkPurchase(base.localAvatar, CLERK_COUNTDOWN_TIME, 'purchaseClerkDone')
        self.purchaseGui.load()
        self.purchaseGui.enter()

    def __handlePurchaseDone(self, state):
        self.d_setInventory(base.localAvatar.inventory.makeNetString(), base.localAvatar.getMoney())
        self.destroyDialog()
        self.freeAvatar()
        self.detectAvatars()
        self.d_setState(state)


@NPCToonClass(npcType=NPCToonEnum.GNG_CLERK)
class DistributedNPCGagAndGoClerk(DistributedNPCClerk):

    def __init__(self, cr):
        DistributedNPCClerk.__init__(self, cr)
        self.npcType = "Gag n' Go Clerk"
        self.lastCollision = 0
        self.purchaseGui = None

        self.mSphere = CollisionTube(0.0, 1.0, 0.0, 0.0, 1.0, 5.0, 18)
        self.mSphere.setTangible(0)
        self.mSphereNode = CollisionNode(f'mSphereNode-GagAndGo-{id(self)}')
        self.mSphereNode.addSolid(self.mSphere)
        self.mSphereNodePath = self.attachNewNode(self.mSphereNode)
        self.mSphereNodePath.hide()
        self.mSphereNode.setCollideMask(ToontownGlobals.WallBitmask)

    def announceGenerate(self):
        super().announceGenerate()
        self.setupToonNodes()
        self.accept("toonDied", self.toonDied)

    def toonDied(self, _) -> None:
        self.showSticker(ChatStickersItemType.GreenedCat)

    def disable(self):
        self.ignoreAll()
        self.mSphereNodePath.removeNode()
        self.mSphereNodePath = None
        if getattr(base.cr.playGame, 'hood', None) and getattr(base.cr.playGame.hood, 'loader', None):
            base.musicMgr.stopMusic(base.cr.playGame.hood.loader.gagAndGoMusic_preloaded)
        super().disable()

    def detectAvatars(self):
        DistributedNPCClerk.detectAvatars(self)
        self.accept('enter' + self.mSphereNode.getName(), self.startMusic)
        self.accept('exit' + self.mSphereNode.getName(), self.stopMusic)

    def ignoreAvatars(self):
        DistributedNPCClerk.ignoreAvatars(self)
        self.ignore('enter' + self.mSphereNode.getName())

    def startMusic(self, collEntry):
        if collEntry.getIntoNode().getName() != self.mSphereNode.getName():
            return

        place = base.cr.playGame.getPlace()
        if place and place.getState() == 'Walk':
            base.musicMgr.crossfadeIntoMusic(base.cr.playGame.hood.loader.gagAndGoMusic_preloaded, duration=1, volume=1.0, musicCode=base.cr.playGame.hood.loader.gagAndGoMusic)

    def stopMusic(self, collEntry):
        if collEntry.getIntoNode().getName() != self.mSphereNode.getName():
            return

        place = base.cr.playGame.getPlace()
        if place and place.getState() == 'Walk':
            base.musicMgr.crossfadeIntoMusic(base.cr.playGame.hood.loader.music_preloaded, duration=1, volume=0.8, musicCode=base.cr.playGame.hood.loader.music)

    def initToonState(self):
        self.setAnimState('Neutral', 1.05, None, None)
        self.dropShadow.hide()
        npcOrigin = self.cr.playGame.hood.loader.geom.find('**/npc_gng_clerk_origin_%s;+s' % self.posIndex)
        if not npcOrigin.isEmpty():
            self.reparentTo(npcOrigin)
            self.clearMat()
            self.dropShadow.hide()
        else:
            npcOrigin = self.cr.playGame.hood.loader.geom.find('**/npc_gng_clerk_origin_0;+s')
            if not npcOrigin.isEmpty():
                self.reparentTo(npcOrigin)
                self.clearMat()
            else:
                self.reparentTo(render)
                # self.notify.error('announceGenerate: Could not find npc_gng_clerk_origin_' + str(self.posIndex))
        return

    def handleCollisionSphereEnter(self, collEntry):
        place = base.cr.playGame.getPlace()
        if place and place.getState() != 'Walk':
            return

        super().handleCollisionSphereEnter(collEntry)

    # Override the purchase GUI method to bring up our more expensive store
    def popupPurchaseGUI(self, task):
        self.clearChat()
        self.acceptOnce('purchaseClerkDone', self.__handlePurchaseDone)
        self.purchaseGui = ClerkPurchase(base.localAvatar, CLERK_COUNTDOWN_TIME, 'purchaseClerkDone')
        self.purchaseGui.setCostMultiplier(2)
        self.purchaseGui.load()
        self.purchaseGui.enter()

    def __handlePurchaseDone(self, state):
        self.d_setInventory(base.localAvatar.inventory.makeNetString(), base.localAvatar.getMoney())
        self.destroyDialog()
        self.freeAvatar()
        self.detectAvatars()
        self.d_setState(state)


@NPCToonClass(npcType=NPCToonEnum.CLUB_CREATION)
class DistributedNPCClubCreation(DistributedNPCToon):
    TRANSITION_LENGTH = 1.0

    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)
        self.headPrefix = '/models/char/toons/head/doevinci-heads-'
        self.npcType = 'Club Creation'
        self.gui = None
        self.accept(ClubCreationGUI.msg_onExit, self.__onGuiClose)

    def handleCollisionSphereEnter(self, collEntry):
        # First, check if the Toon is in the Tutorial.
        if QuestGlobals.isInTutorial(base.localAvatar):
            # They're in the toontorial, tell them to go say hi to Flippers.
            self._npcSayPhrase(ClubLocalizer.ClubCreationNPCPhrases[0])
        # Is the clubMgr in the club?
        elif self.clubMgr.isInClub():
            # The player is in a club. Ignore em, unless they're the owner.
            if not self.localAvIsOwner():
                # Ignore phrase
                self._npcSayPhrase(ClubLocalizer.ClubCreationNPCPhrases[1])
            else:
                # Ignore them, unless we're interested in changing the club name.
                if self.clubContainer.nameStatus == ClubNameStatus.NAME_APPROVED:
                    # Ignooore. They are enjoying their club.
                    self._npcSayPhrase(ClubLocalizer.ClubCreationNPCPhrases[1])
                elif self.clubContainer.nameStatus == ClubNameStatus.NAME_REQUESTED:
                    # They are waiting for their name.
                    self._npcSayPhrase(ClubLocalizer.ClubCreationNPCPhrases[2])
                else:
                    # OK, we are looking to change the club name.
                    base.cr.playGame.getPlace().setState('Stopped')
                    self.lookAt(base.localAvatar)
                    self._cameraDoEnterSeq()
                    self._openStoreGuiSeq(rewriteGui=True)
                    self._npcSayPhrase(ClubLocalizer.ClubCreationNPCPhrases[{
                        ClubNameStatus.NAME_CHANGING: 3,
                        ClubNameStatus.NAME_DENIED:   4,
                        ClubNameStatus.NAME_FAILED:   11,
                    }.get(self.clubContainer.nameStatus)])
        else:
            # The player is NOT in a club. Perhaps they would like to create a club!
            base.cr.playGame.getPlace().setState('Stopped')
            self._cameraDoEnterSeq()
            self._openStoreGuiSeq(rewriteGui=False)
            self._npcSayPhrase(ClubLocalizer.ClubCreationNPCPhrases[5])

    def __popupClubCreationGUI(self, rewriteGui):
        if not rewriteGui:
            self.gui = ClubCreationGUI(self)
        else:
            self.gui = ClubNameRewriteGUI(self)

    def __onGuiClose(self, clubMade=False, nameRewriteGui=False, timeout=False):
        """Called when the ClubCreationGUI is closed."""
        if timeout:
            # The player timed out.
            self._npcSayPhrase(ClubLocalizer.ClubCreationNPCPhrases[10])
            return
        if not nameRewriteGui:
            # We weren't rewriting name -- so just do standard close line.
            self._npcSayPhrase(ClubLocalizer.ClubCreationNPCPhrases[7 if clubMade else 6])
        else:
            # We were rewriting name -- so use name rewrite lines.
            self._npcSayPhrase(ClubLocalizer.ClubCreationNPCPhrases[9 if clubMade else 8])
        self.startLookAround()

    """
    Transition methods
    """

    def _cameraDoEnterSeq(self):
        """Camera does the enter sequence, and pops up the GUI"""
        camera.posQuatInterval(self.TRANSITION_LENGTH, Vec3(-5, 9, self.getHeight() - 0.5), Vec3(-150, -2, 0), other=self,
                               blendType='easeOut', name=self.uniqueName('lerpCamera')).start()
        self.stopLookAround()

    def _openStoreGuiSeq(self, rewriteGui=False):
        taskMgr.doMethodLater(self.TRANSITION_LENGTH, self.__popupClubCreationGUI,
                              self.uniqueName('__popupStoreGUI'), extraArgs=[rewriteGui])

    def _npcSayPhrase(self, phraseList):
        """Makes the NPC say a phrase from the phrase list."""
        phrase = random.choice(phraseList).replace('_avName_', base.localAvatar.getName())
        self.setChatAbsolute(phrase, CFSpeech | CFTimeout)
        self.headsUp(base.localAvatar)

    """
    Properties
    """

    @property
    def clubMgr(self):
        return base.cr.clubMgr

    @property
    def clubContainer(self):
        return self.clubMgr.clubContainer

    @property
    def clubNameStatus(self):
        return self.clubContainer.nameStatus

    def localAvIsOwner(self):
        return self.clubContainer.localAvIsOwner()


@NPCToonClass(npcType=NPCToonEnum.CLUB_SHOP)
class DistributedNPCClubShop(DistributedNPCToon):
    TRANSITION_LENGTH = 1.0

    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)
        # self.eyePath = 'phase_3/maps/toon/webstereyes.png'
        self.headPrefix = '/models/char/toons/head/brovinci-heads-'
        self.npcType = 'Club Shop'
        self.gui = None
        self.accept(ClubShopGUI.msg_onExit, self.__onGuiClose)
        self.accept(ClubShopGUI.msg_onPurchase, self.__onItemPurchase)
        self.accept(DistributedClubManager.notification, self.processClubCallback)

    def handleCollisionSphereEnter(self, collEntry):
        # First, check if the Toon is in the Tutorial.
        if QuestGlobals.isInTutorial(base.localAvatar):
            # They're in the toontorial, tell them to go say hi to Flippers.
            self._npcSayPhrase(ClubLocalizer.ClubShopNPCPhrases[0])
        # Is the clubMgr in the club?
        elif self.clubMgr.isInClub():
            # The player is in a club, yay!
            base.cr.playGame.getPlace().setState('Stopped')
            self._cameraDoEnterSeq()
            self._openStoreGuiSeq()
            self._npcSayPhrase(ClubLocalizer.ClubShopNPCPhrases[1])
        else:
            # The player is not in a club. Deny them.
            self._npcSayPhrase(ClubLocalizer.ClubShopNPCPhrases[2])

    def __popupClubShopGUI(self, task):
        self.gui = ClubShopGUI(self)

    def __onGuiClose(self, purchased=False, timeout=False, rolled=False):
        """Called when the ClubShopGUI is closed."""
        if rolled:
            # The player got kicked from their club IN the GUI.
            self._npcSayPhrase(ClubLocalizer.ClubShopNPCPhrases[7])
        elif timeout:
            # The player timed out.
            self._npcSayPhrase(ClubLocalizer.ClubShopNPCPhrases[5])
        elif purchased:
            # The player purchased something
            self._npcSayPhrase(ClubLocalizer.ClubShopNPCPhrases[3])
        else:
            # The player did not do anything
            self._npcSayPhrase(ClubLocalizer.ClubShopNPCPhrases[4])
        self.startLookAround()

    def __onItemPurchase(self, success):
        self._npcSayPhrase(ClubLocalizer.ClubShopNPCPhrases[3 if success else 6])

    def processClubCallback(self, context: ClubNotification, args: list):
        """Process callback data from a ClubNotification."""
        if context == ClubNotification.ClubShop_Success:
            self._npcSayPhrase(ClubLocalizer.ClubShopNPCPhrases[3])
        elif context == ClubNotification.ClubShop_Failure:
            self._npcSayPhrase(ClubLocalizer.ClubShopNPCPhrases[6])
        elif context == ClubNotification.ClubShop_Equip:
            self._npcSayPhrase(ClubLocalizer.ClubShopNPCPhrases[8])

    """
    Transition methods
    """

    def _cameraDoEnterSeq(self):
        """Camera does the enter sequence, and pops up the GUI"""
        camera.posQuatInterval(self.TRANSITION_LENGTH, Vec3(-5, 9, self.getHeight() - 0.5), Vec3(-150, -2, 0), other=self,
                               blendType='easeOut', name=self.uniqueName('lerpCamera')).start()
        self.stopLookAround()

    def _openStoreGuiSeq(self):
        taskMgr.doMethodLater(self.TRANSITION_LENGTH, self.__popupClubShopGUI, self.uniqueName('__popupStoreGUI'))

    def _npcSayPhrase(self, phraseList):
        """Makes the NPC say a phrase from the phrase list."""
        phrase = random.choice(phraseList).replace('_avName_', base.localAvatar.getName())
        self.setChatAbsolute(phrase, CFSpeech | CFTimeout)
        self.headsUp(base.localAvatar)

    """
    Properties
    """

    @property
    def clubMgr(self):
        return base.cr.clubMgr

    @property
    def clubContainer(self):
        return self.clubMgr.clubContainer

    def localAvIsOwner(self):
        return self.clubContainer.localAvIsOwner()


@NPCToonClass(npcType=NPCToonEnum.BUBBY)
class DistributedNPCBubby(DistributedEmptyNPC):
    def __init__(self, cr):
        DistributedEmptyNPC.__init__(self, cr)

        self.npcType = ''
        self.dialogArrayDefault = [base.loader.loadSfx('phase_11/audio/dial/cc_s_dlg_plant_rustle.ogg')] * 9
        self.dialogArrayChime = [base.loader.loadSfx('phase_11/audio/dial/cc_s_dlg_plant_rustle_chimes.ogg')] * 9
        self.dialogArray = self.dialogArrayDefault
        self.chatNpcPresetType = ChatNpcPreset.Plant

        self.pendingResponse = False

    def initPos(self):
        self.setPos(-15, 35, 1)

        # These plants are taller if in a cog area, for scaling to cog suits.
        self.setHeight(4.7)

    def getCollSphereRadius(self):
        return 5.5

    def getDialogueArray(self):
        return self.dialogArray

    def handleCollisionSphereEnter(self, collEntry):
        if self.pendingResponse:
            return

        self.pendingResponse = True
        self.sendUpdate('requestCheck')

    def requestCheckResponse(self, response):
        taskMgr.doMethodLater(3.0, self.endCooldown, self.uniqueName('requestCooldown'))
        if response == 0:
            # Bubby isn't a part of the puzle, so he will always "error"
            self.dialogArray = self.dialogArrayDefault
            self.setChatAbsolute(TTLocalizer.PlantDialogDefault, CFSpeech | CFTimeout)

    def requestCheckChatResponse(self, response):
        taskMgr.doMethodLater(0.5, self.endCooldown, self.uniqueName('requestCooldown'))
        self.dialogArray = self.dialogArrayChime
        self.setChatAbsolute(response, CFSpeech | CFTimeout)

    def endCooldown(self, _):
        self.pendingResponse = False


@NPCToonClass(npcType=NPCToonEnum.EASTER)
class DistributedNPCEaster(DistributedNPCToon):

    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)
        self.npcType = "Eggstravagant Rabbit"

    def initToonState(self):
        self.initPos()
        return
        self.setHat(111, 0, 0)
        self.setBackpack(76, 0, 0)

    def initPos(self):
        self.setPos(-138.17, -37.3, 0.525)
        self.setH(-62)


@NPCToonClass(npcType=NPCToonEnum.ELF)
class DistributedNPCElf(DistributedNPCToon):

    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)
        self.npcType = "Elf"
        self.hints = [
            [datetime(2018, 12, 18, 23), datetime(2018, 12, 19, 23), 1],
            [datetime(2018, 12, 19, 23), datetime(2018, 12, 20, 23), 2],
            [datetime(2018, 12, 20, 23), datetime(2018, 12, 21, 23), 3],
            [datetime(2018, 12, 21, 23), datetime(2018, 12, 22, 23), 4],
            [datetime(2018, 12, 22, 23), datetime(2018, 12, 23, 23), 5],
            [datetime(2018, 12, 23, 23), datetime(2018, 12, 24, 23), 6],
            [datetime(2018, 12, 24, 23), datetime(2018, 12, 25, 23), 7],
            [datetime(2018, 12, 25, 23), datetime(2018, 12, 26, 23), 8],
            [datetime(2018, 12, 26, 23), datetime(2018, 12, 27, 23), 9],
            [datetime(2018, 12, 27, 23), datetime(2018, 12, 28, 23), 10],
            [datetime(2018, 12, 28, 23), datetime(2018, 12, 29, 23), 11],
        ]

    def initToonState(self):
        self.initPos()

    def initPos(self):
        if self.zoneId == ToontownGlobals.ToonselTown:
            self.setPos(-5.252, 301.172, 32.860)
            self.setH(131.719)
        else:
            self.setPos(-38.966, 29.218, 6.192)
            self.setH(138)

    def handleCollisionSphereEnter(self, col):
        for l in self.hints:
            if l[0] <= datetime.utcnow() < l[1]:
                key = l[2]
                break

        base.cr.playGame.getPlace().request('Quest', self)
        self.sendUpdate('avatarEnter', [])
        self.nametag3d.setDepthTest(0)
        self.nametag3d.setBin('fixed', 0)
        return


@NPCToonClass(npcType=NPCToonEnum.ELPHABAT)
class DistributedNPCElphabat(DistributedNPCToon):
    elphabatPos = {
        # npcId: (pos), H
        7051: ((62.894, -164.690, 3.025), -14),  # ttc
        7053: ((-99.235, 92.576, 3.280), -110),  # bb
        7055: ((108.421, -58.987, 14.762), -17),  # yott
        7057: ((-8.174, 282.942, 14.029), 0),  # dg
        7059: ((105, -12.758, -10), 60),  # mm
        7061: ((-161.56, -31, 6.192), -110),  # tb
        7063: ((-76.035, -24.918, 3.334), 68),  # aa
        7065: ((-70, 12, 1.583), 90),  # ddl
    }

    # Constant codes to use for decrypting chat phrases upon certain interactions
    START_INTERACT_CODE = 1
    EXIT_INTERACT_CODE = 2

    CLIENT_SIDE_CONTEXTS = (
        START_INTERACT_CODE,
        EXIT_INTERACT_CODE
    )

    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)
        self.npcType = "Witch"
        self.storeGui = None
        self.interactCooldown = CooldownManager(2)
        self.responseCooldown = CooldownManager(3)

    def initToonState(self):
        self.initPos()

    def initPos(self):
        self.setPos(*self.elphabatPos[self.npc_id][0])
        self.setH(self.elphabatPos[self.npc_id][1])
        # Setting accessories here so they aren't overwritten by the holiday.
        # self.setBackpack(26, 0, 0)
        # self.setShoes(3, 50, 0)
        # self.setHat(39, 23, 0)

    def handleCollisionSphereEnter(self, collEntry):
        if not self.interactCooldown.check(base.localAvatar.doId).outcome:
            return

        # Freeze the toon and make them look at us
        base.cr.playGame.getPlace().setState('Stopped')
        self.lookAt(base.localAvatar)

        TRANSITION_LENGTH = 1.0
        # Do a pretty camera pan into opening the GUI
        camera.posQuatInterval(TRANSITION_LENGTH, Vec3(-5, 9, self.getHeight() - 0.5), Vec3(-150, -2, 0), other=self,
                               blendType='easeOut', name=self.uniqueName('lerpCamera')).start()

        taskMgr.doMethodLater(TRANSITION_LENGTH, self.__popupStoreGUI, self.uniqueName('__popupStoreGUI'))

        # Tell server we interacted with a ctx code of 1
        self.sendUpdate('toonInteracted', [self.START_INTERACT_CODE])

    def __popupStoreGUI(self, _=None):
        self.storeGui = HalloweenStoreGUI(self)

    def doBuy(self, updateName, cost, material, id, extra=None):
        # no spaces allowed!!!!
        updateName = updateName.replace(' ', '')
        if updateName in ('requestDailyBoosterPurchase'):
            self.sendUpdate(updateName, [cost, material, id, extra])
        else:
            self.sendUpdate(updateName, [cost, material, id])

    def doExit(self):
        # Tell the server we exited
        self.sendUpdate('toonInteracted', [self.EXIT_INTERACT_CODE])

    def handleBuyResponse(self, code, avId):
        if self.storeGui and avId == base.localAvatar.getDoId():
            self.setChatAbsolute(TTLocalizer.halloweenWitchResponses[code], CFSpeech | CFTimeout)
            self.storeGui.updatePage()
            self.cr.chatManager.sendSystemMessageLocally(TTLocalizer.halloweenWitchResponses[code], senderName='Elphabat', preset=ChatSystemMessagePreset.Halloween)
            self.storeGui.updateMaterialAmounts()
            messenger.send('halloweenStoreCleanupDialogue')

    # Called from AI, given avId that triggered this interaction, in which context, and which phrase
    def handleInteraction(self, avId, ctxCode, phraseId):

        # For this NPC, we ignore certain contexts if the associated avId isn't us,
        # Remove this check if you want server side npc elphabat again
        if ctxCode in self.CLIENT_SIDE_CONTEXTS and avId != base.localAvatar.doId:
            return

        # Get av associated with interaction, if av is not real don't do anything
        av = base.cr.doId2do.get(avId)
        if not av:
            return

        # Get phrases based on context
        phraseChoices = TTLocalizer.halloweenWitchEnterExitResponses[ctxCode]
        # Get which phrase needed
        phrase = phraseChoices[phraseId]

        # Replace _avId_ if needed
        phrase = phrase.replace('_avName_', av.getName())

        # Say it
        self.setChatAbsolute(phrase, CFSpeech | CFTimeout)


@NPCToonClass(npcType=NPCToonEnum.FIREWORK)
class DistributedNPCFirework(DistributedNPCToon):
    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)
        self.npcType = "Firework Enthusiast"
        self.colors = {
            'Happie Newbear': 0,  # red
            'Pawst Midnight': 1,  # green
            'Jan Furrst': 2,  # blue
        }
        self.nameToPos = {
            'Happie Newbear': [(-14.209, -81.987, 0.539), -1.223],
            'Pawst Midnight': [(-110.039, -81.766, 0.525), -49.858],
            'Jan Furrst': [(-11.443,  85.704,  1.188), -165.025],
        }

    def initToonState(self):
        self.initPos()

    def initPos(self):
        # self.setBackpack(40, 48, 0)
        self.setPos(*self.nameToPos[self.name][0])
        self.setH(self.nameToPos[self.name][1])


@NPCToonClass(npcType=NPCToonEnum.FISHERMAN)
class DistributedNPCFisherman(DistributedNPCToonBase):

    def __init__(self, cr):
        DistributedNPCToonBase.__init__(self, cr)
        self.isLocalToon = 0
        self.av = None
        self.button = None
        self.fishGui = None
        self.nextCollision = 0
        self.npcType = 'Fisherman'
        return

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('popupFishGUI'))
        taskMgr.remove(self.uniqueName('lerpCamera'))
        if self.fishGui:
            self.fishGui.destroy()
            self.fishGui = None
        self.av = None
        DistributedNPCToonBase.disable(self)
        return

    def generate(self):
        """
        Called when the DistributedObject is reintroduced to the world, either for the first time or from the cache.
        """
        DistributedNPCToonBase.generate(self)
        self.fishGuiDoneEvent = 'fishGuiDone'

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        DistributedNPCToonBase.announceGenerate(self)

    def initToonState(self):
        self.setAnimState('Neutral', 1.05, None, None)
        npcOrigin = self.cr.playGame.hood.loader.geom.find('**/npc_fisherman_origin_%s;+s' % self.posIndex)
        if not npcOrigin.isEmpty():
            self.reparentTo(npcOrigin)
            self.clearMat()
        else:
            npcOrigin = self.cr.playGame.hood.loader.geom.find('**/npc_fisherman_origin_0;+s')
            if not npcOrigin.isEmpty():
                self.reparentTo(npcOrigin)
                self.clearMat()
            else:
                self.notify.error('announceGenerate: Could not find npc_fisherman_origin_' + str(self.posIndex))
        return

    def getCollSphereRadius(self):
        return 1.0

    def handleCollisionSphereEnter(self, collEntry):
        self.currentTime = time.time()
        if self.nextCollision > self.currentTime:
            self.nextCollision = self.currentTime + 2
        else:
            base.cr.playGame.getPlace().request('Purchase')
            self.sendUpdate('avatarEnter', [])
            self.nextCollision = self.currentTime + 2

    def __handleUnexpectedExit(self):
        self.notify.warning('unexpected exit')
        self.av = None
        return

    def setupAvatars(self, av):
        self.ignoreAvatars()
        av.stopLookAround()
        av.lerpLookAt(Point3(-0.5, 4, 0), time=0.5)
        self.stopLookAround()
        self.lerpLookAt(Point3(av.getPos(self)), time=0.5)

    def resetFisherman(self):
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('popupFishGUI'))
        taskMgr.remove(self.uniqueName('lerpCamera'))
        if self.fishGui:
            self.fishGui.destroy()
            self.fishGui = None
        self.show()
        self.startLookAround()
        self.detectAvatars()
        self.clearMat()
        if self.isLocalToon:
            self.freeAvatar()
        return Task.done

    def setMovie(self, mode, npcId, avId, extraArgs, timestamp):
        timeStamp = ClockDelta.globalClockDelta.localElapsedTime(timestamp)
        self.remain = CLERK_COUNTDOWN_TIME - timeStamp
        self.npcId = npcId
        self.isLocalToon = avId == base.localAvatar.doId
        if mode == SELL_MOVIE_CLEAR:
            return
        if mode == SELL_MOVIE_TIMEOUT:
            taskMgr.remove(self.uniqueName('lerpCamera'))
            if self.isLocalToon:
                base.transitions.noFade()
                self.ignore(self.fishGuiDoneEvent)
                if self.fishGui:
                    self.fishGui.destroy()
                    self.fishGui = None
            self.setChatAbsolute(TTLocalizer.ClerkTimeout, CFSpeech | CFTimeout)
            self.resetFisherman()
        elif mode == SELL_MOVIE_START:
            self.av = base.cr.doId2do.get(avId)
            if self.av is None:
                self.notify.warning('Avatar %d not found in doId' % avId)
                return
            else:
                self.accept(self.av.uniqueName('disable'), self.__handleUnexpectedExit)
            self.setupAvatars(self.av)
            if self.isLocalToon:
                camera.wrtReparentTo(render)
                quat = Quat()
                quat.setHpr((-150, -2, 0))
                camera.posQuatInterval(1, Point3(-5, 9, base.localAvatar.getHeight() - 0.5), quat, other=self, blendType='easeOut').start()
            if self.isLocalToon:
                taskMgr.doMethodLater(1.0, self.popupFishGUI, self.uniqueName('popupFishGUI'))
        elif mode == SELL_MOVIE_COMPLETE:
            chatStr = TTLocalizer.FisherManThanksFish
            self.setChatAbsolute(chatStr, CFSpeech | CFTimeout)
            self.resetFisherman()
        elif mode == SELL_MOVIE_TROPHY:
            self.av = base.cr.doId2do.get(avId)
            if self.av is None:
                self.notify.warning('Avatar %d not found in doId' % avId)
                return
            else:
                numFish, totalNumFish = extraArgs
                self.setChatAbsolute(TTLocalizer.FishingClerkTrophy % (numFish, totalNumFish), CFSpeech | CFTimeout)
            self.resetFisherman()
        elif mode == SELL_MOVIE_NOFISH:
            chatStr = TTLocalizer.FishingClerkNoFish
            self.setChatAbsolute(chatStr, CFSpeech | CFTimeout)
            self.resetFisherman()
        return

    def __handleSaleDone(self, sell):
        self.ignore(self.fishGuiDoneEvent)
        self.sendUpdate('completeSale', [sell])
        self.fishGui.destroy()
        self.fishGui = None
        base.transitions.noFade()
        return

    def popupFishGUI(self, task):
        self.setChatAbsolute('', CFSpeech)
        self.acceptOnce(self.fishGuiDoneEvent, self.__handleSaleDone)
        self.fishGui = FishSellGUI(self.fishGuiDoneEvent)
        base.transitions.fadeScreen(0.5)


@NPCToonClass(npcType=NPCToonEnum.FLIPPYTOONHALL)
class DistributedNPCFlippyInToonHall(DistributedNPCToon):

    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)
        self.npcType = "Mayor"

    def getCollSphereRadius(self):
        return 4

    def initPos(self):
        self.clearMat()
        self.setScale(1.25)

    def handleCollisionSphereEnter(self, collEntry):
        """
        Response for a toon walking up to this NPC
        """
        if self.allowedToTalk():
            # Lock down the avatar for quest mode
            base.cr.playGame.getPlace().request('Quest', self)
            # Tell the server
            self.sendUpdate('avatarEnter', [])
            # make sure this NPCs chat balloon is visible above all others for the locekd down avatar
            self.nametag3d.setDepthTest(0)
            self.nametag3d.setBin('fixed', 0)
            self.lookAt(base.localAvatar)

    # Overriding this because the camera was too low by default.
    def setupCamera(self, mode):
        camera.wrtReparentTo(render)
        if not self.previousCameraPosHpr:
            self.previousCameraPosHpr = [camera.getPos(base.localAvatar), camera.getHpr(base.localAvatar)]
        if mode == QUEST_MOVIE_QUEST_CHOICE:
            camera.posQuatInterval(1, (5, 9, self.getHeight()), (155, -2, 0), other=self, blendType='easeInOut', name='npcCamTrack').start()
            base.localAvatar.lerpCameraFov(70, 1)
        else:
            camera.posQuatInterval(1, (-5, 9, self.getHeight()), (-150, -2, 0), other=self, blendType='easeInOut', name='npcCamTrack').start()


@NPCToonClass(npcType=NPCToonEnum.GHASTLY)
class DistributedNPCGhastly(DistributedNPCToon):

    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)
        self.npcType = "Phantom"

    def initToonState(self):
        self.initPos()

    def initPos(self):
        self.setPos(-157, -22.63, 6.192)
        self.setH(-122.63)
        # self.setGlasses(14, 0, 0)
        # self.setHat(93, 29, 0)
        # self.setShoes(2, 72, 0)
        # self.setCheesyEffect(9)


@NPCToonClass(npcType=NPCToonEnum.HALLOWEEN_PASS)
class DistributedNPCHalloweenPass(DistributedNPCToon):
    traderPos = {
        # npcId: (pos), H
        7052: ((73.694, -163.861, 3.025), 18),  # ttc
        7054: ((-106.228, 82.009, 3.281), -151),  # bb
        7056: ((122.516, -60.867, 14.629), 0),  # yott
        7058: ((2.746, 282.923, 14.027), 0),  # dg
        7060: ((105, -30.328, -10), 120),  # mm
        7062: ((-161.2, -52.8, 6.192), -64),  # tb
        7064: ((-77.405, -46.647, 4.083), 122),  # aa
        7066: ((-70, -12, 1.574), 90),  # ddl
    }

    # Constant codes to use for decrypting chat phrases upon certain interactions
    START_INTERACT_CODE = 1
    EXIT_INTERACT_CODE = 2

    # Which types of phrases do we ignore server side?
    CLIENT_SIDE_CONTEXTS = (
        START_INTERACT_CODE,
        EXIT_INTERACT_CODE
    )

    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)
        self.npcType = "Batcoin Trader"
        self.storeCooldown = CooldownManager(2)
        self.claimCooldown = CooldownManager(8)
        self.storeAssets = loader.loadModel('phase_13/models/events/halloween/battlepass_gui') # Preloading here
        self.hasItemsToClaim = False

    def initToonState(self):
        self.initPos()

    def initPos(self):
        self.setPos(*self.traderPos[self.npc_id][0])
        self.setH(self.traderPos[self.npc_id][1])

    def handleCollisionSphereEnter(self, collEntry):
        if not self.storeCooldown.check(base.localAvatar.doId).outcome:
            return

        self.sendUpdate('checkForRewards', [])

        # Freeze the toon and make them look at us
        base.cr.playGame.getPlace().setState('Stopped')
        self.lookAt(base.localAvatar)

        TRANSITION_LENGTH = 1.0
        # Do a pretty camera pan into opening the GUI
        camera.posQuatInterval(TRANSITION_LENGTH, Vec3(-5, 9, self.getHeight() - 0.5), Vec3(-150, -2, 0), other=self,
                               blendType='easeOut', name=self.uniqueName('lerpCamera')).start()

        taskMgr.doMethodLater(TRANSITION_LENGTH, self.__popupStoreGUI, self.uniqueName('__popupStoreGUI'))

        # Tell server we interacted with a ctx code of 1
        self.sendUpdate('toonInteracted', [self.START_INTERACT_CODE])

    def __popupStoreGUI(self, _=None):
        self.storeGui = HalloweenPass(self)
        taskMgr.doMethodLater(300, self.closePass, 'PassClose')

    def setHasItemsToClaim(self, claimItems):
        if claimItems:
            self.hasItemsToClaim = True
        else:
            self.hasItemsToClaim = False

    def claimItems(self):
        if not self.claimCooldown.check(base.localAvatar.doId).outcome:
            return
        self.sendUpdate('checkForPrizes', [])
        self.sendUpdate('checkForRewards', [])

    def closePass(self, task=None):
        self.storeGui.handleClose()

    def runCleanup(self):
        del self.storeGui
        taskMgr.remove('PassClose')
        base.cr.playGame.getPlace().setState('Walk')
        self.sendUpdate('toonInteracted', [self.EXIT_INTERACT_CODE])

    # Called from AI, given avId that triggered this interaction, in which context, and which phrase
    def handleInteraction(self, avId, ctxCode, phraseId):

        # For this NPC, we ignore certain contexts if the associated avId isn't us,
        # Remove this check if you want server side npc hex again
        if ctxCode in self.CLIENT_SIDE_CONTEXTS and avId != base.localAvatar.doId:
            return

        # Get av associated with interaction, if av is not real don't do anything
        av = base.cr.doId2do.get(avId)
        if not av:
            return

        # Get phrases based on context
        phraseChoices = TTLocalizer.halloweenPassEnterExitResponses[ctxCode]
        # Get which phrase needed
        phrase = phraseChoices[phraseId]

        # Replace _avId_ if needed
        phrase = phrase.replace('_avName_', av.getName())

        # Say it
        self.setChatAbsolute(phrase, CFSpeech | CFTimeout)


@NPCToonClass(npcType=NPCToonEnum.HQ)
class DistributedNPCHQOfficer(DistributedNPCToon):

    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)

        self.npcType = 'HQ Officer'

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        DistributedNPCToon.announceGenerate(self)
        return

        if base.cr.playGame.hood.hoodId == 1000:
            if self.posIndex in [0, 3]:
                self.setHat(16, 0, 0)
            else:
                self.setHat(48, 0, 0)
            self.setGlasses(20, 0, 0)
        elif base.cr.playGame.hood.hoodId == 4000:
            self.setHat(29, 0, 0)
            if self.posIndex == 3:
                self.setBackpack(22, 0, 0)
        elif base.cr.playGame.hood.hoodId == 7000:
            if self.posIndex == 0:
                self.setHat(39, 23, 0)
            elif self.posIndex == 1:
                self.setHat(39, 24, 0)
            elif self.posIndex == 2:
                self.setHat(39, 25, 0)


@NPCToonClass(npcType=NPCToonEnum.HQ_INTERN)
class DistributedNPCHQIntern(DistributedNPCToon):

    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)

        self.npcType = 'HQ Intern'


@NPCToonClass(npcType=NPCToonEnum.HQRANGER)
class DistributedNPCHQRanger(DistributedNPCToon):

    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)

        self.npcType = 'Resistance Ranger'

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        DistributedNPCToon.announceGenerate(self)
        self.setOverheadIcon('fist')


@NPCToonClass(npcType=NPCToonEnum.KARTCLERK)
class DistributedNPCKartClerk(DistributedNPCToonBase):

    def __init__(self, cr):
        DistributedNPCToonBase.__init__(self, cr)

        self.isLocalToon = 0
        self.av = None
        self.button = None
        self.kartShopGui = None
        self.npcType = 'Kart Clerk'

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('popupKartShopGUI'))
        taskMgr.remove(self.uniqueName('lerpCamera'))
        if self.kartShopGui:
            self.kartShopGui.destroy()
            self.kartShopGui = None
        self.av = None

        DistributedNPCToonBase.disable(self)

    def getCollSphereRadius(self):
        return 2.25

    def handleCollisionSphereEnter(self, collEntry):
        base.cr.playGame.getPlace().request('Purchase')
        self.sendUpdate('avatarEnter', [])

    def __handleUnexpectedExit(self):
        self.notify.warning('unexpected exit')
        self.av = None

    def resetKartShopClerk(self):
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('popupKartShopGUI'))
        taskMgr.remove(self.uniqueName('lerpCamera'))
        if self.kartShopGui:
            self.kartShopGui.destroy()
            self.kartShopGui = None
        self.show()
        self.startLookAround()
        self.detectAvatars()
        self.clearMat()
        if self.isLocalToon:
            self.showNametag2d()
            self.freeAvatar()
        return Task.done

    def ignoreEventDict(self):
        for event in KartShopGlobals.EVENTDICT:
            self.ignore(event)

    def setMovie(self, mode, npcId, avId, extraArgs, timestamp):
        timeStamp = ClockDelta.globalClockDelta.localElapsedTime(timestamp)
        self.remain = CLERK_COUNTDOWN_TIME - timeStamp
        self.npcId = npcId
        self.isLocalToon = avId == base.localAvatar.doId
        if mode == SELL_MOVIE_CLEAR:
            return
        if mode == SELL_MOVIE_TIMEOUT:
            taskMgr.remove(self.uniqueName('lerpCamera'))
            if self.isLocalToon:
                self.ignoreEventDict()
                if self.kartShopGui:
                    self.kartShopGui.destroy()
                    self.kartShopGui = None
            self.setChatAbsolute(TTLocalizer.ClerkTimeout, CFSpeech | CFTimeout)
            self.resetKartShopClerk()
        elif mode == SELL_MOVIE_START:
            self.av = base.cr.doId2do.get(avId)
            if self.av is None:
                self.notify.warning('Avatar %d not found in doId' % avId)
                return
            else:
                self.accept(self.av.uniqueName('disable'), self.__handleUnexpectedExit)
            self.setupAvatars(self.av)
            if self.isLocalToon:
                self.hideNametag2d()
                camera.wrtReparentTo(render)
                quat = Quat()
                quat.setHpr((-150, -2, 0))
                camera.posQuatInterval(1, Point3(-5, 9, base.localAvatar.getHeight() - 0.5), quat, other=self, blendType='easeOut').start()
                taskMgr.doMethodLater(1.0, self.popupKartShopGUI, self.uniqueName('popupKartShopGUI'))
        elif mode == SELL_MOVIE_COMPLETE:
            self.setChatAbsolute(TTLocalizer.ClerkGoodbye, CFSpeech | CFTimeout)
            self.resetKartShopClerk()

    def __handleBuyKart(self, kartID):
        self.sendUpdate('buyKart', [kartID])

    def __handleBuyAccessory(self, accID):
        self.sendUpdate('buyAccessory', [accID])

    def __handleGuiDone(self, bTimedOut = False):
        self.ignoreAll()
        if hasattr(self, 'kartShopGui') and self.kartShopGui is not None:
            self.kartShopGui.destroy()
            self.kartShopGui = None
        if not bTimedOut:
            self.sendUpdate('transactionDone')

    def popupKartShopGUI(self, task):
        self.setChatAbsolute('', CFSpeech)
        self.accept(KartShopGlobals.EVENTDICT['buyAccessory'], self.__handleBuyAccessory)
        self.accept(KartShopGlobals.EVENTDICT['buyKart'], self.__handleBuyKart)
        self.acceptOnce(KartShopGlobals.EVENTDICT['guiDone'], self.__handleGuiDone)
        self.kartShopGui = KartShopGuiMgr(KartShopGlobals.EVENTDICT)


class DistributedNPCBumpy(DistributedNPCToon):

    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)
        self.npcType = "Lawyer Toon"
        self.boss = None
        self.movementMovie = None
        self.adviceMovie = None
        self.buttons = []

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        DistributedNPCToon.announceGenerate(self)
        self.request('Neutral')

    def initPos(self):
        pass # thanks bizzy :pensive:

    def delete(self):
        del self.npcType
        del self.boss
        self.interruptMove()
        del self.movementMovie
        self.interruptAdvice()
        del self.adviceMovie
        DistributedNPCToon.delete(self)

    def generateToon(self):
        self.generateToonLegs()
        self.generateToonHead()
        self.generateToonTorso()
        self.generateToonColor()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        self.rightHands = []
        self.leftHands = []
        self.headParts = []
        self.hipsParts = []
        self.torsoParts = []
        self.legsParts = []
        self.__bookActors = []
        self.__holeActors = []
        self.setupToonNodes()
        self.setShaderAuto()

    def handleCollisionSphereEnter(self, collEntry):
        pass

    def detectAvatars(self):
        pass

    def setBossCogId(self, bossCogId):
        self.bossCogId = bossCogId
        self.boss = base.cr.doId2do[bossCogId]

    def interruptMove(self):
        if self.movementMovie and self.movementMovie.isPlaying():
            self.movementMovie.pause()
        self.movementMovie = None
        if self.buttons:
            MovieUtil.removeProps(self.buttons)
        self.buttons = []

    def interruptAdvice(self):
        if self.adviceMovie and self.adviceMovie.isPlaying():
            self.adviceMovie.pause()
        self.adviceMovie = None
        self.clearChat()

    def doTravelMove(self, travelTime, x, y):
        self.interruptMove()
        time = float(travelTime)
        toPos = Point3(x, y, -71.601)
        self.movementMovie = Sequence(
            Func(self.headsUp, toPos),
            Func(self.request, "Run"),
            Func(self.stashBodyCollisions),     # stash while moving
            self.posInterval(time, toPos),
            Func(self.unstashBodyCollisions),   # unstash when done moving
            Func(self.request, "Neutral")
        )
        self.movementMovie.start()

    def doTrapMove(self, trapIndex, trapStatus):
        self.interruptMove()
        button = BattleProps.globalPropPool.getProp('trap-button')
        self.buttons = [button]
        hands = self.getLeftHands()
        buttonSound = BattleSounds.globalBattleSoundCache.getSound('AA_drop_trigger_box.ogg')
        if trapIndex != 0:
            propSound = BattleSounds.globalBattleSoundCache.getSound("TL_quicksand.ogg")
        else:
            propSound = BattleSounds.globalBattleSoundCache.getSound("TL_trap_door.ogg")

        trapObj = self.boss.traps[trapIndex]

        soundTrack = Sequence(
            Wait(2.3),
            SoundInterval(buttonSound, duration=0.67, node=trapObj.trap),
            Wait(0.3),
            SoundInterval(propSound, duration=0.5, node=trapObj.trap)
        )
        # always ensure body collisions aren't stashed b4 doing trap things
        trapSequence = Sequence(Func(self.unstashBodyCollisions), Func(self.lookAt, trapObj.trap))
        if trapStatus == 0:
            trapSequence.append(
                Parallel(
                    Sequence(
                        Func(MovieUtil.showProps, self.buttons, hands),
                        Parallel(
                            ActorInterval(button, 'trap-button'),
                            ActorInterval(self, 'pushbutton'),
                        ),
                        Func(MovieUtil.removeProps, self.buttons)
                    ),
                    soundTrack
                )
            )
        else:
            trapSequence.append(
                Parallel(
                    Func(self.request, "Thinking"), # Placeholder animation
                    Wait(10)
                )
            )
        trapSequence.append(Func(self.request, "Neutral"))
        self.movementMovie = trapSequence
        self.movementMovie.start()

    def doIdleMove(self, time, x, y, h):
        self.interruptMove()
        time = float(time)
        toPos = Point3(x, y, -71.601)
        toHpr = VBase3(h, 0, 0)
        self.movementMovie = Sequence(
            Func(self.headsUp, toPos),
            Func(self.request, "Run"),
            Func(self.stashBodyCollisions),     # stash when moving to idle
            self.posInterval(time, toPos),
            Func(self.unstashBodyCollisions),   # stash when done moving to idle
            Func(self.setHpr, toHpr),
            Func(self.request, "Neutral")
        )
        self.movementMovie.start()

    def sayAdvice(self, helpIndex):
        self.interruptAdvice()
        advice = TTLocalizer.LawbotBossBumpyAdvice[helpIndex]
        if advice:
            advice = advice % {'primary': base.PRIMARY_KEY.upper(), 'secondary': base.SECONDARY_KEY.upper()}
            adviceSequence = Sequence(Func(self.setChatAbsolute, advice, CFSpeech | CFTimeout))
        else:
            adviceSequence = Sequence(Func(self.clearChat))
        self.adviceMovie = adviceSequence
        self.adviceMovie.start()


class DistributedNPCLauren(DistributedNPCBumpy):

    def sayAdvice(self):
        self.adviceMovie = Sequence(Func(self.setChatAbsolute, TTLocalizer.LawbotBossLaurenAdvice, CFSpeech | CFTimeout))
        self.adviceMovie.start()


@NPCToonClass(npcType=NPCToonEnum.PETCLERK)
class DistributedNPCPetclerk(DistributedNPCToonBase):

    def __init__(self, cr):
        super().__init__(cr)
        self.isLocalToon = 0
        self.av = None
        self.button = None
        self.fishGui = None
        self.npcType = 'Pet Clerk'
        self.fishGuiDoneEvent = 'fishGuiDone'

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('popupFishGUI'))
        taskMgr.remove(self.uniqueName('lerpCamera'))
        if self.fishGui:
            self.fishGui.destroy()
            self.fishGui = None
        self.av = None

        super().disable()

    def generate(self):
        """
        Called when the DistributedObject is reintroduced to the world, either for the first time or from the cache.
        """
        super().generate()
        self.fishGuiDoneEvent = 'fishGuiDone'

    def getCollSphereRadius(self):
        return 4.0

    def allowedToEnter(self):
        return True

    def handleCollisionSphereEnter(self, collEntry):
        base.cr.playGame.getPlace().request('Purchase')
        self.sendUpdate('avatarEnter', [])

    def __handleUnexpectedExit(self):
        self.notify.warning('unexpected exit')
        self.av = None

    def resetPetshopClerk(self):
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('popupFishGUI'))
        taskMgr.remove(self.uniqueName('lerpCamera'))
        if self.fishGui:
            self.fishGui.destroy()
            self.fishGui = None
        self.show()
        self.startLookAround()
        self.detectAvatars()
        self.clearMat()
        if self.isLocalToon:
            self.showNametag2d()
            self.freeAvatar()
        return Task.done

    def setMovie(self, mode, npcId, avId, extraArgs, timestamp):
        timeStamp = ClockDelta.globalClockDelta.localElapsedTime(timestamp)
        self.remain = CLERK_COUNTDOWN_TIME - timeStamp
        self.npcId = npcId
        self.isLocalToon = avId == base.localAvatar.doId
        if mode == SELL_MOVIE_CLEAR:
            return
        if mode == SELL_MOVIE_TIMEOUT:
            taskMgr.remove(self.uniqueName('lerpCamera'))
            if self.isLocalToon:
                self.ignore(self.fishGuiDoneEvent)
                if self.fishGui:
                    self.fishGui.destroy()
                    self.fishGui = None
            self.setChatAbsolute(TTLocalizer.ClerkTimeout, CFSpeech | CFTimeout)
            self.resetPetshopClerk()
        elif mode == SELL_MOVIE_START:
            self.av = base.cr.doId2do.get(avId)
            if self.av is None:
                self.notify.warning('Avatar %d not found in doId' % avId)
                return
            else:
                self.accept(self.av.uniqueName('disable'), self.__handleUnexpectedExit)
            self.setupAvatars(self.av)
            if self.isLocalToon:
                self.hideNametag2d()
                camera.wrtReparentTo(render)
                seq = Sequence((camera.posQuatInterval(1, Vec3(-5, 9, self.getHeight() - 0.5), Vec3(-150, -2, 0), other=self, blendType='easeOut', name=self.uniqueName('lerpCamera'))))
                seq.start()
                taskMgr.doMethodLater(1.0, self.popupFishGUI, self.uniqueName('popupFishGUI'))
        elif mode == SELL_MOVIE_COMPLETE:
            self.setChatAbsolute(TTLocalizer.PetClerkThanksFish, CFSpeech | CFTimeout)
            self.resetPetshopClerk()
        elif mode == SELL_MOVIE_TROPHY:
            self.av = base.cr.doId2do.get(avId)
            if self.av is None:
                self.notify.warning('Avatar %d not found in doId' % avId)
                return
            else:
                numFish, totalNumFish = extraArgs
                self.setChatAbsolute(TTLocalizer.FishingClerkTrophy % (numFish, totalNumFish), CFSpeech | CFTimeout)
            self.resetPetshopClerk()
        elif mode == SELL_MOVIE_NOFISH:
            self.setChatAbsolute(TTLocalizer.FishingClerkNoFish, CFSpeech | CFTimeout)
            self.resetPetshopClerk()

    def __handleSaleDone(self, sell):
        self.ignore(self.fishGuiDoneEvent)
        self.sendUpdate('completeSale', [sell])
        if self.fishGui:
            self.fishGui.destroy()
            self.fishGui = None

    def popupFishGUI(self, task):
        self.setChatAbsolute('', CFSpeech)
        self.acceptOnce(self.fishGuiDoneEvent, self.__handleSaleDone)
        self.fishGui = FishSellGUI(self.fishGuiDoneEvent)


@NPCToonClass(npcType=NPCToonEnum.PLANT)
class DistributedNPCPlant(DistributedEmptyNPC):
    def __init__(self, cr):
        DistributedEmptyNPC.__init__(self, cr)

        self.npcType = ''
        self.dialogArrayDefault = [base.loader.loadSfx('phase_11/audio/dial/cc_s_dlg_plant_rustle.ogg')] * 9
        self.dialogArrayChime = [base.loader.loadSfx('phase_11/audio/dial/cc_s_dlg_plant_rustle_chimes.ogg')] * 9
        self.dialogArray = self.dialogArrayDefault
        self.chatNpcPresetType = ChatNpcPreset.Plant

        self.pendingResponse = False
        self.plantData = None

    def initPos(self):
        if self.plantData:
            return

        self.plantData = next(filter(lambda x: x[1] == self.npc_id, ToontownGlobals.PlantData))

        self.setPos(*self.plantData[2])
        self.setName(TTLocalizer.PlantId2Name.get(self.npc_id, 'UNKNOWN PLANT'))

        # These plants are taller if in a cog area, for scaling to cog suits.
        if self.plantData[3] == ToontownGlobals.LawbotLounge:
            self.setHeight(4.7)
        else:
            self.setHeight(3)

        self.setNameVisible(False)
        self.hideNametag2d()
        self.hideNametag3d() # disabled for now to fix crash
        self.nametag.getNametag2d().setContents(Nametag.CSpeech)
        self.nametag.getNametag3d().setContents(Nametag.CSpeech)

    def getDialogueArray(self):
        return self.dialogArray

    def handleCollisionSphereEnter(self, collEntry):
        if self.pendingResponse:
            return

        self.pendingResponse = True
        self.sendUpdate('requestCheck', [self.plantData[0]])

    def requestCheckResponse(self, response):
        taskMgr.doMethodLater(3.0, self.endCooldown, self.uniqueName('requestCooldown'))
        if response == 0:
            # "error" out of order
            self.dialogArray = self.dialogArrayDefault
            self.setChatAbsolute(TTLocalizer.PlantDialogDefault, CFSpeech | CFTimeout)
        elif response == 1:
            # in order, progress time!
            self.dialogArray = self.dialogArrayChime
            self.setChatAbsolute(TTLocalizer.PlantDialogChime, CFSpeech | CFTimeout)

    def requestCheckChatResponse(self, response):
        taskMgr.doMethodLater(0.5, self.endCooldown, self.uniqueName('requestCooldown'))
        self.dialogArray = self.dialogArrayChime
        self.setChatAbsolute(response, CFSpeech | CFTimeout)

    def endCooldown(self, _):
        self.pendingResponse = False


@NPCToonClass(npcType=NPCToonEnum.RED_NOSE)
class DistributedNPCRedNose(DistributedNPCToon):

    def initPos(self):
        self.setAnimalEffect(1)


@NPCToonClass(npcType=NPCToonEnum.ITEM_SELLER)
class DistributedNPCItemSeller(DistributedNPCToon):
    # Constant codes to use for decrypting chat phrases upon certain interactions
    START_INTERACT_CODE = 1
    EXIT_INTERACT_CODE = 2

    CLIENT_SIDE_CONTEXTS = (
        START_INTERACT_CODE,
        EXIT_INTERACT_CODE
    )

    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)
        self.storeGui = None
        self.interactCooldown = CooldownManager(2)
        self.responseCooldown = CooldownManager(3)

    def hasProgressableQuestAvailable(self):
        # Try to do a relatively janky check to see if there are any progressable quests available
        # before we let the local av into the shop
        for questRef in base.localAvatar.getQuestReferences():
            for index, questObjective in enumerate(QuestLine.dereferenceQuestReference(questRef, quester=base.localAvatar).getQuestObjectives()):
                if type(questObjective) in (VisitObjective, VisitHQOfficerObjective, DeliverObjective, ObtainObjective,
                                            DeliverGagObjective, DeliverJellybeanObjective) and self.npc_id in questObjective.getResolvableNpcIds():
                    return True
                elif questObjective.npcReturnable and questObjective.isComplete(questRef, index, base.localAvatar) and self.npc_id in questObjective.getResolvableNpcIds():
                    return True

        return False

    def handleCollisionSphereEnter(self, collEntry):
        if self.hasProgressableQuestAvailable():
            super().handleCollisionSphereEnter(collEntry)
            return

        if not self.interactCooldown.check(base.localAvatar.doId).outcome:
            return

        # Freeze the toon and make them look at us
        base.cr.playGame.getPlace().setState('Stopped')
        self.lookAt(base.localAvatar)

        TRANSITION_LENGTH = 1.0
        # Do a pretty camera pan into opening the GUI
        camera.posQuatInterval(TRANSITION_LENGTH, Vec3(-5, 9, self.getHeight() - 0.5), Vec3(-150, -2, 0), other=self,
                               blendType='easeOut', name=self.uniqueName('lerpCamera')).start()

        taskMgr.doMethodLater(TRANSITION_LENGTH, self.__popupStoreGUI, self.uniqueName('__popupStoreGUI'))

        # Tell server we interacted with a ctx code of 1
        self.sendUpdate('toonInteracted', [self.START_INTERACT_CODE])

    def __popupStoreGUI(self, _=None):
        self.storeGui = NPCToonShopGUI(aspect2d, npc=self)

    def doExit(self):
        # Tell the server we exited
        self.sendUpdate('toonInteracted', [self.EXIT_INTERACT_CODE])

    def handleBuyResponse(self, code):
        if self.storeGui:
            self.setChatAbsolute(TTLocalizer.NPCStoreResponses[code], CFSpeech | CFTimeout)
            self.cr.chatManager.sendSystemMessageLocally(TTLocalizer.NPCStoreResponses[code], senderName=self.getName())
            self.storeGui.updatePage()

    # Called from AI, given avId that triggered this interaction, in which context, and which phrase
    def handleInteraction(self, ctxCode, phraseId):
        # Get phrases based on context
        phraseChoices = TTLocalizer.NPCStoreEnterExitResponses[ctxCode]
        # Get which phrase needed
        phrase = phraseChoices[phraseId]

        # Replace _avId_ if needed
        phrase = phrase.replace('_avName_', base.localAvatar.getName())

        # Say it
        self.setChatAbsolute(phrase, CFSpeech | CFTimeout)


@NPCToonClass(npcType=NPCToonEnum.SECRETARY)
class DistributedNPCSecretary(DistributedNPCToon):
    chatNpcPresetType = ChatNpcPreset.Cog

    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)
        self.npcType = ''
        self.setupComplete = False
        self.exclaim = None
        self.exclaimLoop = None
        self.questWarningBox = None

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        if self.questWarningBox:
            self.questWarningBox.cleanup()
            self.questWarningBox = None

        DistributedNPCToon.disable(self)
        taskMgr.remove('attemptQuestWarning')

    def delete(self):
        DistributedNPCToon.delete(self)
        if self.exclaimLoop is not None:
            self.exclaimLoop.finish()
            self.exclaim = None
            del self.exclaim

    def initPos(self):
        # So none of them show up as executives
        self.cogReviveLevels = [-1, -1, -1, -1, -1]
        if self.zoneId == ToontownGlobals.LawbotLobby:  # Judy
            # Stuff that only needs to be run once goes under here
            if not self.setupComplete:
                self.putOnSuit('judy')
                self.suit.loop('sit')
                self.setPlayerType(NametagGroup.CCSuit)
                self.setName(SuitBattleGlobals.SuitAttributes[self.suit.style.name]['name'])
                nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': self._name,
                                                                'dept': TTLocalizer.Lawbot,
                                                                'level': '20.mgr'}
                self.setDisplayName(nameInfo)
                self.suit.shadowJoint.hide()

                self.chair = loader.loadModel('phase_11/models/lawbotHQ/LawbotBossRoomChair')
                self.chair.reparentTo(self)
                self.chair.setScale(0.5)
                self.chair.setColorScale(1, 1, 1, 1)

                questWarningBools = self.isQuestAvailable()
                if questWarningBools[0]:
                    self.doQuestWarning(2, questWarningBools[1])
                    self.exclaim = self.createQuestIndicator()
                    self.exclaim.setPos(-0.4, -2.2, 9.5)
                    self.exclaim.setScale(2)
                    self.exclaimLoop = self.makeIndicatorLoopMovie()
                    self.exclaimLoop.loop()
            self.setPos(-56, 79.5, 0.6)
            self.setH(-90)
            self.nametag3d.setPos(-0.365, -2.5, self.height + 2.5)
            self.chair.setPos(-0.4, -2.2, -0.4)
            if self.exclaim is not None and self.isQuestAvailable()[0]:
                self.exclaim.show()
        self.setupComplete = True

    # Overriding this because the camera was too low by default.
    def setupCamera(self, mode):
        if self.exclaim is not None:
            self.exclaim.hide()
        camera.wrtReparentTo(render)
        if not self.previousCameraPosHpr:
            self.previousCameraPosHpr = [camera.getPos(base.localAvatar), camera.getHpr(base.localAvatar)]
        if mode == QUEST_MOVIE_QUEST_CHOICE:
            camera.posQuatInterval(1, (5, 9, self.getHeight() + 1.5), (155, -2, 0), other=self, blendType='easeInOut', name='npcCamTrack').start()
            base.localAvatar.lerpCameraFov(70, 1)
        else:
            camera.posQuatInterval(1, (-5, 9, self.getHeight() + 1.5), (-150, -2, 0), other=self, blendType='easeInOut', name='npcCamTrack').start()

    def getCollSphereRadius(self):
        return 10.0

    def initToonState(self):
        self.setAnimState('Neutral', 0.9, None, None)
        npcOrigin = base.cr.playGame.hood.loader.geom
        if not npcOrigin.isEmpty():
            self.reparentTo(npcOrigin)
            self.initPos()

    def getDialogueSfx(self, type, length):
        # Override this to make Judy use the correct dialogue indices.
        return DistributedAvatar.getDialogueSfx(self, type, length)

    def setChatAbsolute(self, chatString, chatFlags, dialogue=None, interrupt=1, wantBalloonAnim=True, wantSound=True, logMessage=None):
        # Override this to give Judy the gray cog text in the Chat log.
        DistributedAvatar.setChatAbsolute(self, chatString, chatFlags, dialogue, interrupt, wantBalloonAnim, wantSound, logMessage)

        if self.suit.specialHead:
            type = self.suit.getDialogTypeName(chatString)
            animation = type if type in self.suit.specialHead.getAnimNames() else 'talk'
            seq = Sequence(ActorInterval(self.suit.specialHead, animation), Func(self.suit.specialHead.loopNeutral))
            seq.start()

        if getattr(base, "cr", None) and self.isNPC:
            if logMessage is None:
                for message in chatString.split("\x07"):
                    base.cr.chatManager.receiveChatMessage(ChatChannel.NPC, self.chatNpcPresetType, ChatContentType.Text, message, self.doId, self.getName())
            elif logMessage:
                base.cr.chatManager.receiveChatMessage(ChatChannel.NPC, self.chatNpcPresetType, ChatContentType.Text, logMessage, self.doId, self.getName())

    def isQuestAvailable(self):
        """
        :return: (bool, bool) First is if quest is available. Second is if it is the first quest from the secretary.
        """
        # Quests which the npc offers.
        validQuests = []
        # Quests which the npc offers, but the quester doesn't own or hasn't completed.
        availableQuests = []
        for chainId, chain in DirectiveQuestLine.getValidQuestChains(base.localAvatar):
            chain: QuestChain

            # Get the first objective of the quest chain.
            firstObjective = chain.getInitialObjective()

            # Get the npcId from this objective.
            fromNpc = firstObjective.getFromNpcId()

            # The npcId matches the npcId of the first npc of the chain.
            if self.npc_id == fromNpc:
                questId = QuestId(QuestSource.Directive, chainId, chain.getStartObjectiveId())
                validQuests.append(questId)
                # The chainId does not exist in the quester's quest history.
                if not base.localAvatar.hasCompletedQuest(QuestSource.Directive, chainId):
                    # The questId does not exist in any of their quest references.
                    if not base.localAvatar.hasQuest(questId):
                        availableQuests.append(questId)
        return bool(availableQuests), len(validQuests) == len(availableQuests)

    def doQuestWarning(self, dept, firstQuestDialog=False):
        # All checks passed, display the dialog.
        if firstQuestDialog:
            dialog = TTLocalizer.SecretaryQuestAvailableWarning[dept][0]
        else:
            dialog = TTLocalizer.SecretaryQuestAvailableWarning[dept][1]
        taskMgr.doMethodLater(0.65, self.attemptQuestWarning, 'attemptQuestWarning', extraArgs=[dialog], priority=0)

    def attemptQuestWarning(self, dialog):
        if base.cr.playGame.getPlace() is not None and base.cr.playGame.getPlace().getState() == 'Walk':
            self.questWarningBox = TTDialog.TTGlobalDialog(dialog, doneEvent='secretaryQuestAck', style=TTDialog.Acknowledge)
            self.questWarningBox.show()
            base.cr.playGame.getPlace().setState('Stopped')
            self.accept('secretaryQuestAck', self.__handleSecretaryQuestAck)
        else:
            taskMgr.doMethodLater(0.05, self.attemptQuestWarning, 'attemptQuestWarning', extraArgs=[dialog], priority=0)

    def __handleSecretaryQuestAck(self):
        self.questWarningBox.cleanup()
        self.questWarningBox = None
        base.cr.playGame.getPlace().setState('Walk')

    def createQuestIndicator(self):
        tipsGui = loader.loadModel('phase_3/models/gui/ttcc_tips')
        exclaim = tipsGui.find('**/tipExclaim')
        tipsGui.removeNode()

        exclaim.setBillboardPointEye()
        exclaim.reparentTo(self)
        exclaim.setPos(0, 0, self.height + 2)
        return exclaim

    def makeIndicatorLoopMovie(self):
        if self.exclaim is not None:
            startingZ = self.exclaim.getZ()
            exclaimLoop = Sequence(
                LerpFunc(self.exclaim.setZ, 0.5, fromData=startingZ, toData=startingZ - 0.25, blendType='easeOut'),
                LerpFunc(self.exclaim.setZ, 1.0, fromData=startingZ - 0.25, toData=startingZ + 0.25, blendType='easeInOut'),
                LerpFunc(self.exclaim.setZ, 0.5, fromData=startingZ + 0.25, toData=startingZ, blendType='easeIn'),
            )
            return exclaimLoop


@NPCToonClass(npcType=NPCToonEnum.SNOWMAN)
class DistributedNPCSnowman(DistributedNPCToon):
    def __init__(self, cr):
        super().__init__(cr)
        self.npcType = "Man of Snow"
        self.snowman = None
        self.dialogArray = []
        snowmanDialogueFiles = ('AV_snowman_short', 'AV_snowman_med', 'AV_snowman_long', 'AV_snowman_question',
                                'AV_snowman_exclaim', 'AV_snowman_howl', 'AV_snowman_med', 'AV_snowman_long',
                                'AV_snowman_indifferent')

        for file in snowmanDialogueFiles:
            self.dialogArray.append(base.loader.loadSfx('phase_13/audio/dial/' + file + '.ogg'))
    
    def announceGenerate(self):
        super().announceGenerate()
        self.accept("localPieSplat", self.d_snowballHit)
        taskMgr.doMethodLater(1, self.__snowmanRandomObserve, 'BR-snowmanAnim')

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        super().disable()
        self.ignoreAll()
        if self.snowman:
            self.snowman.cleanup()
            self.snowman = None
        taskMgr.remove('BR-snowmanAnim')

    def getDialogueArray(self):
        for dialog in self.dialogArray:
            dialog.setPlayRate(1 / self.getScale().x)
        return self.dialogArray

    def __snowmanRandomObserve(self, _):
        CHANCE = 5
        check = random.randint(1, CHANCE)
        nextTaskTime = random.random() * 5.0 + 10.0

        if self.snowman:
            if check == CHANCE:
                self.snowman.snowmanFSM.request('Observe')

            taskMgr.doMethodLater(nextTaskTime, self.__snowmanRandomObserve, 'BR-snowmanAnim')
            return Task.done

    def setMovie(self, mode, npcId, avId, quests, timestamp, questId):
        ret = super().setMovie(mode, npcId, avId, quests, timestamp, questId)

        if not self.snowman:
            return ret

        if mode in [QUEST_MOVIE_QUEST_CHOICE]:
            self.snowman.snowmanFSM.request('Approach')
        elif mode in [QUEST_MOVIE_REJECT, QUEST_MOVIE_ASSIGN]:
            self.snowman.snowmanFSM.request('Talk')

        return ret

    def initPos(self):
        if self.zoneId == ToontownGlobals.TheBrrrgh and not self.snowman:
            self.setPos(18.19, 0.16, 6.28)
            self.setHeight(5)
            self.getPart('head').hide()
            self.getPart('torso').hide()
            self.getPart('legs').hide()
            self.setH(-215)
            self.snowman = SnowmanSteve(self.getGeomNode())
            self.snowman.snowmanFSM.request('Neutral')

    def snowballScale(self, scaleAmt):
        if self.snowman:
            self.setScale(scaleAmt)
            self.snowman.snowmanBody.setScale(scaleAmt)

    def d_snowballHit(self, pieCode, entry):
        # Ensure that the snowman was the one that got hit.
        collisionParent = None if not entry.getIntoNodePath() else entry.getIntoNodePath().getParent()
        if not collisionParent or collisionParent.getName() != self.name:
            return

        self.sendUpdate('snowballHit', [pieCode])


@NPCToonClass(npcType=NPCToonEnum.TAILOR)
class DistributedNPCTailor(DistributedNPCToonBase):
    # TODO: FIX

    def __init__(self, cr):
        super().__init__(cr)
        self.isLocalToon = 0
        self.clothesGUI = None
        self.av = None
        self.oldStyle = None
        self.browsing = 0
        self.roomAvailable = 0
        self.button = None
        self.beanBank = None
        self.costLabel = None
        self.npcType = 'Clothing Tailor'

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('popupPurchaseGUI'))
        if self.clothesGUI:
            self.clothesGUI.exit()
            self.clothesGUI.unload()
            self.clothesGUI = None
            if self.button is not None:
                self.button.destroy()
                del self.button
            self.cancelButton.destroy()
            del self.cancelButton
            del self.gui
            self.counter.show()
            del self.counter
        self.av = None
        self.oldStyle = None
        DistributedNPCToonBase.disable(self)

    def handleCollisionSphereEnter(self, collEntry):
        base.cr.playGame.getPlace().request('Purchase')
        self.sendUpdate('avatarEnter', [])

    def __handleUnexpectedExit(self):
        self.notify.warning('unexpected exit')
        self.av = None
        self.oldStyle = None

    def resetTailor(self):
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('popupPurchaseGUI'))
        if self.clothesGUI:
            self.clothesGUI.hideButtons()
            self.clothesGUI.exit()
            self.clothesGUI.unload()
            self.clothesGUI = None
        if self.beanBank:
            self.beanBank.removeNode()
            self.beanBank = None
        if self.costLabel:
            self.costLabel.removeNode()
            self.costLabel = None
            if self.button is not None:
                self.button.destroy()
                del self.button
            self.cancelButton.destroy()
            del self.cancelButton
            del self.gui
            self.counter.show()
            del self.counter
            self.show()
        self.startLookAround()
        self.detectAvatars()
        self.clearMat()
        if self.isLocalToon:
            self.freeAvatar()
        return Task.done

    def setMovie(self, mode, npcId, avId, timestamp):
        timeStamp = ClockDelta.globalClockDelta.localElapsedTime(timestamp)
        self.remain = CLERK_COUNTDOWN_TIME - timeStamp
        self.npcId = npcId
        self.isLocalToon = avId == base.localAvatar.doId
        if mode == PURCHASE_MOVIE_CLEAR:
            return
        if mode == PURCHASE_MOVIE_TIMEOUT:
            if self.isLocalToon:
                self.ignore(self.purchaseDoneEvent)
                self.ignore(self.swapEvent)
            if self.clothesGUI:
                self.clothesGUI.resetClothes(self.oldStyle)
                self.__handlePurchaseDone(timeout=1)
            self.setChatAbsolute(TTLocalizer.ClerkTimeout, CFSpeech | CFTimeout)
            self.resetTailor()
        elif mode == PURCHASE_MOVIE_START or mode == PURCHASE_MOVIE_START_BROWSE or mode == PURCHASE_MOVIE_START_NOROOM or mode == PURCHASE_MOVIE_START_BROWSE_JBS:
            if mode == PURCHASE_MOVIE_START:
                self.browsing = 0
                self.roomAvailable = 1
            elif mode == PURCHASE_MOVIE_START_BROWSE or mode == PURCHASE_MOVIE_START_BROWSE_JBS:
                self.browsing = 1
                self.roomAvailable = 1
            elif mode == PURCHASE_MOVIE_START_NOROOM:
                self.browsing = 0
                self.roomAvailable = 0
            self.av = base.cr.doId2do.get(avId)
            if self.av is None:
                self.notify.warning('Avatar %d not found in doId' % avId)
                return
            else:
                self.accept(self.av.uniqueName('disable'), self.__handleUnexpectedExit)
            style = self.av.getStyle()
            self.oldStyle = ToonDNA()
            self.oldStyle.makeFromNetString(style.makeNetString())
            self.setupAvatars(self.av)
            if self.isLocalToon:
                self.cameraWork = camera.posHprInterval(2, Point3(-4.16, 8.25, 2.47), Point3(-152.89, 0, 0), blendType='easeOut', other=base.localAvatar)
                self.cameraWork.start()
            if self.browsing == 0:
                if self.roomAvailable == 0:
                    self.setChatAbsolute(TTLocalizer.TailorClerkNoClosetSpace, CFSpeech | CFTimeout)
                else:
                    self.setChatAbsolute(TTLocalizer.ClerkGreeting, CFSpeech | CFTimeout)
            elif mode == PURCHASE_MOVIE_START_BROWSE_JBS:
                self.setChatAbsolute(TTLocalizer.TailorClerkBrowsingNoBeans, CFSpeech | CFTimeout)
            if self.isLocalToon:
                taskMgr.doMethodLater(3.0, self.popupPurchaseGUI, self.uniqueName('popupPurchaseGUI'))
        elif mode == PURCHASE_MOVIE_COMPLETE:
            self.setChatAbsolute(TTLocalizer.ClerkGoodbye, CFSpeech | CFTimeout)
            self.resetTailor()
        elif mode == PURCHASE_MOVIE_NO_MONEY:
            self.notify.warning('PURCHASE_MOVIE_NO_MONEY should not be called')
            self.resetTailor()
        return

    def popupPurchaseGUI(self, task):
        self.setChatAbsolute('', CFSpeech)
        self.purchaseDoneEvent = 'purchaseDone'
        self.swapEvent = 'swap'
        self.acceptOnce(self.purchaseDoneEvent, self.__handlePurchaseDone)
        self.accept(self.swapEvent, self.__handleSwap)
        self.clothesGUI = TailorClothesGUI(self.purchaseDoneEvent, self.swapEvent, self.npcId)
        self.clothesGUI.load()
        self.clothesGUI.enter(self.av)
        self.clothesGUI.showButtons()
        self.clothesGUI.topLButton['state'] = DGG.DISABLED
        self.clothesGUI.topRButton['state'] = DGG.DISABLED
        self.clothesGUI.bottomLButton['state'] = DGG.DISABLED
        self.clothesGUI.bottomRButton['state'] = DGG.DISABLED

        bean = loader.loadModel('phase_4/models/props/jellybean4.bam')
        bean = bean.find('**/jellybean')
        bean.setColor(hexToPCol('00f5ff'))
        bean.setDepthWrite(1)
        bean.setDepthTest(1)
        bean.setTwoSided(True)

        genBgIconsTexcard = loader.loadModel(f'{GUI_ICON_MODEL_PATH}{GUI_TEXCARD_PREFIX}gen_bg_icons')
        self.beanBank = DirectLabel(
            base.a2dLeftCenter,
            relief=None,
            pos=(-0.190741, 0, 0.261111),
            scale=0.7,
            image=genBgIconsTexcard.find('**/icon_bank_1'),
            text=str(base.localAvatar.getMoney() + base.localAvatar.getBankMoney()),
            text_align=TextNode.ARight,
            text_scale=0.11,
            text_fg=(0.95, 0.95, 0, 1),
            text_shadow=(0, 0, 0, 1),
            text_pos=(0.75, -0.81),
            text_font=ToontownGlobals.getSignFont()
        )
        self.costLabel = DirectLabel(
            base.a2dLeftCenter,
            relief=None,
            pos=(0.0888888, 0, 0.0425926),
            image=bean,
            image_hpr=(90, 0, 0),
            image_scale=0.2,
            text=TTLocalizer.TailorCostBuy % ToontownGlobals.TailorBeanCost,
            text_align=TextNode.ALeft,
            text_pos=(-0.03, 0.04, 0),
            text_scale=0.06,
            text_fg=(0.95, 0.95, 0, 1),
            text_shadow=(0, 0, 0, 1),
            text_font=ToontownGlobals.getSignFont()
        )

        self.gui = loader.loadModel('phase_3/models/gui/create_a_toon_gui')
        if self.browsing == 0:
            self.button = DirectButton(
                relief=None,
                scale=0.7,
                image=(
                    self.gui.find('**/CrtAtoon_Btn1_UP'),
                    self.gui.find('**/CrtAtoon_Btn1_DOWN'),
                    self.gui.find('**/CrtAtoon_Btn1_RLLVR')
                ),
                pos=(-0.15, 0, -0.8),
                command=self.__handleButton,
                text=(
                    '',
                    TTLocalizer.MakeAToonDone,
                    TTLocalizer.MakeAToonDone
                ),
                text_font=ToontownGlobals.getInterfaceFont(),
                text_scale=0.08,
                text_pos=(0, -0.03),
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1)
            )
        else:
            self.button = None
        self.cancelButton = DirectButton(
            relief=None,
            scale=0.7,
            image=(
                self.gui.find('**/CrtAtoon_Btn2_UP'),
                self.gui.find('**/CrtAtoon_Btn2_DOWN'),
                self.gui.find('**/CrtAtoon_Btn2_RLLVR')
            ),
            pos=(0.15, 0, -0.8),
            command=self.__handleCancel,
            text=(
                '',
                TTLocalizer.MakeAToonCancel,
                TTLocalizer.MakeAToonCancel
            ),
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.08,
            text_pos=(0, -0.03),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1)
        )
        camera.setPosHpr(base.localAvatar, -4.16, 8.25, 2.47, -152.89, 0.0, 0.0)
        self.counter = render.find('**/*ounter')
        self.counter.hide()
        self.hide()
        return Task.done

    def __handleButton(self):
        messenger.send('next')

    def __handleCancel(self):
        self.clothesGUI.resetClothes(self.oldStyle)
        messenger.send('last')

    def __handleSwap(self):
        if self.clothesGUI.topStyleChoice != -1:
            self.clothesGUI.topLButton['state'] = DGG.NORMAL
            self.clothesGUI.topRButton['state'] = DGG.NORMAL
        if self.clothesGUI.bottomStyleChoice != -1:
            self.clothesGUI.bottomLButton['state'] = DGG.NORMAL
            self.clothesGUI.bottomRButton['state'] = DGG.NORMAL
        self.d_setDNA(self.av.getStyle().makeNetString(), 0)

    def __handlePurchaseDone(self, timeout = 0):
        """
        This is the callback from the Purchase object
        Cleanup the gui and send the message to the AI
        """
        if self.clothesGUI.doneStatus == 'last' or timeout == 1:
            # The client really does not need to send the DNA here
            # since the server is keeping track of it
            self.d_setDNA(self.oldStyle.makeNetString(), 1)
        else:
            # The client really does not need to send the DNA here
            # since the server is keeping track of it

            # check if we ever changed the shorts or shirt
            # create a bit string that identifies which items
            # have been changed
            # bit 0 = shirts
            # bit 1 = shorts
            # bit 2...unused
            which = 0
            if self.clothesGUI.topChoice != -1:
                which = which | ClosetGlobals.SHIRT
            if self.clothesGUI.topStyleChoice != -1:
                which = which | ClosetGlobals.SHIRT
            if self.clothesGUI.bottomChoice != -1:
                which = which | ClosetGlobals.SHORTS
            if self.clothesGUI.bottomStyleChoice != -1:
                which = which | ClosetGlobals.SHORTS

            # if the closet is full or almost full, confirm that we want to lose the
            # clothes we are wearing
            if self.roomAvailable == 0:
                if self.isLocalToon:
                    self.d_setDNA(self.av.getStyle().makeNetString(), 2, which)
            else:
                self.d_setDNA(self.av.getStyle().makeNetString(), 2, which)

    def d_setDNA(self, dnaString, finished, whichItems = 1 | 2):
        # Report our DNA to the server
        self.sendUpdate('setDNA', [dnaString, finished, whichItems])

    def setCustomerDNA(self, avId, dnaString):
        # The AI doesn't set the DNA on swaps (finished=0) anymore.
        # This is to avoid bugged clothes on AI crashes while browsing.  Now the AI
        # just tells the clients the correct DNA for the current customer
        # and lets the clients set the value directly on the distributed
        # toon. The AI will still do a DNA change on purchase.

        # the av might be gone, so check first
        if avId != base.localAvatar.doId:
            av = base.cr.doId2do.get(avId, None)
            if av:
                if self.av == av:
                    oldTorso = self.av.style.torso
                    self.av.style.makeFromNetString(dnaString)
                    if len(oldTorso) == 2 and len(self.av.style.torso) == 2 and self.av.style.torso[1] != oldTorso[1]:
                        self.av.swapToonTorso(self.av.style.torso, genClothes=0)
                        self.av.loop('neutral', 0)


@NPCToonClass(npcType=NPCToonEnum.SPIRITS)
class DistributedNPCToonsmasSpirits(DistributedNPCToon):

    def __init__(self, cr):
        super().__init__(cr)
        # self.spiritInfo = {npcID: NPC Title}
        self.spiritInfo = {
            18517: "Spirit of the Past",
            18518: "Spirit of the Present",
            18519: "Spirit of the Future",
        }

    def initToonState(self):
        self.initPos()

    def initPos(self):
        # Handle the NPC Tag
        self.npcType = self.spiritInfo.get(self.npc_id, "Spirit of the Unknown")    # doubt this will be an issue, but spawnNPC also has a "hide NPC if id isn't known" check)
        self.setToonTag(self.npc_id, self.npcType)

        # Handle NPC Spawning
        # NOTE: hiding the NPC toon via holiday is now handled with DToonAI check + DToon.announceGenerate()
        self.spawnNPC(self.npc_id)

    def spawnNPC(self, npc):
        if npc == 18517:
            self.setPos(170.5, 6.6, 29.208)
            self.setH(110)
            # self.setHat(116, 0, 0)
            # self.setBackpack(81, 0, 0)
            # self.setCheesyEffect(9)
        elif npc == 18518:
            self.setPos(70.302, -93.298, 20.716)
            self.setH(72.94)
            # self.setHat(117, 0, 0)
            # self.setBackpack(82, 0, 0)
            # self.setCheesyEffect(9)
        elif npc == 18519:
            self.setPos(-216.75, 126.14, 51.147)
            self.setH(96.25)
            # self.setHat(118, 0, 0)
            # self.setBackpack(85, 0, 0)
            # self.setCheesyEffect(9)
        else:
            self.hideNPCToon()


@NPCToonClass(npcType=NPCToonEnum.TRASHCAT)
class DistributedNPCTrashCat(DistributedNPCToon):

    def __init__(self, cr):
        super().__init__(cr)
        self.npcType = "Trash Cat"
        self.can = None

        self.musicPath = 'toontown_central_travis'
        self.mSphere = CollisionTube(0.0, 1.0, 0.0, 0.0, 1.0, 5.0, 13)
        self.mSphere.setTangible(0)
        self.mSphereNode = CollisionNode(f'mSphereNode-TrashCat-{id(self)}')
        self.mSphereNode.addSolid(self.mSphere)
        self.mSphereNodePath = self.attachNewNode(self.mSphereNode)
        self.mSphereNodePath.hide()
        self.mSphereNode.setCollideMask(ToontownGlobals.WallBitmask)
        self.trashMusic = None
        self.playgroundMusic = None

    def announceGenerate(self):
        super().announceGenerate()
        self.trashMusic = base.musicMgr.loadMusic(self.musicPath)
        self.playgroundMusic = base.musicMgr.loadMusic(base.cr.playGame.hood.loader.music)

    def disable(self):
        self.ignoreAll()
        self.mSphereNodePath.removeNode()
        self.mSphereNodePath = None
        super().disable()
        base.musicMgr.stopMusic(self.trashMusic)
        self.trashMusic = None
        self.playgroundMusic = None

    def detectAvatars(self):
        super().detectAvatars()
        self.accept('enter' + self.mSphereNode.getName(), self.startMusic)
        self.accept('exit' + self.mSphereNode.getName(), self.stopMusic)

    def ignoreAvatars(self):
        super().ignoreAvatars()
        self.ignore('enter' + self.mSphereNode.getName())

    def startMusic(self, collEntry):
        if collEntry.getIntoNode().getName() != self.mSphereNode.getName():
            return

        place = base.cr.playGame.getPlace()
        if place and place.getState() == 'Walk':
            base.musicMgr.crossfadeIntoMusic(self.trashMusic, duration=0.5, volume=1.0, musicCode=self.musicPath)

    def stopMusic(self, collEntry):
        if collEntry.getIntoNode().getName() != self.mSphereNode.getName():
            return

        place = base.cr.playGame.getPlace()
        if place and place.getState() == 'Walk':
            base.musicMgr.crossfadeIntoMusic(self.playgroundMusic, duration=0.5, volume=0.8, musicCode=base.cr.playGame.hood.loader.music)

    def initToonState(self):
        npcOrigin = self.cr.playGame.hood.loader.geom.find('**/npc_origin_' + str(self.posIndex))
        if not npcOrigin.isEmpty():
            self.reparentTo(npcOrigin)
            self.initPos()

    def initPos(self):
        if not self.can:
            node = base.loader.loadModel('areas/toontown_central/models/cc_a_ara_ttc_prp_trashcan_1')
            self.can = Actor(node, copy=0)
            self.can.reparentTo(self)
            self.can.setH(180)
            self.can.loadAnims({'anim': 'phase_5/models/char/tt_a_ara_ttc_trashcan_open'})
            self.can.setBlend(frameBlend=base.wantSmoothAnims)
            self.can.loop('anim')

    def setPositionIndex(self, posIndex):
        self.posIndex = 1


@NPCToonClass(npcType=NPCToonEnum.TUMBLES)
class DistributedNPCTumbles(DistributedNPCToon):
    # Corresponding quest IDs for below poses: (1534, 2531, 3531, 4539, 5526, 6544, 7534, 8539)
    TumblesPoseIds = [
        ProfilePoseItemType.Selfie,
        ProfilePoseItemType.Diving,
        ProfilePoseItemType.Casting,
        ProfilePoseItemType.Running,
        ProfilePoseItemType.Presenting,
        ProfilePoseItemType.Surprised,
        ProfilePoseItemType.Greened,
        ProfilePoseItemType.Yawn,
    ]

    def __init__(self, cr):
        super().__init__(cr)
        self.npcType = "Tacky Tourist"

    def initToonState(self):
        pass

    def initPos(self):
        DistributedNPCToon.initPos(self)

        self.spawnTumbles()
        self.tumblesPoseCheck()
        if self.zoneId == ToontownGlobals.DonaldsDock:
            self.doFreeze()

    def spawnTumbles(self):
        locationData = ToontownGlobals.TumblesLocations[self.zoneId]
        self.setPos(*locationData[0])
        self.setH(locationData[1])

    # Using poses to check rather than quest IDs here as even holding the final quest of a chain can make tumbles
    # despawn when re-entering the zone...
    # So, to get around this, using the pose rewarded at the end of each task so that Tumbles can only not spawn
    # once the task it completely turned in.
    def tumblesPoseCheck(self):
        inventory = base.cr.inventoryManager.inventory
        if not inventory:
            return

        poseItemSubtypes = [item.getItemSubtype() for item in inventory.findItemsOfType(ProfilePoseItemType)]

        # Spawning (Or rather, don't spawn) Logic
        tumblesPosesOwned = 0
        for poseID in self.TumblesPoseIds:
            if poseID in poseItemSubtypes:
                tumblesPosesOwned += 1
        # Zone and Pose Checks to see if we want Tumbles to spawn
        if tumblesPosesOwned < 8:
            if self.zoneId == ToontownGlobals.ToontownCentral and self.TumblesPoseIds[0] in poseItemSubtypes:
                self.hideNPCToon()
            elif self.zoneId == ToontownGlobals.DonaldsDock and (self.TumblesPoseIds[0] not in poseItemSubtypes or self.TumblesPoseIds[1] in poseItemSubtypes):
                self.hideNPCToon()
            elif self.zoneId == ToontownGlobals.OldeToontown and (self.TumblesPoseIds[1] not in poseItemSubtypes or self.TumblesPoseIds[2] in poseItemSubtypes):
                self.hideNPCToon()
            elif self.zoneId == ToontownGlobals.DaisyGardens and (self.TumblesPoseIds[2] not in poseItemSubtypes or self.TumblesPoseIds[3] in poseItemSubtypes):
                self.hideNPCToon()
            elif self.zoneId == ToontownGlobals.MinniesMelodyland and (self.TumblesPoseIds[3] not in poseItemSubtypes or self.TumblesPoseIds[4] in poseItemSubtypes):
                self.hideNPCToon()
            elif self.zoneId == ToontownGlobals.TheBrrrgh and (self.TumblesPoseIds[4] not in poseItemSubtypes or self.TumblesPoseIds[5] in poseItemSubtypes):
                self.hideNPCToon()
            elif self.zoneId == ToontownGlobals.OutdoorZone and (self.TumblesPoseIds[5] not in poseItemSubtypes or self.TumblesPoseIds[6] in poseItemSubtypes):
                self.hideNPCToon()
            elif self.zoneId == ToontownGlobals.DonaldsDreamland and (self.TumblesPoseIds[6] not in poseItemSubtypes or self.TumblesPoseIds[7] in poseItemSubtypes):
                self.hideNPCToon()
        else:
            # 60% chance to spawn Tumbles randomly if all his quests are complete
            if random.random() <= 0.4:
                self.hideNPCToon()

    def doFreeze(self):
        if base.wantChristmas and self.npc_id in QuestRejects.QuestsRejectDefinedWinter:
            self.showAngryMuzzle()
            self.sadEyes()
            self.setPos(self.getPos() + Vec3(0, 0, 0.31))

    # Since initPos() is ran on the normal NPCToon file version of this func...
    # Custom version here to avoid having Ninja Tumbles at end of a task
    def finishMovie(self, av, isLocalToon, elapsedTime):
        av.startLookAround()
        self.detectAvatars()
        if isLocalToon:
            self.cleanupMovie()
            self.startLookAround()
            self.showNametag2d()
            taskMgr.remove(self.uniqueName('lerpCamera'))
            base.cr.playGame.getPlace().setState('Walk')
            self.sendUpdate('setMovieDone', [])
            self.nametag3d.clearDepthTest()
            self.nametag3d.clearBin()


@NPCToonClass(npcType=NPCToonEnum.TURNKEY)
class DistributedNPCTurnkey(DistributedNPCToon):

    def __init__(self, cr):
        super().__init__(cr)
        self.npcType = "Feast Organizer"

    def initToonState(self):
        self.initPos()

    def initPos(self):
        self.setPos(-108.1, -79.7, 0.525)
        self.setH(-40)
        # self.setBackpack(80, 0, 0)
        # self.setHat(115, 0, 0)


@NPCToonClass(npcType=NPCToonEnum.VALENTINES)
class DistributedNPCValentines(DistributedNPCToon):

    def __init__(self, cr):
        super().__init__(cr)
        self.npcType = "Violets"

    def initToonState(self):
        self.initPos()
        # self.setBackpack(42, 0, 0)

    def initPos(self):
        self.setPos(116, -19.1, 0.82)
        self.setH(90)
        # self.setNametagWithClub(self.npcType, 3)


@NPCToonClass(npcType=NPCToonEnum.WEBSTER)
class DistributedNPCWebster(DistributedNPCToon):

    def __init__(self, cr):
        super().__init__(cr)
        # commented out until a fix for his eye/texture is found
        # self.eyePath = 'phase_3/maps/toon/webstereyes.png'
        self.headPrefix = '/models/char/toons/head/webster-heads-'
        self.npcType = "Shopkeeper"

    def initPos(self):
        pass
        # self.setHat(84, 0, 0)
        # self.toonHat.accessoryGeom.setPosHpr(-0.06, -0.32, 1.05, 180, 5, 5)


@NPCToonClass(npcType=NPCToonEnum.TUTORIAL)
class DistributedNPCLowden(DistributedNPCToon):

    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)
        self.npcType = "Resistance Ranger"

    def announceGenerate(self):
        DistributedNPCToon.announceGenerate(self)
        self.setPickable(0)
        self.reparentTo(render)

    def initPos(self):
        # Name Wordwrap
        if self.npc_toon.nameWordwrap:
            self.nametag.setNameWordwrap(self.npc_toon.nameWordwrap)

    def handleCollisionSphereEnter(self, collEntry):
        pass

    def detectAvatars(self):
        pass

    def generateToon(self):
        self.generateToonLegs()
        self.generateToonHead()
        self.generateToonTorso()
        self.generateToonColor()
        self.generateToonClothes()
        self.parentToonParts()
        self.rescaleToon()
        self.resetHeight()
        self.rightHands = []
        self.leftHands = []
        self.headParts = []
        self.hipsParts = []
        self.torsoParts = []
        self.legsParts = []
        self.__bookActors = []
        self.__holeActors = []
        self.setupToonNodes()
        self.setShaderAuto()
