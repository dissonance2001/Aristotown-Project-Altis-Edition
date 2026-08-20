import random
import time

from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.task.TaskManagerGlobal import taskMgr

from toontown.events.winter.DistributedWinterMinigameSuitAI import DistributedWinterMinigameSuitAI
from toontown.suit import SuitDNA
from toontown.toonbase import TTLocalizer, ToontownGlobals

MIN_PRESENT_ID = 100
MAX_PRESENT_ID = 999
MAX_PRESENTS = 40
MAX_COGS = 15
STANDARD_COGS = (
    'f', 'p', 'ym', 'mm', 'ds', 'hh', 'cr', 'tbc',
    'bf', 'b', 'dt', 'ac', 'bs', 'sd', 'le', 'bw',
    'sc', 'pp', 'tw', 'bc', 'nc', 'mb', 'ls', 'rb',
    'cc', 'tm', 'nd', 'gh', 'ms', 'tf', 'm', 'mh'
)


class DistributedToonseltownMinigameAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedToonseltownMinigameAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.air = air
        self.presentsPerToon = 3
        self.gameTime = 180
        self.rewardMinimum = 8
        self.teamRewardMinimum = 150
        self.presentSpawnQueue = list(ToontownGlobals.TsMinigamePresentSpawns)
        self.treePresentSpawns = list(ToontownGlobals.TsMinigameTreePresentLocations)
        self.freeSuitLocations = list(ToontownGlobals.TsMinigameSuitLocations)
        self.nextPresentId = MIN_PRESENT_ID
        self.spawnedPresentLocations = {}
        self.activeSuits = {}
        self.activeSuitLocations = {}
        self.players = {}
        self.totalScore = 0
        self.running = False
        self.rateLimiters = {}
        self.spawnTaskNames = []
        self.suitSpawnSerial = 0
        random.shuffle(self.presentSpawnQueue)

    def delete(self):
        self._removeTasks()
        DistributedObjectAI.delete(self)

    def startGameWarnings(self):
        self.sendTsMessage(TTLocalizer.TsMinigameStartingSoon)
        taskMgr.doMethodLater(10, self.startGame, self.uniqueName('startGame'))

    def startGame(self, task=None):
        if self.running:
            return
        self.running = True
        for playerId in self.getPlayersInTs():
            self.registerPlayer(playerId)
        self.sendUpdate('setupTree', [])
        self.sendUpdate('setupGUI', [])
        self.spawnStarterPresents()
        self.sendUpdate('handleEventStart', [self.gameTime])
        self.generateSuits()

    def spawnStarterPresents(self):
        playerCount = len(self.getPlayersInTs())
        count = min(MAX_PRESENTS, max(9, playerCount * self.presentsPerToon))
        for i in xrange(count):
            self.spawnFieldPresent()

    def spawnFieldPresent(self):
        if not self.presentSpawnQueue:
            self.presentSpawnQueue = list(ToontownGlobals.TsMinigamePresentSpawns)
            random.shuffle(self.presentSpawnQueue)
        if not self.presentSpawnQueue:
            return
        presentId = self.getNextPresentId()
        if presentId is None:
            return
        presentPos = self.presentSpawnQueue.pop(0)
        x, y, z = presentPos
        self.spawnedPresentLocations[presentId] = presentPos
        self.sendUpdate('generateFieldPresent', [presentId, x, y, z])

    def getNextPresentId(self):
        if self.nextPresentId > MAX_PRESENT_ID:
            return None
        presentId = self.nextPresentId
        self.nextPresentId += 1
        return presentId

    def removeFieldPresent(self, presentId):
        if presentId not in self.spawnedPresentLocations:
            return False
        self.presentSpawnQueue.append(self.spawnedPresentLocations[presentId])
        del self.spawnedPresentLocations[presentId]
        self.sendUpdate('destroyPresent', [presentId])
        return True

    def spawnTreePresent(self):
        if not self.treePresentSpawns:
            return
        presentPos = random.choice(self.treePresentSpawns)
        self.treePresentSpawns.remove(presentPos)
        x, y, z = presentPos
        self.sendUpdate('generateTreePresent', [x, y, z])

    def registerPlayer(self, toonId):
        if toonId not in self.players:
            self.players[toonId] = {'score': 0, 'holding-present': False}

    def isHoldingPresent(self, toonId):
        return self.players.get(toonId, {}).get('holding-present', False)

    def setPlayerIsHoldingPresent(self, toonId, status):
        if toonId in self.players:
            self.players[toonId]['holding-present'] = status

    def isRateLimited(self, avId):
        now = time.time()
        recent = [stamp for stamp in self.rateLimiters.get(avId, []) if now - stamp < 1.0]
        if len(recent) >= 3:
            self.rateLimiters[avId] = recent
            return True
        recent.append(now)
        self.rateLimiters[avId] = recent
        return False

    def playerTouchedFieldPresent(self, presentId):
        if not self.running:
            return
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.players or self.isRateLimited(avId) or self.isHoldingPresent(avId):
            return
        if not self.removeFieldPresent(presentId):
            return
        self.setPlayerIsHoldingPresent(avId, True)
        self.sendUpdateToAvatarId(avId, 'showHoldingPresent', [])
        self.spawnFieldPresent()

    def playerTouchedTree(self):
        if not self.running:
            return
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.players or self.isRateLimited(avId) or not self.isHoldingPresent(avId):
            return
        self.setPlayerIsHoldingPresent(avId, False)
        self.sendUpdateToAvatarId(avId, 'hideHoldingPresent', [])
        self.spawnTreePresent()
        self.increasePlayerScore(avId, ToontownGlobals.TsMinigamePresentPoints)

    def playerHitCogWithSnowball(self, cogId):
        if not self.running:
            return
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.players:
            return
        self.suitHitBySnowball(cogId, avId)

    def getTotalScore(self):
        return self.totalScore

    def increaseTotalScore(self, amount):
        self.totalScore += amount
        self.updateTotalScore()

    def deductTotalScore(self, amount):
        self.totalScore = max(0, self.totalScore - amount)
        self.updateTotalScore()

    def getPlayersScore(self, toonId):
        return self.players.get(toonId, {}).get('score', 0)

    def increasePlayerScore(self, toonId, amount):
        if toonId not in self.players:
            return
        self.players[toonId]['score'] += amount
        self.increaseTotalScore(amount)

    def updateTotalScore(self):
        self.sendUpdate('updateTotalScore', [self.totalScore])

    def generateSuits(self, task=None):
        if not self.running:
            return
        currentPlayers = self.getPlayersInTs()
        for playerId in currentPlayers:
            self.registerPlayer(playerId)
        if self.totalScore > 0:
            activeCogsNum = len(self.activeSuitLocations)
            totalToons = len(currentPlayers)
            totalToSpawn = min(MAX_COGS - activeCogsNum, totalToons - activeCogsNum)
            if totalToSpawn > 0:
                random.shuffle(self.freeSuitLocations)
                for i in xrange(totalToSpawn):
                    self.suitSpawnSerial += 1
                    taskName = self.uniqueName('cogSpawn-%s' % self.suitSpawnSerial)
                    self.spawnTaskNames.append(taskName)
                    taskMgr.doMethodLater(random.randint(1, 6), self.generateSuit, taskName)
                self.sendUpdate('showWarningText', [])
        taskMgr.doMethodLater(30, self.generateSuits, self.uniqueName('cogGenerator'))

    def suitHitBySnowball(self, suitId, toonId):
        suit = self.activeSuits.get(suitId)
        if suit and not suit.hit:
            self.destroySuit(suitId)
            self.increasePlayerScore(toonId, ToontownGlobals.TsMinigameCogPoints)

    def destroySuit(self, suitId=None):
        if not suitId:
            return
        suit = self.activeSuits.get(suitId)
        if not suit:
            return
        suit.hitByToon()
        taskMgr.remove('ts-stealing-present-loop-%d' % suitId)
        if suitId in self.activeSuitLocations:
            self.freeSuitLocations.append(self.activeSuitLocations[suitId])
            del self.activeSuitLocations[suitId]
        if suitId in self.activeSuits:
            del self.activeSuits[suitId]

    def destroyAllSuits(self):
        for suitId in list(self.activeSuits.keys()):
            self.destroySuit(suitId)

    def removeAllSuits(self):
        for suitId, suit in list(self.activeSuits.items()):
            taskMgr.remove('ts-stealing-present-loop-%d' % suitId)
            taskMgr.remove('ts-stop-flyin-cog-%s' % suitId)
            suit.canGrab = False
            suit.requestDelete()
        self.activeSuits.clear()
        self.activeSuitLocations.clear()

    def stealPresent(self, suitId):
        if not self.running:
            return
        suit = self.air.doId2do.get(suitId)
        if suit:
            if suit.canGrab and self.getTotalScore() > 0:
                self.deductTotalScore(ToontownGlobals.TsMinigameDeductCogPoints)
            taskMgr.doMethodLater(4, self.stealPresent, 'ts-stealing-present-loop-%d' % suitId, extraArgs=[suitId])

    def getRandomSuitLocation(self):
        if not self.freeSuitLocations:
            return None
        return self.freeSuitLocations.pop()

    def generateSuit(self, task=None):
        if not self.running:
            return
        pos = self.getRandomSuitLocation()
        if not pos:
            return
        head = random.choice(STANDARD_COGS)
        if head == 'mm':
            head = 'ds'
        suit = DistributedWinterMinigameSuitAI(self.air, None)
        suit.dna = SuitDNA.SuitDNA()
        suit.dna.newSuit(head)
        suit.setPosHpr(*pos)
        suit.generateWithRequired(ToontownGlobals.Toonseltown)
        self.activeSuitLocations[suit.doId] = pos
        self.activeSuits[suit.doId] = suit
        self.sendUpdate('activateSuit', [suit.doId])
        suit.flyIn(pos[0], pos[1], pos[2])
        taskMgr.doMethodLater(4, self.stealPresent, 'ts-stealing-present-loop-%d' % suit.doId, extraArgs=[suit.doId])

    def endGame(self, task=None):
        if not self.running and not self.players:
            self.requestDelete()
            return
        self.running = False
        self.sendTsMessage(TTLocalizer.TsMinigameEnd)
        self.rewardPrizes(list(self.players.keys()))
        self._removeTasks()
        self.sendUpdate('startCleanup', [])
        self.removeAllSuits()
        self.requestDelete()

    def rewardPrizes(self, players):
        for avId in players:
            score = self.getPlayersScore(avId)
            if score < self.rewardMinimum:
                continue
            extraRewards = max(0, (score - self.rewardMinimum) // 10)
            if self.getTotalScore() >= self.teamRewardMinimum:
                extraRewards += self.getTotalScore() // self.teamRewardMinimum
            beans = 1500 + int(extraRewards) * 500
            av = self.air.doId2do.get(avId)
            if av:
                try:
                    av.addMoney(beans)
                    self._sendMessageToAvatar(av, 'Congratulations on scoring %s points. You have won %s jellybeans!' % (score, beans))
                except:
                    self.notify.warning('Could not reward Toon %s for Present Thief.' % avId)

    def getPlayersInTs(self):
        players = set()
        for obj in self.air.doId2do.values():
            if obj.__class__.__name__ != 'DistributedToonAI':
                continue
            try:
                zoneId = obj.getLocation()[1]
            except:
                continue
            if zoneId == ToontownGlobals.Toonseltown:
                players.add(obj.doId)
        return players

    def _sendMessageToAvatar(self, av, message):
        try:
            self.air.newsManager.sendSystemMessageToAvatar(av, message, 0)
        except:
            try:
                av.sendUpdate('setSystemMessage', [0, message])
            except:
                pass

    def sendTsMessage(self, message):
        for avId in self.getPlayersInTs():
            av = self.air.doId2do.get(avId)
            if av:
                self._sendMessageToAvatar(av, message)

    def _removeTasks(self):
        taskMgr.remove(self.uniqueName('startGame'))
        taskMgr.remove(self.uniqueName('cogGenerator'))
        for taskName in self.spawnTaskNames:
            taskMgr.remove(taskName)
        self.spawnTaskNames = []
        for suitId in list(self.activeSuits.keys()):
            taskMgr.remove('ts-stealing-present-loop-%d' % suitId)
