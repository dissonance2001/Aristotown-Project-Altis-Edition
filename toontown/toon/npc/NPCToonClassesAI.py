from typing import TYPE_CHECKING, List

from panda3d.core import ConfigVariableBool, Point3, Vec3
from direct.distributed.ClockDelta import globalClockDelta
from direct.task.TaskManagerGlobal import taskMgr, Task

from toontown.suit import BossCogGlobals
from toontown.ai.DatabaseObject import DatabaseObject
from toontown.battle import BattleGlobals
from toontown.chat.enums.ChatSystemMessagePreset import ChatSystemMessagePreset
from toontown.fishing import FishGlobals
from toontown.inventory.base.Inventory import Inventory
from toontown.inventory.enums.ItemEnums import ClothingTopItemType, ClothingBottomItemType, NeckItemType, \
    BackpackItemType, GlassesItemType, HatItemType, CheesyEffectItemType, ShoeItemType
from toontown.quest3.base import QuestGlobals
from toontown.quest3.base.QuestHistory import QuestHistory
from toontown.quest3.context.NPCInteractContext import NPCInteractContext
from toontown.quest3.context.PurchaseGagContext import PurchaseGagContext
from toontown.quest3.questlines.KudosQuestLine import *
from toontown.quest3.kudos.KudosConstants import KUDOS_QUESTS_PER_NPC
from toontown.racing.KartDNA import getAccCost, getAccessoryType, getKartCost
from toontown.racing.KartShopGlobals import KartShopGlobals
from toontown.shop.ShopManagerAI import ShopManagerAI
from toontown.shop.base.ShopItem import ShopItem
from toontown.shop.item.InventoryShopItem import InventoryShopItem
from toontown.toon.GagInventoryBase import GagInventoryBase
from toontown.toon.DistributedNPCToonBaseAI import DistributedNPCToonBaseAI
from toontown.toon.DistributedToonAI import DistributedToonAI
from toontown.toon.ToonDNA import ToonDNA
from toontown.toon.npc.NPCToonConstants import *
from toontown.toon.npc.shop.NPCToonShopGlobals import getNPCItemCatalogue
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.toonbase.CooldownManager import CooldownManager

if TYPE_CHECKING:
    from toontown.ai.ToontownAIRepository import ToontownAIRepository


NPCToonClasses = {}


def createNPC(npcType: NPCToonEnum, *args, **kwargs):
    """Finds the npc toon object attached to the npc enum,
    then creates and returns that object, supplying any arguments.
    """
    if npcType not in NPCToonClasses:
        raise NotImplementedError(f"No npc toon object exists for npc enum: {repr(npcType)}.")

    return NPCToonClasses[npcType](*args, **kwargs)


class NPCToonClassAI:
    """NPCToonClassAI: Decorator class used for the sole purpose of
    populating the NPCToonClasses global object with npc toon
    server representations.

    :param npcType: The NPCToonEnum value which to attach the
    desired class to. This can also be a tuple of multiple
    NPCToonEnum values.
    """

    def __init__(self, npcType: NPCToonEnum) -> None:
        self.npcType = npcType

    def __call__(self, cls) -> None:
        # Populate the repository with the type.
        NPCToonClasses[self.npcType] = cls
        return cls


@NPCToonClassAI(npcType=NPCToonEnum.REGULAR)
class DistributedNPCToonAI(DistributedNPCToonBaseAI):

    def __init__(self, air, npcId, questCallback=None, hq=0, canSpawn=True):
        DistributedNPCToonBaseAI.__init__(self, air, npcId, questCallback, canSpawn=canSpawn)
        self.hq = hq
        self.tutorial = 0
        self.pendingAvIds = []
        self.avId2PendingQuests = {}
        self.task = None
        self.endDialogue = 9999  # NPC Quest dialogue timeout
        self.npcId = npcId

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        DistributedNPCToonBaseAI.announceGenerate(self)
        self.sendUpdate("setNpcId", [self.npcId])

    def delete(self):
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('clearMovie'))
        DistributedNPCToonBaseAI.delete(self)

    def getTutorial(self):
        return self.tutorial

    def setTutorial(self, val):
        self.tutorial = val

    def getHq(self):
        return self.hq

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        av: DistributedToonAI = self.air.doId2do.get(avId)
        if not av:
            return
        self.busy = avId

        # Determine if we have progressed from NPC.
        questId = self.air.quest3Manager.progressObjective(av, context=NPCInteractContext(self, av), completeOnlyOne=True)
        if questId:
            # ToonUp the toon to max health if they aren't at full HP.
            if av.getHp() < av.getMaxHp():
                av.toonUp(av.getMaxHp())
            self.completeQuest(avId, questId)
        else:
            questIds = QuestGlobals.getSidequestsByNpcId(av, self.npcId)
            if questIds and av.canAddQuest():
                self.presentQuestChoice(avId, questIds)
            else:
                self.rejectAvatar(avId)

        # Various other movie stuffs.
        self.acceptOnce(self.air.getAvatarExitEvent(avId), self._handleUnexpectedExit, extraArgs=[avId])
        self.clearTasks()
        self.task = self.uniqueName('clearMovie')
        taskMgr.doMethodLater(self.endDialogue, self.sendTimeoutMovie, self.task)
        DistributedNPCToonBaseAI.avatarEnter(self)

    def chooseQuest(self, questId):
        avId = self.air.getAvatarIdFromSender()
        self.notify.debug('chooseQuest: avatar %s choseQuest %s' % (avId, questId))
        if avId not in self.pendingAvIds:
            self.notify.warning('chooseQuest: not expecting an answer from this avatar: %s' % avId)
            return
        if len(self.avId2PendingQuests) == 0:
            self.notify.warning('chooseQuest: not expecting a quest choice from this avatar: %s' % avId)
            self.air.writeServerEvent('suspicious', avId, 'unexpected chooseQuest')
            return
        av: Quester = self.air.doId2do.get(avId)
        if not av:
            return
        
        questId = QuestId.fromStruct(questId)

        for quest in self.avId2PendingQuests[avId]:
            quest: QuestId
            if questId == quest:
                if avId in self.pendingAvIds:
                    self.pendingAvIds.remove(avId)
                    self.avId2PendingQuests[avId] = None
                result = av.addQuest(questId)

                # The quester received the quest.
                if result:
                    # Remove the tasks for timeout.
                    taskMgr.remove(self.uniqueName('clearMovie'))

                    # Assign the quest.
                    self.assignQuest(avId, questId)
                    return
        self.notify.warning('chooseQuest: avatar: %s chose a quest not offered: %s' % (avId, questId))
        if avId in self.pendingAvIds:
            self.pendingAvIds.remove(avId)
            self.avId2PendingQuests[avId] = None
        self.cancelChoseQuest(avId)
    
    def cancelChooseQuest(self):
        avId = self.air.getAvatarIdFromSender()
        self.notify.debug('chooseQuest: avatar %s cancelChooseQuest %s')
        if avId not in self.pendingAvIds:
            self.notify.warning('chooseQuest: not expecting an answer from this avatar: %s' % avId)
            return
        if len(self.avId2PendingQuests) == 0:
            self.notify.warning('chooseQuest: not expecting a quest choice from this avatar: %s' % avId)
            self.air.writeServerEvent('suspicious', avId, 'unexpected chooseQuest')
            return
        self.pendingAvIds.remove(avId)
        self.avId2PendingQuests[avId] = None
        self.cancelChoseQuest(avId)

    def sendTimeoutMovie(self, avId=None, task=None):
        self.pendingTracks = None
        self.pendingTrackQuest = None
        if avId in self.pendingAvIds:
            self.sendUpdateToAvatarId(avId, 'setMovie', [QUEST_MOVIE_TIMEOUT,
                                                         self.npcId,
                                                         self.busy,
                                                         [],
                                                         globalClockDelta.getRealNetworkTime(), []])
            self.pendingAvIds.remove(avId)
            del self.avId2PendingQuests[avId]
        self.sendClearMovie(avId=avId)
        return Task.done

    def sendClearMovie(self, avId=None, task=None):
        self.pendingTracks = None
        self.pendingTrackQuest = None
        self.busy = 0
        if avId in self.pendingAvIds:
            self.sendUpdateToAvatarId(avId, 'setMovie', [
                QUEST_MOVIE_CLEAR, self.npcId, 0, [], globalClockDelta.getRealNetworkTime(), []
            ])
            self.pendingAvIds.remove(avId)
            del self.avId2PendingQuests[avId]
        return Task.done

    def rejectAvatar(self, avId):
        self.busy = avId
        self.sendUpdateToAvatarId(avId, 'setMovie', [
            QUEST_MOVIE_REJECT, self.npcId, avId, [], globalClockDelta.getRealNetworkTime(), []
        ])
        if not self.tutorial:
            taskMgr.doMethodLater(5.5, self.sendClearMovie, self.uniqueName('clearMovie'), extraArgs=[avId])

    def rejectAvatarTierNotDone(self, avId):
        self.busy = avId
        self.sendUpdate('setMovie', [
            QUEST_MOVIE_TIER_NOT_DONE, self.npcId, avId, [], globalClockDelta.getRealNetworkTime()
        ])
        if not self.tutorial:
            self.clearTasks()
            self.task = self.uniqueName('clearMovie')
            taskMgr.doMethodLater(5.5, self.sendClearMovie, self.task, extraArgs=[avId])

    def completeQuest(self, avId, questId):
        self.busy = avId
        self.sendUpdateToAvatarId(avId, 'setMovie', [QUEST_MOVIE_COMPLETE,
                                                     self.npcId,
                                                     avId,
                                                     [],
                                                     globalClockDelta.getRealNetworkTime(bits=16),
                                                     [questId.toStruct()]])
        if not self.tutorial:
            self.clearTasks()
            self.task = self.uniqueName('clearMovie')
            taskMgr.doMethodLater(540.0, self.sendTimeoutMovie, self.task, extraArgs=[avId])

    def incompleteQuest(self, avId, questId, completeStatus, toNpcId):
        self.busy = avId
        self.sendUpdateToAvatarId(avId, 'setMovie', [QUEST_MOVIE_INCOMPLETE,
                                                     self.npcId,
                                                     avId,
                                                     [questId, completeStatus, toNpcId],
                                                     globalClockDelta.getRealNetworkTime(), []])
        if not self.tutorial:
            self.clearTasks()
            self.task = self.uniqueName('clearMovie')
            taskMgr.doMethodLater(540.0, self.sendTimeoutMovie, self.task, extraArgs=[avId])

    def assignQuest(self, avId, questId: QuestId):
        self.busy = avId
        if self.questCallback:
            self.questCallback()
        self.sendUpdateToAvatarId(avId, 'setMovie', [QUEST_MOVIE_ASSIGN,
                                                     self.npcId,
                                                     avId,
                                                     [],
                                                     globalClockDelta.getRealNetworkTime(), [questId.toStruct()]])
        if not self.tutorial:
            self.clearTasks()
            self.task = self.uniqueName('clearMovie')
            taskMgr.doMethodLater(540.0, self.sendTimeoutMovie, self.task, extraArgs=[avId])

    def presentQuestChoice(self, avId, questIds: "List[QuestId]"):
        self.busy = avId
        if avId in self.pendingAvIds:
            return
        self.pendingAvIds.append(avId)
        self.avId2PendingQuests[avId] = questIds
        flatQuests = [quest.toStruct() for quest in questIds]

        self.sendUpdateToAvatarId(avId, 'setMovie', [QUEST_MOVIE_QUEST_CHOICE,
                                                     self.npcId,
                                                     avId,
                                                     [],
                                                     globalClockDelta.getRealNetworkTime(), flatQuests])
        if not self.tutorial:
            self.clearTasks()
            self.task = self.uniqueName('clearMovie')
            taskMgr.doMethodLater(20.0, self.sendTimeoutMovie, self.task, extraArgs=[avId])

    def cancelChoseQuest(self, avId):
        self.busy = avId
        self.sendUpdateToAvatarId(avId, 'setMovie', [QUEST_MOVIE_QUEST_CHOICE_CANCEL,
                                                     self.npcId,
                                                     avId,
                                                     [],
                                                     globalClockDelta.getRealNetworkTime(), []])
        if not self.tutorial:
            self.clearTasks()
            self.task = self.uniqueName('clearMovie')
            taskMgr.doMethodLater(60.0, self.sendTimeoutMovie, self.task, extraArgs=[avId])

    def setMovieDone(self):
        avId = self.air.getAvatarIdFromSender()
        self.notify.debug('setMovieDone busy: %s avId: %s' % (self.busy, avId))
        self.clearTasks()
        self.sendClearMovie(avId=avId)

    def _handleUnexpectedExit(self, avId):
        self.notify.warning('avatar:' + str(avId) + ' has exited unexpectedly')
        self.notify.warning('not busy with avId: %s, busy: %s ' % (avId, self.busy))
        self.clearTasks()
        taskMgr.remove(self.uniqueName('clearMovie'))
        self.sendClearMovie(avId=avId)

    def clearTasks(self):
        if self.task:
            taskMgr.remove(self.task)

        self.task = None


@NPCToonClassAI(npcType=NPCToonEnum.CLUB_CREATION)
class DistributedNPCClubCreationAI(DistributedNPCToonAI):
    pass


@NPCToonClassAI(npcType=NPCToonEnum.CLUB_SHOP)
class DistributedNPCClubShopAI(DistributedNPCToonAI):
    pass


@NPCToonClassAI(npcType=NPCToonEnum.EASTER)
class DistributedNPCEasterAI(DistributedNPCToonAI):
    pass


@NPCToonClassAI(npcType=NPCToonEnum.ELF)
class DistributedNPCElfAI(DistributedNPCToonAI):
    pass


@NPCToonClassAI(npcType=NPCToonEnum.FIREWORK)
class DistributedNPCFireworkAI(DistributedNPCToonAI):
    pass


@NPCToonClassAI(npcType=NPCToonEnum.FLIPPYTOONHALL)
class DistributedNPCFlippyInToonHallAI(DistributedNPCToonAI):
    pass


@NPCToonClassAI(npcType=NPCToonEnum.GHASTLY)
class DistributedNPCGhastlyAI(DistributedNPCToonAI):
    pass


@NPCToonClassAI(npcType=NPCToonEnum.HQ)
class DistributedNPCHQOfficerAI(DistributedNPCToonAI):
    hq = 1

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.kudosQuests = []

    def announceGenerate(self) -> None:
        super().announceGenerate()

        # Generate an initial batch of kudos quests.
        self.generateKudosQuests()
        # Listen for the kudos manager to reset our kudos quests
        # twice a day.
        self.accept("kudos_bidailyReset", self.generateKudosQuests)

    def delete(self) -> None:
        self.ignore("kudos_bidailyReset")
        super().delete()

    def generateKudosQuests(self) -> None:
        """Generates and saves a list of kudos quest ids that
        any quester which interacts with the NPC can choose from.
        """
        # Generate 3 random kudos quest chains.
        questChains = [
            KudosQuestLine.getRandomKudosQuestChainId(self.zoneId, self.npcId, index=i)
            for i in range(KUDOS_QUESTS_PER_NPC)
        ]

        # Finally, save the quest ids.
        self.kudosQuests = [QuestId(QuestSource.KudosQuest, chainId, 1) for chainId in questChains]

    def getKudosQuests(self, quester: Quester) -> None:
        """Filters the randomly generated list of kudos quest ids based
        on whether the given quester has already completed the quest
        or not.
        """
        # Don't show any quests if they're already full.
        if not quester.canAddQuest():
            return []

        # Find out of they are eligible for a rank up quest.
        questId = KudosConstants.getRankUpKudosTask(quester, ZoneUtil.getSafeZoneId(self.zoneId))
        if questId:
            # Ensure that the quester doesn't already have the quest.
            if quester.hasQuest(questId, history=True):
                return []
            return [questId]

        # Disable grabbing kudos tasks from HQ officers for now.
        return []

        # Create a shallow copy of the kudos quests list.
        kudosQuests = self.kudosQuests.copy()

        # Iterate the kudos quests and remove any that the
        # given quester has already completed.
        for quest in self.kudosQuests:
            if not self.canChooseKudosQuest(quester, quest):
                kudosQuests.remove(quest)

        # Return the result.
        return kudosQuests

    def canChooseKudosQuest(self, quester: Quester, questId: QuestId) -> bool:
        questHistory = QuestHistory(QuestSource.KudosQuest, questId.getChainId())
        if questHistory in quester.getQuestHistory():
            return False
        elif questId in quester.getQuestIdsFromRefs():
            return False
        else:
            questChain = QuestLine.getQuestChainFromId(QuestSource.KudosQuest, questId.getChainId(), quester=quester)
            if questChain is None:
                return False
            if not questChain.validate(quester):
                return False
        return True

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        av: DistributedToonAI = self.air.doId2do.get(avId)
        if not av:
            return
        self.busy = avId

        # Determine if we have progressed from NPC.
        questId = self.air.quest3Manager.progressObjective(av, context=NPCInteractContext(self, av), completeOnlyOne=True)
        if questId:
            # ToonUp the toon to max health if they aren't at full HP.
            if av.getHp() < av.getMaxHp():
                av.toonUp(av.getMaxHp())
            self.completeQuest(avId, questId)
        else:
            # Retrieve our kudos quests.
            questIds = self.getKudosQuests(av)
            if questIds:
                self.presentQuestChoice(avId, questIds)
            else:
                self.rejectAvatar(avId)

        # Various other movie stuffs.
        self.acceptOnce(self.air.getAvatarExitEvent(avId), self._handleUnexpectedExit, extraArgs=[avId])
        self.clearTasks()
        self.task = self.uniqueName('clearMovie')
        taskMgr.doMethodLater(self.endDialogue, self.sendTimeoutMovie, self.task)


@NPCToonClassAI(npcType=NPCToonEnum.HQ_INTERN)
class DistributedNPCHQInternAI(DistributedNPCHQOfficerAI):
    pass


@NPCToonClassAI(npcType=NPCToonEnum.HQRANGER)
class DistributedNPCHQRangerAI(DistributedNPCHQOfficerAI):
    pass


@NPCToonClassAI(npcType=NPCToonEnum.RED_NOSE)
class DistributedNPCRedNoseAI(DistributedNPCToonAI):
    pass


@NPCToonClassAI(npcType=NPCToonEnum.SPIRITS)
class DistributedNPCToonsmasSpiritsAI(DistributedNPCToonAI):
    pass


@NPCToonClassAI(npcType=NPCToonEnum.TRASHCAT)
class DistributedNPCTrashCatAI(DistributedNPCToonAI):
    pass


@NPCToonClassAI(npcType=NPCToonEnum.TUMBLES)
class DistributedNPCTumblesAI(DistributedNPCToonAI):
    pass


@NPCToonClassAI(npcType=NPCToonEnum.TURNKEY)
class DistributedNPCTurnkeyAI(DistributedNPCToonAI):
    pass


@NPCToonClassAI(npcType=NPCToonEnum.VALENTINES)
class DistributedNPCValentinesAI(DistributedNPCToonAI):
    pass


@NPCToonClassAI(npcType=NPCToonEnum.WEBSTER)
class DistributedNPCWebsterAI(DistributedNPCToonAI):
    pass


@NPCToonClassAI(npcType=NPCToonEnum.CLERK)
class DistributedNPCClerkAI(DistributedNPCToonBaseAI):

    def setInventory(self, inventory, money):
        av = self.air.doId2do.get(self.air.getAvatarIdFromSender())

        if not av:
            return

        av.setMoney(money if av.inventory.validatePurchase(av.inventory.makeFromNetString(inventory), av.getMoney(), money) else av.getMoney())
        av.d_setInventory(av.inventory.makeNetString())
        self.air.quest3Manager.progressObjective(quester=av, context=PurchaseGagContext())

    def setState(self, avId, state):
        self.sendUpdate('setState', [self.air.getAvatarIdFromSender(), state])


@NPCToonClassAI(npcType=NPCToonEnum.GNG_CLERK)
class DistributedNPCGagAndGoClerkAI(DistributedNPCClerkAI):
    pass # Completely identical AI sided to regular gag clerks, at least currently


@NPCToonClassAI(npcType=NPCToonEnum.BUBBY)
class DistributedNPCBubbyAI(DistributedNPCToonAI):
    def __init__(self, air, npcId, questCallback=None, hq=0):
        DistributedNPCToonAI.__init__(self, air, npcId, questCallback)
        self.air = air  # type: ToontownAIRepository

    def requestCheck(self):
        av = self.air.getDo(self.air.getAvatarIdFromSender())
        if not av:
            return

        if len(av.seenPlants) == 27:
            # They have finished the ARG! Now they can hear Bubby talk.
            return self.sendUpdateToAvatarId(av.doId, 'requestCheckChatResponse', ["Dad's been looking lonely recently. Maybe you could go cheer him up!"]) # This is gross. I know. Dataminers be damned.
        else:
            # They haven't finished the plant puzzle yet, Bubby will just rustle
            av.b_setSeenPlants([])
            self.sendUpdateToAvatarId(av.doId, 'requestCheckResponse', [0])


class DistributedNPCBumpyAI(DistributedNPCToonAI):

    def __init__(self, air, lawbotBoss, npcId, questCallback = None, hq = 0):
        DistributedNPCToonAI.__init__(self, air, npcId, questCallback)
        self.speed = ToontownGlobals.ToonForwardSpeed
        self.distance = 0
        self.boss = lawbotBoss
        self.bossId = lawbotBoss.doId
        self.currPos = None
        self.isIdle = False
        self.trap = None
        self.lastTrapIndex = None

    def delete(self):
        taskMgr.remove(self.uniqueName('NextMove'))
        taskMgr.remove(self.uniqueName('DetermineAdvice'))
        taskMgr.remove(self.uniqueName("TrapMove"))
        self.speed = None
        self.distance = None
        self.boss = None
        self.bossId = None
        self.currPos = None
        self.isIdle = None
        self.trap = None
        self.lastTrapIndex = None
        DistributedNPCToonAI.delete(self)

    def getPosHpr(self):
        return (
            self.getX(),
            self.getY(),
            self.getZ(),
            self.getH(),
            self.getP(),
            self.getR()
        )

    def getBossCogId(self):
        return self.bossId

    def initializeTimers(self):
        self.waitForNextMove(1)
        self.waitToDetermineAdvice(20)

    def waitForNextMove(self, delayTime):
        taskName = self.uniqueName('NextMove')
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(delayTime, self.doNextMove, taskName)

    def doNextMove(self, taskName):
        self.trap = None
        self.currPos = self.getPos()
        if self.boss.traps is None:
            return
        disabledTraps = self.__getDisabledBossTraps()
        brokenTraps = self.__getBrokenBossTraps()
        activeTraps = self.__getActiveBossTraps()
        if len(disabledTraps) == 0 and len(brokenTraps) == 0:
            self.doIdle()
            return

        self.isIdle = False
        trap = None
        if self.boss.traps[0].getStatus() != 1:
            trap = self.boss.traps[0]
        elif len(activeTraps) + len(brokenTraps) <= 5 and disabledTraps:
            trap = random.choice(disabledTraps)
        elif brokenTraps:
            trap = random.choice(brokenTraps)
            if self.boss.trapIndex == self.boss.traps.index(trap):
                brokenTraps.remove(trap)
                if brokenTraps:
                    trap = random.choice(brokenTraps)
                else:
                    self.doIdle()
                    return

        elif trap is None or (self.boss.traps.index(trap) == self.lastTrapIndex):
            self.doIdle()
            return

        self.trap = trap
        self.lastTrapIndex = self.boss.traps.index(self.trap)
        self.d_doTravelMove()

    def __getDisabledBossTraps(self):
        return self.boss.getDisabledBossTraps()

    def __getBrokenBossTraps(self):
        return self.boss.getBrokenBossTraps()

    def __getActiveBossTraps(self):
        return self.boss.getActiveBossTraps()

    def d_doTravelMove(self):
        if self.boss.traps is None:
            return
        trapIndex = self.boss.traps.index(self.trap)
        x, y, z = BossCogGlobals.LawbotBossBumpyTrapsPos[trapIndex]
        toPos = Point3(x, y, z)
        self.distance = Vec3(toPos - self.currPos).length()
        time = self.getTimeToWalk()
        self.setPos(toPos)
        self.sendUpdate("doTravelMove", [str(time), x, y])
        self.waitToDoTrap(time)

    def waitToDoTrap(self, delayTime):
        taskName = self.uniqueName("TrapMove")
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(delayTime, self.d_doTrapMove, taskName)

    def d_doTrapMove(self, taskName):
        if self.boss.traps is None or self.trap is None:
            return
        trapIndex = self.boss.traps.index(self.trap)
        trapStatus = self.trap.getStatus()
        delayTime = 0
        if trapStatus != 1:
            if trapStatus == -1:
                delayTime = 10
                self.trap.startRepair()
            else:
                delayTime = 5
                self.trap.startEnable()
            self.sendUpdate("doTrapMove", [trapIndex, trapStatus])
        self.waitForNextMove(delayTime)

    def doIdle(self):
        if not self.isIdle:
            self.isIdle = True
            self.d_doIdleMove()
        else:
            self.waitForNextMove(1)

    def waitToDetermineAdvice(self, delayTime=15):
        taskName = self.uniqueName('DetermineAdvice')
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(delayTime, self.determineAdvice, taskName)

    def determineAdvice(self, taskName):
        helpIndex = random.choice(list(range(len(TTLocalizer.LawbotBossBumpyAdvice))))
        self.d_sayAdvice(helpIndex)
        self.waitToDetermineAdvice()

    def d_sayAdvice(self, helpIndex):
        self.sendUpdate('sayAdvice', [helpIndex])

    def d_doIdleMove(self):
        x, y, z, h, p, r = BossCogGlobals.LawbotBossBumpyIdlePosHpr
        toPos = Point3(x, y, z)
        self.distance = Vec3(toPos - self.currPos).length()
        time = self.getTimeToWalk()
        self.setPos(Point3(x, y, z))
        self.sendUpdate('doIdleMove', [str(time), x, y, h])
        self.waitForNextMove(time)

    def getTimeToWalk(self):
        return self.distance / self.speed

    def bossLandBroken(self):
        self.waitForNextMove(0)


@NPCToonClassAI(npcType=NPCToonEnum.ELPHABAT)
class DistributedNPCElphabatAI(DistributedNPCToonAI, ShopManagerAI):

    def __init__(self, air, npcId, questCallback=None, hq=0):
        DistributedNPCToonAI.__init__(self, air, npcId, questCallback)

        from toontown.events.halloween.HalloweenStoreItems import HalloweenShopItems
        ShopManagerAI.__init__(self, air, HalloweenShopItems)

    def sendPurchaseNotification(self, av: DistributedToonAI):
        pass

    def callbackAvatarCannotAfford(self, shopItem: ShopItem, av: DistributedToonAI):
        self.sendUpdate('handleBuyResponse', [1, av.doId])

    def performAdditionalPurchaseChecks(self, shopItem: ShopItem, av: DistributedToonAI) -> bool:
        if isinstance(shopItem, InventoryShopItem):
            if shopItem.ownsItem(av):
                self.sendUpdate('handleBuyResponse', [2, av.doId])
                return False
        return True

    def callbackAvatarCannotPurchase(self, shopItem: ShopItem, av: DistributedToonAI):
        self.sendUpdate('handleBuyResponse', [3, av.doId])

    def callbackPurchaseAttemptFailed(self, shopItem: ShopItem, av: DistributedToonAI):
        self.sendUpdate('handleBuyResponse', [4, av.doId])

    def callbackPurchaseSuccessful(self, shopItem: ShopItem, av: DistributedToonAI, returnValue=None):
        if returnValue is True:
            self.sendUpdate('handleBuyResponse', [5, av.doId])
        else:
            self.sendUpdate('handleBuyResponse', [0, av.doId])

    def toonInteracted(self, contextCode):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av:
            return

        # Get the pool of phrases we can say using the context code
        # Since this is given from the client, make sure its allowed
        phrasePool = TTLocalizer.halloweenWitchEnterExitResponses.get(contextCode)
        if not phrasePool:
            return

        # Generate a random phrase index
        phraseIndex = random.randint(0, len(phrasePool)-1)
        self.sendUpdate('handleInteraction', [avId, contextCode, phraseIndex])


@NPCToonClassAI(npcType=NPCToonEnum.FISHERMAN)
class DistributedNPCFishermanAI(DistributedNPCToonBaseAI):

    def __init__(self, air, npcId):
        DistributedNPCToonBaseAI.__init__(self, air, npcId)
        self.givesQuests = 0
        self.busy = 0

    def delete(self):
        taskMgr.remove(self.uniqueName('clearMovie'))
        self.ignoreAll()
        DistributedNPCToonBaseAI.delete(self)

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.air.doId2do:
            self.notify.warning('Avatar: %s not found' % avId)
            return
        if self.isBusy():
            self.freeAvatar(avId)
            return
        for spot in self.air.hoodId2Hood[ZoneUtil.getCanonicalBranchZone(self.zoneId)].fishingSpots:
            if spot.avId == avId:
                return

        av = self.air.doId2do[avId]
        self.busy = avId
        self.acceptOnce(self.air.getAvatarExitEvent(avId), self._handleUnexpectedExit, extraArgs=[avId])
        value = av.fishTank.getTotalValue()
        if value > 0:
            flag = SELL_MOVIE_START
            self.d_setMovie(avId, flag)
            taskMgr.doMethodLater(30.0, self.sendTimeoutMovie, self.uniqueName('clearMovie'))
        else:
            flag = SELL_MOVIE_NOFISH
            self.d_setMovie(avId, flag)
            self.sendClearMovie(None)
        DistributedNPCToonBaseAI.avatarEnter(self)
        return

    def rejectAvatar(self, avId):
        self.notify.warning('rejectAvatar: should not be called by a fisherman!')

    def d_setMovie(self, avId, flag, extraArgs = []):
        self.sendUpdate('setMovie', [flag,
         self.npcId,
         avId,
         extraArgs,
         globalClockDelta.getRealNetworkTime()])

    def sendTimeoutMovie(self, task):
        self.d_setMovie(self.busy, SELL_MOVIE_TIMEOUT)
        self.sendClearMovie(None)
        return Task.done

    def sendClearMovie(self, task):
        self.ignore(self.air.getAvatarExitEvent(self.busy))
        taskMgr.remove(self.uniqueName('clearMovie'))
        self.busy = 0
        self.d_setMovie(0, SELL_MOVIE_CLEAR)
        return Task.done

    def completeSale(self, sell):
        avId = self.air.getAvatarIdFromSender()
        if self.busy != avId:
            self.air.writeServerEvent('suspicious', avId, 'DistributedNPCFishermanAI.completeSale busy with %s' % self.busy)
            self.notify.warning('somebody called setMovieDone that I was not busy with! avId: %s' % avId)
            return

        for spot in self.air.hoodId2Hood[ZoneUtil.getCanonicalBranchZone(self.zoneId)].fishingSpots:
            if spot.avId == avId:
                self.sendClearMovie(None)
                return

        if sell:
            av = simbase.air.doId2do.get(avId)
            if av:
                trophyResult = self.air.fishManager.creditFishTank(av)
                if trophyResult:
                    movieType = SELL_MOVIE_TROPHY
                    extraArgs = [len(av.fishCollection), FishGlobals.getTotalNumFish()]
                else:
                    movieType = SELL_MOVIE_COMPLETE
                    extraArgs = []
                self.d_setMovie(avId, movieType, extraArgs)
        else:
            av = simbase.air.doId2do.get(avId)
            if av:
                self.d_setMovie(avId, SELL_MOVIE_NOFISH)
        self.sendClearMovie(None)
        return

    def _handleUnexpectedExit(self, avId):
        self.notify.warning('avatar:' + str(avId) + ' has exited unexpectedly')
        self.notify.warning('not busy with avId: %s, busy: %s ' % (avId, self.busy))
        taskMgr.remove(self.uniqueName('clearMovie'))
        self.sendClearMovie(None)
        return


@NPCToonClassAI(npcType=NPCToonEnum.HALLOWEEN_PASS)
class DistributedNPCHalloweenPassAI(DistributedNPCToonAI):
    # Item Costs
    passCostToItem = {200:  [ClothingTopItemType.JacketAndFlannel],  # mcfly shirt
                      500:  [ClothingTopItemType.Detective,
                             ClothingBottomItemType.DetectiveShorts,
                             NeckItemType.MysteryBowtie],  # Detective outfit
                      800:  [BackpackItemType.Backpack_Plushie_Sads],  # Skelecog Backpack
                      1100: [ClothingBottomItemType.FloralShorts],  # patrick shorts
                      1400: [ClothingTopItemType.TwoPocketCargo],  # Chris McClean Shirt
                      1700: [GlassesItemType.Mask_Count],  # Count Facemask
                      2000: [ClothingTopItemType.ChupShirt,
                             ClothingBottomItemType.ChupShorts,
                             ClothingBottomItemType.ChupSkirt],  # Chup Outfit
                      2300: [HatItemType.Hat_GhostlyGibus],  # Ghastly Gibbus Hat
                      2600: [CheesyEffectItemType.Spirit],  # Spirit Cheesy Effect (slightly more transparent white toon)
                      2900: [NeckItemType.EyeBowtie],  # Evil Eye Bowtie
                      3200: [ClothingTopItemType.HallowopolisShirt,
                             ClothingBottomItemType.HallowopolisShorts,
                             GlassesItemType.Mask_HWTown,
                             BackpackItemType.Backpack_Cape_HwTown,
                             ShoeItemType.HallowopolisBoots],  # HWTown Outfit
                      3500: [HatItemType.Overhead_Pumpkin_2021_Short,],  # Scapegourd
                      5777: [CheesyEffectItemType.Stomped,],  # Stomped
                      ToontownGlobals.MaxBatcoin: [CheesyEffectItemType.Amogus,
                                                   GlassesItemType.Glasses_Visor_SciFi],  # Sussy Rewards
                      }

    def __init__(self, air, npcId, questCallback=None, hq=0):
        DistributedNPCToonAI.__init__(self, air, npcId, questCallback)
        self.cooldown = CooldownManager(5)

    def deliverItem(self, item, av):
        inv: Inventory = av.getHammerspace()
        if not inv:
            return
        if inv.cache.getItemsOfSubtype(item):
            return
        inv.addItem(item)

    def getValidRewards(self, points, av, quietly=False):  # This function dynamically returns the threshold based on points owned
        itemCosts = list(self.passCostToItem)
        deliverItemList = []
        for cost in itemCosts:
            if points >= cost:  # If the points owned are equal or higher than current cost being checked
                deliverItemList += self._getNecessaryItems(cost, av)  # If we don't already own the item, it to items able to be delivered
            else:  # If the cost is higher than points owned
                if not deliverItemList:  # Check if we have prizes able to be delivered; if none, say we can't afford next prize
                    # don't spam this twice just to check if we can flash
                    if not quietly:
                        self.air.chatManager.sendSystemMessageToToon(av.doId, TTLocalizer.HalloweenPassNotEnough, preset = ChatSystemMessagePreset.Halloween)
                    return

        return deliverItemList  # Return the rewards list

    def _getNecessaryItems(self, cost, av) -> list:
        """Returns a list of all items we haven't gotten yet."""
        retlist = []
        for item in self.passCostToItem[cost]:
            if not item.reachedPurchaseLimit(av):
                retlist.append(cost)
                break
        return retlist

    def checkForRewards(self):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av:
            return

        hasRewards = self.getValidRewards(av.getBatcoins(), av, quietly=True)
        if hasRewards:
            self.sendUpdateToAvatarId(avId, 'setHasItemsToClaim', [1])
        else:
            self.sendUpdateToAvatarId(avId, 'setHasItemsToClaim', [0])

    def checkForPrizes(self):
        """
        This method is called by the Client Pass GUI.
        Here we're going to check the users points and send them the items they don't have yet.
        """
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av:
            return

        # Check to see if we're allowed to process this
        if not self.cooldown.check(avId).outcome:
            return

        # Get their total amount of Batcoins
        totalPoints = av.getBatcoins()

        # Time to check if they can get rewards
        validRewards = self.getValidRewards(totalPoints, av)
        if validRewards:  # They have rewards to get
            if totalPoints == ToontownGlobals.MaxBatcoin:
                pass
                # We do not want this message anymore.
                # av.showToonTip(TTE.TIP_MAX_BATCOINS)
            for reward in validRewards:
                for delivery in self.passCostToItem[reward]:  # Make sure we get all rewards if there's multiple for a threshhold
                    self.deliverItem(delivery, av)  # Deliver their gaming rewards

    # Called from clients when they interact with the npc
    def toonInteracted(self, contextCode):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av:
            return

        # Get the pool of phrases we can say using the context code
        # Since this is given from the client, make sure its allowed
        phrasePool = TTLocalizer.halloweenPassEnterExitResponses.get(contextCode)
        if not phrasePool:
            return

        # Generate a random phrase index
        phraseIndex = random.randint(0, len(phrasePool)-1)
        self.sendUpdate('handleInteraction', [avId, contextCode, phraseIndex])


@NPCToonClassAI(npcType=NPCToonEnum.KARTCLERK)
class DistributedNPCKartClerkAI(DistributedNPCToonBaseAI):

    def __init__(self, air, npcId):
        DistributedNPCToonBaseAI.__init__(self, air, npcId)
        self.givesQuests = 0
        self.busy = 0

    def delete(self):
        taskMgr.remove(self.uniqueName('clearMovie'))
        self.ignoreAll()
        DistributedNPCToonBaseAI.delete(self)

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.air.doId2do:
            self.notify.warning('Avatar: %s not found' % avId)
            return
        if self.isBusy():
            self.freeAvatar(avId)
            return
        self.transactionType = ''
        av = self.air.doId2do[avId]
        self.busy = avId
        self.acceptOnce(self.air.getAvatarExitEvent(avId), self._handleUnexpectedExit, extraArgs=[avId])
        flag = SELL_MOVIE_START
        self.d_setMovie(avId, flag)
        taskMgr.doMethodLater(KartShopGlobals.KARTCLERK_TIMER, self.sendTimeoutMovie, self.uniqueName('clearMovie'))
        DistributedNPCToonBaseAI.avatarEnter(self)

    def rejectAvatar(self, avId):
        self.notify.warning('rejectAvatar: should not be called by a kart clerk!')

    def d_setMovie(self, avId, flag, extraArgs = []):
        self.sendUpdate('setMovie', [flag,
         self.npcId,
         avId,
         extraArgs,
         globalClockDelta.getRealNetworkTime()])

    def sendTimeoutMovie(self, task):
        self.d_setMovie(self.busy, SELL_MOVIE_TIMEOUT)
        self.sendClearMovie(None)
        return Task.done

    def sendClearMovie(self, task):
        self.ignore(self.air.getAvatarExitEvent(self.busy))
        taskMgr.remove(self.uniqueName('clearMovie'))
        self.busy = 0
        self.d_setMovie(0, SELL_MOVIE_CLEAR)
        return Task.done

    def buyKart(self, whichKart):
        avId = self.air.getAvatarIdFromSender()
        if self.busy != avId:
            self.air.writeServerEvent('suspicious', avId, 'DistributedNPCKartClerkAI.buyKart busy with %s' % self.busy)
            self.notify.warning('somebody called buyKart that I was not busy with! avId: %s' % avId)
            return
        av = simbase.air.doId2do.get(avId)
        if av:
            movieType = SELL_MOVIE_COMPLETE
            extraArgs = []
            cost = getKartCost(whichKart)
            if cost == 'key error':
                self.air.writeServerEvent('suspicious', avId, 'Player trying to buy non-existant kart %s' % whichKart)
                self.notify.warning('somebody is trying to buy non-existant kart%s! avId: %s' % (whichKart, avId))
                return
            elif cost > av.getTotalMoney():
                self.air.writeServerEvent('suspicious', avId, "DistributedNPCKartClerkAI.buyKart and toon doesn't have enough jellybeans!")
                self.notify.warning("somebody called buyKart and didn't have enough jellybeans to purchase! avId: %s" % avId)
                return
            av.takeMoney(cost)
            self.air.writeServerEvent('kartingTicketsSpent', avId, '%s' % cost)
            av.b_setKartBodyType(whichKart)
            self.air.writeServerEvent('kartingKartPurchased', avId, '%s' % whichKart)

    def buyAccessory(self, whichAcc):
        avId = self.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)
        if self.busy != avId:
            self.air.writeServerEvent('suspicious', avId, 'DistributedNPCKartClerkAI.buyAccessory busy with %s' % self.busy)
            self.notify.warning('somebody called buyAccessory that I was not busy with! avId: %s' % avId)
            return
        if len(av.getKartAccessoriesOwned()) >= KartShopGlobals.MAX_KART_ACC:
            self.air.writeServerEvent('suspicious', avId, 'DistributedNPCKartClerkAI.buyAcc and toon already has max number of accessories!')
            self.notify.warning('somebody called buyAcc and already has maximum allowed accessories! avId: %s' % avId)
            return
        av = simbase.air.doId2do.get(avId)
        if av:
            movieType = SELL_MOVIE_COMPLETE
            extraArgs = []
            cost = getAccCost(whichAcc)
            if cost > av.getTotalMoney():
                self.air.writeServerEvent('suspicious', avId, "DistributedNPCKartClerkAI.buyAcc and toon doesn't have enough jellybeans!")
                self.notify.warning("somebody called buyAcc and didn't have enough jellybeans to purchase! avId: %s" % avId)
                return
            av.takeMoney(cost)
            self.air.writeServerEvent('kartingTicketsSpent', avId, '%s' % cost)
            av.addOwnedAccessory(whichAcc)
            self.air.writeServerEvent('kartingAccessoryPurchased', avId, '%s' % whichAcc)
            av.updateKartDNAField(getAccessoryType(whichAcc), whichAcc)

    def transactionDone(self):
        avId = self.air.getAvatarIdFromSender()
        if self.busy != avId:
            self.air.writeServerEvent('suspicious', avId, 'DistributedNPCKartClerkAI.transactionDone busy with %s' % self.busy)
            self.notify.warning('somebody called transactionDone that I was not busy with! avId: %s' % avId)
            return
        av = simbase.air.doId2do.get(avId)
        if av:
            movieType = SELL_MOVIE_COMPLETE
            extraArgs = []
            self.d_setMovie(avId, movieType, extraArgs)
        self.sendClearMovie(None)
        return

    def _handleUnexpectedExit(self, avId):
        self.notify.warning('avatar:' + str(avId) + ' has exited unexpectedly')
        self.notify.warning('not busy with avId: %s, busy: %s ' % (avId, self.busy))
        taskMgr.remove(self.uniqueName('clearMovie'))
        self.sendClearMovie(None)
        return


class DistributedNPCLaurenAI(DistributedNPCToonAI):

    def __init__(self, air, lawbotBoss, npcId, questCallback = None, hq = 0):
        DistributedNPCToonAI.__init__(self, air, npcId, questCallback)
        self.speed = ToontownGlobals.ToonForwardSpeed
        self.distance = 0
        self.boss = lawbotBoss
        self.bossId = lawbotBoss.doId
        self.currPos = None
        self.isIdle = False
        self.trap = None

    def delete(self):
        taskMgr.remove(self.uniqueName('NextMove'))
        taskMgr.remove(self.uniqueName("TrapMove"))
        self.speed = None
        self.distance = None
        self.boss = None
        self.bossId = None
        self.currPos = None
        self.isIdle = None
        self.trap = None
        DistributedNPCToonAI.delete(self)

    def getPosHpr(self):
        return (
            self.getX(),
            self.getY(),
            self.getZ(),
            self.getH(),
            self.getP(),
            self.getR()
        )

    def getBossCogId(self):
        return self.bossId

    def initializeTimers(self):
        self.waitForNextMove(1)

    def waitForNextMove(self, delayTime):
        taskName = self.uniqueName('NextMove')
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(delayTime, self.doNextMove, taskName)

    def doNextMove(self, taskName):
        self.trap = None
        self.currPos = self.getPos()
        if self.boss.traps is None:
            return

        activeTraps = self.__getActiveBossTraps()
        prestigedTraps = self.__getPrestigedBossTraps()

        # Also, only prestige the quicksand
        activeUnprestigedTraps = [trap for trap in activeTraps if trap not in prestigedTraps and trap.getTrapLevel() == 4]
        if len(activeUnprestigedTraps) == 0:
            self.doIdle()
            return

        self.isIdle = False
        trap = random.choice(activeUnprestigedTraps)
        if trap.getSuitId() is not None:
            self.doIdle()
            return
        elif trap.getDuringActivation():
            self.doIdle()
            return

        self.trap = trap
        self.d_doTravelMove()

    def __getActiveBossTraps(self):
        return self.boss.getActiveBossTraps()

    def __getPrestigedBossTraps(self):
        return self.boss.getPrestigedBossTraps()

    def d_doTravelMove(self):
        if self.boss.traps is None:
            return
        trapIndex = self.boss.traps.index(self.trap)
        x, y, z = BossCogGlobals.LawbotBossBumpyTrapsPos[trapIndex]
        toPos = Point3(x, y, z)
        self.distance = Vec3(toPos - self.currPos).length()
        time = self.getTimeToWalk()
        self.setPos(toPos)
        self.sendUpdate("doTravelMove", [str(time), x, y])
        self.waitToDoTrap(time)

    def waitToDoTrap(self, delayTime):
        taskName = self.uniqueName("TrapMove")
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(delayTime, self.d_doTrapMove, taskName)

    def d_doTrapMove(self, taskName):
        if self.boss.traps is None or self.trap is None:
            return
        trapIndex = self.boss.traps.index(self.trap)
        trapStatus = self.trap.getStatus()
        delayTime = 0
        if trapStatus == 1 and self.trap.getSuitId() is None:
            delayTime = 10
            self.trap.startPrestige()
            self.sendUpdate("doTrapMove", [trapIndex, trapStatus])
        self.waitForNextMove(delayTime)

    def doIdle(self):
        if not self.isIdle:
            self.isIdle = True
            self.d_doIdleMove()
        else:
            self.waitForNextMove(1)

    def d_sayAdvice(self):
        self.sendUpdate('sayAdvice')

    def d_doIdleMove(self):
        x, y, z, h, p, r = BossCogGlobals.LawbotBossLaurenIdlePosHpr
        toPos = Point3(x, y, z)
        self.distance = Vec3(toPos - self.currPos).length()
        time = self.getTimeToWalk()
        self.setPos(Point3(x, y, z))
        self.sendUpdate('doIdleMove', [str(time), x, y, h])
        self.waitForNextMove(time)

    def getTimeToWalk(self):
        return self.distance / self.speed

    def bossLand(self):
        self.waitForNextMove(0)


@NPCToonClassAI(npcType=NPCToonEnum.PETCLERK)
class DistributedNPCPetclerkAI(DistributedNPCToonBaseAI):

    def __init__(self, air, npcId):
        super().__init__(air, npcId)
        self.givesQuests = 0
        self.busy = 0

    def delete(self):
        taskMgr.remove(self.uniqueName('clearMovie'))
        self.ignoreAll()
        super().delete()

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.air.doId2do:
            self.notify.warning('Avatar: %s not found' % avId)
            return
        if self.isBusy():
            self.freeAvatar(avId)
            return

        av = self.air.doId2do[avId]
        self.busy = avId
        self.acceptOnce(self.air.getAvatarExitEvent(avId), self._handleUnexpectedExit, extraArgs=[avId])
        value = av.fishTank.getTotalValue()
        if value > 0:
            flag = SELL_MOVIE_START
            self.d_setMovie(avId, flag)
            taskMgr.doMethodLater(30.0, self.sendTimeoutMovie, self.uniqueName('clearMovie'))
        else:
            flag = SELL_MOVIE_NOFISH
            self.d_setMovie(avId, flag)
            self.sendClearMovie(None)
        super().avatarEnter()

    def rejectAvatar(self, avId):
        self.notify.warning('rejectAvatar: should not be called by a pet clerk!')

    def d_setMovie(self, avId, flag, extraArgs=None):
        self.sendUpdate('setMovie', [
            flag,
            self.npcId,
            avId,
            extraArgs if extraArgs else [],
            globalClockDelta.getRealNetworkTime()
        ])

    def sendTimeoutMovie(self, task):
        self.d_setMovie(self.busy, SELL_MOVIE_TIMEOUT)
        self.sendClearMovie(None)
        return Task.done

    def sendClearMovie(self, task):
        self.ignore(self.air.getAvatarExitEvent(self.busy))
        taskMgr.remove(self.uniqueName('clearMovie'))
        self.busy = 0
        self.d_setMovie(0, SELL_MOVIE_CLEAR)
        return Task.done

    def completeSale(self, sell):
        avId = self.air.getAvatarIdFromSender()
        if self.busy != avId:
            self.air.writeServerEvent('suspicious', avId, 'DistributedNPCFishermanAI.completeSale busy with %s' % self.busy)
            self.notify.warning('somebody called setMovieDone that I was not busy with! avId: %s' % avId)

        if sell:
            av = simbase.air.doId2do.get(avId)
            if av:
                trophyResult = self.air.fishManager.creditFishTank(av)
                if trophyResult:
                    movieType = SELL_MOVIE_TROPHY
                    extraArgs = [len(av.fishCollection), FishGlobals.getTotalNumFish()]
                else:
                    movieType = SELL_MOVIE_COMPLETE
                    extraArgs = []
                self.d_setMovie(avId, movieType, extraArgs)
        else:
            av = simbase.air.doId2do.get(avId)
            if av:
                self.d_setMovie(avId, SELL_MOVIE_NOFISH)
        self.sendClearMovie(None)
        return

    def _handleUnexpectedExit(self, avId):
        self.notify.warning('avatar:' + str(avId) + ' has exited unexpectedly')
        self.notify.warning('not busy with avId: %s, busy: %s ' % (avId, self.busy))
        taskMgr.remove(self.uniqueName('clearMovie'))
        self.sendClearMovie(None)


@NPCToonClassAI(npcType=NPCToonEnum.PLANT)
class DistributedNPCPlantAI(DistributedNPCToonAI):
    # don't hurt me sketched, did this to hide from game client so data miners wouldn't find it
    PHRASES = {
        0: ["Need a job? My cousin's got work as a Caesar Salad!"],
        1: ["Live or Wither, Man?"],
        2: ["Hi."],
        3: ["You have the right to romaine silent!"],
        4: ["Then, everything changed when the Brier Nation attacked."],
        5: ["Whether you're at a high point or aloe, smile!"],
        6: ["..."],
        7: ["The new 2022 Fern F-150 doesn't just raise the bar, it IS the bar."],
        8: ["Oh, SURE. I bet you just meant to GRAZE me. Buzz off."],
        9: ["I am Superfern! I fight for truth, justice and the Toontown way!"],
        10: ["Plank you very much."],
        11: ["Aloe from the other side!"],
        12: ["Git fern done!"],
        13: ["Do you know where I can find the Declaration of Indepenplants?"],
        14: ["WOAH-OH! LIVING IN A PLANTER!"],
        15: ["Happy Leaf Erikson day! Hinga Dinga Gherkin!"],
        16: ["Crikey! Have you seen those wild flytraps? Snappers they are!"],
        17: ["Do you hear drums?"],
        18: ["I'm going to be the leaf actor in an upcoming film. It's called Enter the Dragon-Lily!"],
        19: ["I dream of flying through the air, but here I am, planted in the ground."],
        20: ["Growth the raven, \"Nevermore.\""],
        21: ["The Toon approaches the plant, not knowing that such a plant is capable of a power none other possess. This plant can speak in the third person."],
        22: ["Float like a dandelion, sting like ivy."],
        23: ["I have root."],
        24: ["We don't make mistakes, just happy little acaciadents."],
        25: ["Yippie-ki-yay, pollinator."],
        26: ["I'm feeling vine. Just leaf me be."],
    }

    GENERIC_PHRASES = [
        "Leaf me alone!",
        "Long thyme no see, {toon}.",
        "After winter, trees are relieved.",
        "Speak now or forever hold your peas.",
        "I'm rooting for you!",
        "You look like you could use some encourage-mint.",
        "A penny saved is a penny ferned.",
        "I promise I won't bother you! Sprout's honor!",
        "{plant} is a real thorn in my side.",
    ]

    def __init__(self, air, npcId, questCallback=None, hq=0):
        DistributedNPCToonAI.__init__(self, air, npcId, questCallback)
        self.air = air  # type: ToontownAIRepository

    @staticmethod
    def getPlantOrder(av):
        r = random.Random(av.getDISLid())  # seed a random class with the account id.
        order = [0, 1]

        room = list(range(2, 8))  # our starting plants, hard mode lobby, 0 and 1 are excluded, 2-7
        r.shuffle(room)
        order += room

        room = list(range(8, 18))  # plants in the courtyard, 8-17
        r.shuffle(room)
        order += room

        room = list(range(18, 27))  # our final plants, Lawfice Ext
        room.remove(21)  # remove our final plant to put at the end
        r.shuffle(room)
        order += room

        order = order + [21]  # add our end plant
        return order

    def requestCheck(self, plantId):
        av = self.air.getDo(self.air.getAvatarIdFromSender())
        if not av:
            return
        order = self.getPlantOrder(av)

        if len(av.seenPlants) == 27:
            # Already has reward, just end it early
            choices = self.PHRASES.get(plantId, []) * 5
            choices = choices + self.GENERIC_PHRASES
            randomPlant = random.choice(list(TTLocalizer.PlantId2Name.values()))
            choice = random.choice(choices).replace("{toon}", av.getName()).replace("{plant}", randomPlant)
            return self.sendUpdateToAvatarId(av.doId, 'requestCheckChatResponse', [choice])

        if av.seenPlants and av.seenPlants[-1] == plantId:
            # This is the last plant they've seen, don't penalize them in case they accidentally hit it again
            return self.sendUpdateToAvatarId(av.doId, 'requestCheckResponse', [1])

        nextPlant = order[len(av.seenPlants)]

        if plantId == nextPlant:
            # This is our next plant in the list
            newPlants = av.seenPlants.copy()
            newPlants.append(plantId)
            av.b_setSeenPlants(newPlants)
            if len(av.seenPlants) == 27:
                # First plant clear
                # self.air.netMessenger.send(
                #     'clearCheck', [
                #         json.dumps({
                #             'type': 'plant',
                #             'avatarIds': [av.doId],
                #             'avatarNames': [av.getName()]
                #         })
                #     ]
                # )
                av.d_doDustCloud()
                # Add plant hat item
                if av.getHammerspace().addItem(HatItemType.Hat_Plant_Fern):
                    # If it added successfully, find our plant hat and equip it
                    av.getHammerspace().equipItem(av.getHammerspace().findItems(HatItemType.Hat_Plant_Fern)[0])
                choices = self.PHRASES.get(plantId, []) * 5
                choices = choices + self.GENERIC_PHRASES
                randomPlant = random.choice(list(TTLocalizer.PlantId2Name.values()))
                choice = random.choice(choices).replace("{toon}", av.getName()).replace("{plant}", randomPlant)
                return self.sendUpdateToAvatarId(av.doId, 'requestCheckChatResponse', [choice])
            else:
                return self.sendUpdateToAvatarId(av.doId, 'requestCheckResponse', [1])
        else:
            # They hit the wrong plant!
            av.b_setSeenPlants([])
            self.sendUpdateToAvatarId(av.doId, 'requestCheckResponse', [0])


@NPCToonClassAI(npcType=NPCToonEnum.ITEM_SELLER)
class DistributedNPCItemSellerAI(DistributedNPCToonAI, ShopManagerAI):

    def __init__(self, air, npcId, questCallback=None, hq=0):
        DistributedNPCToonAI.__init__(self, air, npcId, questCallback)

        itemsForSale = getNPCItemCatalogue(npcId)
        ShopManagerAI.__init__(self, air, itemsForSale)

    def sendPurchaseNotification(self, av: DistributedToonAI):
        pass

    def callbackAvatarCannotAfford(self, shopItem: ShopItem, av: DistributedToonAI):
        self.sendUpdateToAvatarId(av.doId, 'handleBuyResponse', [1])

    def performAdditionalPurchaseChecks(self, shopItem: ShopItem, av: DistributedToonAI) -> bool:
        return super().performAdditionalPurchaseChecks(shopItem=shopItem, av=av)

    def callbackAvatarCannotPurchase(self, shopItem: ShopItem, av: DistributedToonAI):
        self.sendUpdateToAvatarId(av.doId, 'handleBuyResponse', [3])

    def callbackPurchaseAttemptFailed(self, shopItem: ShopItem, av: DistributedToonAI):
        self.sendUpdateToAvatarId(av.doId, 'handleBuyResponse', [4])

    def callbackPurchaseSuccessful(self, shopItem: ShopItem, av: DistributedToonAI, returnValue=None):
        if returnValue is True:
            self.sendUpdateToAvatarId(av.doId, 'handleBuyResponse', [5])
        else:
            self.sendUpdateToAvatarId(av.doId, 'handleBuyResponse', [0])

    def toonInteracted(self, contextCode):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av:
            return

        # Get the pool of phrases we can say using the context code
        # Since this is given from the client, make sure its allowed
        phrasePool = TTLocalizer.NPCStoreEnterExitResponses.get(contextCode)
        if not phrasePool:
            return

        # Generate a random phrase index
        phraseIndex = random.randint(0, len(phrasePool)-1)
        self.sendUpdateToAvatarId(avId, 'handleInteraction', [contextCode, phraseIndex])


@NPCToonClassAI(npcType=NPCToonEnum.SECRETARY)
class DistributedNPCSecretaryAI(DistributedNPCToonAI):

    def __init__(self, air, npcId, questCallback = None, hq = 0):
        DistributedNPCToonAI.__init__(self, air, npcId, questCallback)

    def avatarEnter(self):
        DistributedNPCToonAI.avatarEnter(self)
        avId = self.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)
        if av:
            if self.zoneId == ToontownGlobals.LawbotLobby:  # Judy
                suits = [{'type': 'judy'}]
                av.initializeGalleryStatus(suits)


@NPCToonClassAI(npcType=NPCToonEnum.SNOWMAN)
class DistributedNPCSnowmanAI(DistributedNPCToonAI):

    def __init__(self, air, npcId, questCallback=None, hq=0):
        DistributedNPCToonAI.__init__(self, air, npcId, questCallback)
        self.scale = 1.25

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        super().announceGenerate()
        taskMgr.doMethodLater(1, self.shrinkTask, self.uniqueName('snowman-shrink'))

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        super().disable()
        taskMgr.remove(self.uniqueName('snowman-shrink'))

    def canGrow(self):
        return self.scale < 4

    def growRatio(self):
        return 1.003

    def canShrink(self):
        return self.scale > 0.95

    def shrinkRatio(self):
        return 0.998769

    def nameplateMinimum(self):
        return 3.975

    def shrinkTask(self, task):
        if self.canShrink():
            self.scale *= self.shrinkRatio()
            self.sendUpdate('snowballScale', [round(self.scale, 2)])
        return task.again

    def snowballHit(self, pieCode):
        avId = self.air.getAvatarIdFromSender()
        toon = self.air.doId2do.get(avId)
        if not toon:
            return

        if pieCode != ToontownGlobals.PieCodeToon:
            return

        if self.canGrow():
            self.scale *= self.growRatio()
            self.sendUpdate('snowballScale', [round(self.scale, 2)])
        # self.notify.info(f'LogStats SteveHitBySnowball scale {self.scale}')
        if self.scale > self.nameplateMinimum():
            # self.notify.info(f'LogStats SteveNameplateReward toonid {avId}')
            toon.addItem(NameplateItemType.Special_SnowballFight)


@NPCToonClassAI(npcType=NPCToonEnum.TAILOR)
class DistributedNPCTailorAI(DistributedNPCToonBaseAI):
    # TODO: FIX
    housingEnabled = ConfigVariableBool('want-housing', True).getValue()
    useJellybeans = ConfigVariableBool('want-tailor-jellybeans', False).getValue()

    def __init__(self, air, npcId):
        DistributedNPCToonBaseAI.__init__(self, air, npcId)
        self.timedOut = 0
        self.givesQuests = 0
        self.customerDNA = None
        self.customerId = None

    def getTailor(self):
        return 1

    def delete(self):
        taskMgr.remove(self.uniqueName('clearMovie'))
        self.ignoreAll()
        self.customerDNA = None
        self.customerId = None
        DistributedNPCToonBaseAI.delete(self)

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.air.doId2do:
            self.notify.warning('Avatar: %s not found' % avId)
            return

        # Tailors are disabled. Always free avatar.
        self.freeAvatar(avId)
        return

        if self.isBusy():
            self.freeAvatar(avId)
            return
        av = self.air.doId2do[avId]
        self.customerDNA = ToonDNA()
        self.customerDNA.makeFromNetString(av.getDNAString())
        self.customerId = avId
        av.b_setDNAString(self.customerDNA.makeNetString())
        self.acceptOnce(self.air.getAvatarExitEvent(avId), self._handleUnexpectedExit, extraArgs=[avId])

        # Checking if the avatar doesn't have enough money
        if av.getTotalMoney() < ToontownGlobals.TailorBeanCost:
            flag = PURCHASE_MOVIE_START_BROWSE_JBS
        else: # Avatar has enough money
            flag = PURCHASE_MOVIE_START

        self.sendShoppingMovie(avId, flag)
        DistributedNPCToonBaseAI.avatarEnter(self)

    def sendShoppingMovie(self, avId, flag):
        self.busy = avId
        self.sendUpdate('setMovie', [flag,
         self.npcId,
         avId,
         globalClockDelta.getRealNetworkTime()])
        taskMgr.doMethodLater(TAILOR_COUNTDOWN_TIME, self.sendTimeoutMovie, self.uniqueName('clearMovie'))

    def rejectAvatar(self, avId):
        self.notify.warning('rejectAvatar: should not be called by a Tailor!')

    def sendTimeoutMovie(self, task):
        toon = self.air.doId2do.get(self.customerId)
        if toon is not None and self.customerDNA:
            toon.b_setDNAString(self.customerDNA.makeNetString())
        self.timedOut = 1
        self.sendUpdate('setMovie', [PURCHASE_MOVIE_TIMEOUT,
         self.npcId,
         self.busy,
         globalClockDelta.getRealNetworkTime()])
        self.sendClearMovie(None)
        return Task.done

    def sendClearMovie(self, task):
        self.ignore(self.air.getAvatarExitEvent(self.busy))
        self.customerDNA = None
        self.customerId = None
        self.busy = 0
        self.timedOut = 0
        self.sendUpdate('setMovie', [PURCHASE_MOVIE_CLEAR,
         self.npcId,
         0,
         globalClockDelta.getRealNetworkTime()])
        self.sendUpdate('setCustomerDNA', [0, ''])
        return Task.done

    def completePurchase(self, avId):
        av = self.air.doId2do[avId]
        self.busy = avId
        self.sendUpdate('setMovie', [PURCHASE_MOVIE_COMPLETE,
         self.npcId,
         avId,
         globalClockDelta.getRealNetworkTime()])
        self.sendClearMovie(None)

    def setDNA(self, blob, finished, which):
        avId = self.air.getAvatarIdFromSender()
        if avId != self.customerId:
            if self.customerId:
                self.air.writeServerEvent('suspicious', avId, 'DistributedNPCTailorAI.setDNA customer is %s' % self.customerId)
                self.notify.warning('customerId: %s, but got setDNA for: %s' % (self.customerId, avId))
            return

        testDNA = ToonDNA()
        if not testDNA.isValidNetString(blob):
            self.air.writeServerEvent('suspicious', avId, 'DistributedNPCTailorAI.setDNA: invalid dna: %s' % blob)
            return

        if avId in self.air.doId2do:
            av = self.air.doId2do.get(avId)
            if finished == 2 and which > 0:
                if av.getTotalMoney() >= ToontownGlobals.TailorBeanCost:
                    av.takeMoney(ToontownGlobals.TailorBeanCost)
                    av.b_setDNAString(blob)
                    if which & ClosetGlobals.SHIRT:
                        if av.addToClothesTopsList(self.customerDNA.topTex, self.customerDNA.topTexColor, self.customerDNA.sleeveTex, self.customerDNA.sleeveTexColor) == 1:
                            av.b_setClothesTopsList(av.getClothesTopsList())
                        else:
                            self.notify.warning('NPCTailor: setDNA() - unable to save old tops - we exceeded the tops list length')
                    if which & ClosetGlobals.SHORTS:
                        if av.addToClothesBottomsList(self.customerDNA.botTex, self.customerDNA.botTexColor) == 1:
                            av.b_setClothesBottomsList(av.getClothesBottomsList())
                        else:
                            self.notify.warning('NPCTailor: setDNA() - unable to save old bottoms - we exceeded the bottoms list length')
                    av.b_setDNAString(blob)
                    self.air.writeServerEvent('boughtTailorClothes', avId, '%s|%s|%s' % (self.doId, which, self.customerDNA.asTuple()))
                else:
                    self.notify.warning('Avatar no longer has enough money to purchase clothes')
            elif finished == 1:
                # Purchase cancelled - make sure DNA gets reset, but don't
                # burn the clothing ticket
                if self.customerDNA:
                    av.b_setDNAString(self.customerDNA.makeNetString())
            else:
                # Warning - we are trusting the client to set their DNA here
                # This is a big security hole. Either the client should just send
                # indexes into the clothing choices or the tailor should verify
                # av.b_setDNAString(blob)
                # Don't set the avatars DNA.  Instead, send a message back to the
                # all the clients in this zone telling them them the dna of the localToon
                # so they can set it themselves.
                self.sendUpdate('setCustomerDNA', [avId, blob])
        else:
            self.notify.warning('no av for avId: %d' % avId)
        if self.timedOut == 1 or finished == 0:
            return
        if self.busy == avId:
            taskMgr.remove(self.uniqueName('clearMovie'))
            self.completePurchase(avId)
        elif self.busy:
            self.air.writeServerEvent('suspicious', avId, 'DistributedNPCTailorAI.setDNA busy with %s' % self.busy)
            self.notify.warning('setDNA from unknown avId: %s busy: %s' % (avId, self.busy))

    def _handleUnexpectedExit(self, avId):
        self.notify.warning('avatar:' + str(avId) + ' has exited unexpectedly')
        if self.customerId == avId:
            toon = self.air.doId2do.get(avId)
            if toon is None:
                toon = DistributedToonAI(self.air)
                toon.doId = avId
            if self.customerDNA:
                toon.b_setDNAString(self.customerDNA.makeNetString())
                db = DatabaseObject(self.air, avId)
                db.storeObject(toon, ['setDNAString'])
        else:
            self.notify.warning('invalid customer avId: %s, customerId: %s ' % (avId, self.customerId))
        if self.busy == avId:
            self.sendClearMovie(None)
        else:
            self.notify.warning('not busy with avId: %s, busy: %s ' % (avId, self.busy))


@NPCToonClassAI(npcType=NPCToonEnum.TUTORIAL)
class DistributedNPCLowdenAI(DistributedNPCToonAI):
    def __init__(self, air, npcId):
        self.air = air
        super().__init__(air, npcId)

        self.npcId = npcId
        self.cogMerits = [0, 0, 0, 0, 0]
        self.clubIds = []

    def delete(self):
        self.notify.debug("delete")

        if self.inventory:
            self.inventory.unload()
            self.inventory = None

        if self.experience:
            self.experience = None

        self.ignoreAll()

        if __dev__:
            del self._sentExitServerEvent
            GarbageReport.checkForGarbageLeaks()

        self.ignoreAll()
        super().delete()

    def announceGenerate(self):
        super().announceGenerate()
        self.setMaxCarry(110)
        gagTracks = [1] * BattleGlobals.NUM_GAG_TRACKS
        self.b_setTrackAccess(gagTracks)

        self.b_setMaxHp(163)
        self.b_setHp(163)

        self.b_setExperience([BattleGlobals.MaxSkill] * BattleGlobals.NUM_GAG_TRACKS)

        inventory = GagInventoryBase(self)
        self.b_setInventory(inventory.makeNetString())

    def giveNewObjective(self):
        pass

    def d_sendToonTip(self, tipId):
        pass

    def stopToonUp(self):
        taskMgr.remove(self.uniqueName('safeZoneToonUp'))
        self.ignore(self.air.getAvatarExitEvent(self.getDoId()))
        self.ignore(self.air.getAvatarExitEvent(self.getDoId()))

    def b_setMaxHp(self, maxHp: int):
        '''lowden is cool dont check his health'''
        self.d_setMaxHp(maxHp)
        self.setMaxHp(maxHp)

    def d_setMaxHp(self, maxHp):
        '''lowden is cool dont check his health'''
        self.sendUpdate('setMaxHp', [maxHp])
