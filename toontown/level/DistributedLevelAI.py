"""DistributedLevelAI.py: contains the DistributedLevelAI class"""
from typing import Optional

from toontown.ai.AIBaseGlobal import *
from direct.distributed.ClockDelta import *
from direct.distributed import DistributedObjectAI
from toontown.battle import BattleGlobals
from toontown.level import Level
from toontown.level import EntityCreatorAI
from toontown.level.editor import EditorGlobals
from direct.showbase.PythonUtil import Functor, weightedChoice
from toontown.modifiers.contentsync.ContentSyncApplierAI import ContentSyncApplierAI


@DirectNotifyCategory()
class DistributedLevelAI(DistributedObjectAI.DistributedObjectAI, Level.Level, ContentSyncApplierAI):

    def __init__(self, air, zoneId, entranceId, avIds):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        Level.Level.__init__(self)
        # these are required fields
        self.zoneId = zoneId
        self.entranceId = entranceId

        if len(avIds) <= 0 or len(avIds) > 4:
            self.notify.warning('How do we have this many avIds? avIds: %s' % avIds)
        self.avIdList = avIds
        self.numPlayers = len(self.avIdList)
        # this is the list of avatars that are actually present
        self.presentAvIds = list(self.avIdList)
        self.notify.debug('expecting avatars: %s' % str(self.avIdList))
        self.maxMerits = 0
        self.merits = 0
        if EditorGlobals.wantLevelEditor():
            self.modified = 0

    def setLevelSpec(self, levelSpec):
        self.levelSpec = levelSpec

    def generate(self, levelSpec = None):
        self.notify.debug('generate')
        DistributedObjectAI.DistributedObjectAI.generate(self)
        if levelSpec is None:
            levelSpec = self.levelSpec

        self.initializeLevel(levelSpec)

        # self.zoneIds comes from LevelMgrAI
        self.sendUpdate('setZoneIds', [self.zoneIds])
        self.sendUpdate('setStartTimestamp', [self.startTimestamp])
            
    def getBattleCreditMultiplier(self):
        return 1

    def getMeritCreditMultiplier(self):
        return self.getBattleCreditMultiplier() * BattleGlobals.getInvasionMultiplier()

    def getLevelZoneId(self):
        """no entities should be generated in the level's zone; it causes
        nasty race conditions on the client if there are entities in the
        same zone with the level"""
        return self.zoneId

    def getPlayerIds(self):
        return self.avIdList

    def getEntranceId(self):
        return self.entranceId

    def delete(self, deAllocZone=True):
        self.notify.debug('delete')
        if EditorGlobals.wantLevelEditor():
            self.removeAutosaveTask()
        self.destroyLevel()
        self.ignoreAll()
        if deAllocZone:
            self.air.deallocateZone(self.zoneId)
        DistributedObjectAI.DistributedObjectAI.delete(self)

    def initializeLevel(self, levelSpec):
        # record the level's start time so that we can sync the clients
        self.startTime = globalClock.getRealTime()
        self.startTimestamp = globalClockDelta.localToNetworkTime(self.startTime, bits=32)

        # choose a scenario
        # make list of lists: [(weight, scenarioIndex), ...]
        lol = list(zip([1] * levelSpec.getNumScenarios(), list(range(levelSpec.getNumScenarios()))))
        scenarioIndex = weightedChoice(lol)

        Level.Level.initializeLevel(self, self.doId, levelSpec, scenarioIndex)

        if EditorGlobals.wantLevelEditor():
            self.accept(self.editMgrEntity.getSpecSaveEvent(), self.saveSpec)

    # Listen for avatar disconnects and the like
    def initializeLevelToonHooks(self):
        for avId in self.avIdList:
            av = self.air.doId2do.get(avId)
            if av:
                self.acceptOnce(self.air.getAvatarExitEvent(avId), Functor(self.handleAvatarDisconnect, avId))
                self.accept(av.getLeftZoneEvent(), self.handleAvatarLeft)

        self.applyContentSync(*self.avIdsToAvs(self.avIdList))
        # set up a barrier that will clear when all avs have left or
        # disconnected
        self.allToonsGoneBarrier = self.beginBarrier('allToonsGone', self.avIdList, 3 * 24 * 60 * 60, self.allToonsGone)

    def handleAvatarDisconnect(self, avId):
        try:
            self.presentAvIds.remove(avId)
            DistributedLevelAI.notify.warning('av %s has disconnected' % avId)
        except Exception:
            DistributedLevelAI.notify.warning('got disconnect for av %s, not in list' % avId)

        if not self.presentAvIds:
            self.allToonsGone([])

    def handleAvatarLeft(self, avId, oldZoneId):
        if oldZoneId == self.zoneId:
            if avId in self.presentAvIds:
                self.presentAvIds.remove(avId)
        if not self.presentAvIds:
            self.allToonsGone([])

    def allToonsGone(self, toonsThatCleared):
        DistributedLevelAI.notify.debug('allToonsGone')
        if hasattr(self, 'allToonsGoneBarrier'):
            self.ignoreBarrier(self.allToonsGoneBarrier)
            del self.allToonsGoneBarrier
        for avId in self.avIdList:
            self.ignore(self.air.getAvatarExitEvent(avId))
            av = self.air.doId2do.get(avId)
            if av:
                self.ignore(av.getLeftZoneEvent())

        self.requestDelete()

    def contentSync_getForceOldZone(self) -> Optional[int]:
        return self.zoneId

    def createEntityCreator(self):
        """Create the object that will be used to create Entities.
        Inheritors, override if desired."""
        return EntityCreatorAI.EntityCreatorAI(level=self)

    def setOuch(self, penalty):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        self.notify.debug('setOuch %s' % penalty)
        # make sure penalty is > 0
        if av and penalty > 0:
            av.takeDamage(penalty)
            # this should be done in DistributedToonAI; do we ever go sad
            # without losing our gags?

    def requestCurrentLevelSpec(self, specHash, entTypeRegHash):
        self.senderId = self.air.getAvatarIdFromSender()
        self.notify.info('av %s: specHash %s, entTypeRegHash %s' % (self.senderId, specHash, entTypeRegHash))
        # client is running in dev mode and we're not; that won't fly
        if not EditorGlobals.wantLevelEditor():
            self.notify.info('client is in dev mode and we are not')
            self.sendUpdateToAvatarId(self.senderId, 'setSpecDeny', ['AI server is not running in dev mode. Set want-dev to false on your client or true on the AI.'])
            return

        # first check the typeReg hash -- if it doesn't match, the
        # client should not be connecting. Their entityTypeRegistry
        # is different from ours.
        srvHash = self.levelSpec.entTypeReg.getHashStr()
        self.notify.info('srv entTypeRegHash %s' % srvHash)
        if srvHash != entTypeRegHash:
            self.sendUpdateToAvatarId(self.senderId, 'setSpecDeny', ['EntityTypeRegistry hashes do not match! (server:%s, client:%s' % (srvHash, entTypeRegHash)])
            return

        # now compare the hashes of the client and server specs
        if hash(self.levelSpec) != specHash:
            self.notify.info('spec hashes do not match, sending our spec')
            spec = self.levelSpec
            useDisk = ConfigVariableBool('spec-by-disk', True).getValue()
        else:
            self.notify.info('spec hashes match, sending null spec')
            spec = None
            # don't need to hit disk if we're just sending 'None' over the wire
            useDisk = 0
        specStr = repr(spec)
        from toontown.utils.largeblob import DistributedLargeBlobSenderAI
        largeBlob = DistributedLargeBlobSenderAI.DistributedLargeBlobSenderAI(self.air, self.zoneId, self.senderId, specStr, useDisk=useDisk)
        largeBlob.generateWithRequired(self.zoneId)
        self.sendUpdateToAvatarId(self.senderId, 'setSpecSenderDoId', [largeBlob.doId])
        
    def calculateMeritsFromSuits(self, suits):
        '''
        Returns the merits obtained from the given suit handles.
        '''
        totalMerits = 0
        mult = self.getMeritCreditMultiplier()
        for suitHandle in suits:
            if isinstance(suitHandle, dict):
                if suitHandle['isVirtual']:
                    merits = 0
                else:
                    merits = suitHandle['level']
                    merits = int(round(merits))
                    if suitHandle['hasRevives']:
                        merits *= 2
                    if suitHandle['isElite']:
                        merits *= 1.5
                    merits *= mult
                    merits = int(round(merits))
                    totalMerits += merits
            else:
                if suitHandle.getVirtual():
                    merits = 0
                else:
                    merits = suitHandle.getActualLevel()
                    merits = int(round(merits))
                    if suitHandle.getSkeleRevives():
                        merits *= 2
                    if suitHandle.getElite():
                        merits *= 1.5
                    merits *= mult
                    merits = int(round(merits))
                    totalMerits += merits
        return totalMerits
        
    def calculateMeritBonuses(self, merits):
        '''
        Factors in global merit bonuses into the given merit total
        '''
        return merits
        
    def setMaxMerits(self, maxMerits):
        self.maxMerits = maxMerits
        
    def d_setMaxMerits(self, maxMerits):
        self.sendUpdate('setMaxMerits', [maxMerits])
        
    def b_setMaxMerits(self, maxMerits):
        self.setMaxMerits(maxMerits)
        self.d_setMaxMerits(maxMerits)
        
    def getMaxMerits(self):
        return self.maxMerits
        
    def retrieveMerits(self, merits):
        self.merits += merits
        self.b_setMerits(self.merits)
        
    def setMerits(self, merits):
        self.merits = merits
        
    def d_setMerits(self, merits):
        self.sendUpdate('setMerits', [merits])
        
    def b_setMerits(self, merits):
        self.setMerits(merits)
        self.d_setMerits(merits)
        
    def getMerits(self):
        return self.merits

    if EditorGlobals.wantLevelEditor():
        def setAttribChange(self, entId, attribName, value, username = 'SYSTEM'):
            DistributedLevelAI.notify.info('setAttribChange(%s): %s, %s = %s' % (username,
             entId,
             attribName,
             repr(value)))
            self.sendUpdate('setAttribChange', [entId,
             attribName,
             repr(value),
             username])
            self.levelSpec.setAttribChange(entId, attribName, value, username)
            self.modified = 1
            self.scheduleAutosave()

        AutosavePeriod = simbase.config.GetFloat('level-autosave-period-minutes', 5)

        def scheduleAutosave(self):
            if hasattr(self, 'autosaveTask'):
                return
            self.autosaveTaskName = self.uniqueName('autosaveSpec')
            self.autosaveTask = taskMgr.doMethodLater(DistributedLevelAI.AutosavePeriod * 60, self.autosaveSpec, self.autosaveTaskName)

        def removeAutosaveTask(self):
            if hasattr(self, 'autosaveTask'):
                taskMgr.remove(self.autosaveTaskName)
                del self.autosaveTask

        def autosaveSpec(self, task = None):
            self.removeAutosaveTask()
            if self.modified:
                DistributedLevelAI.notify.info('autosaving spec')
                filename = self.levelSpec.getFilename()
                filename = '%s.autosave' % filename
                self.levelSpec.saveToDisk(filename, makeBackup=0)

        def saveSpec(self, task = None):
            DistributedLevelAI.notify.info('saving spec')
            self.removeAutosaveTask()
            if not self.modified:
                DistributedLevelAI.notify.info('no changes to save')
                return
            self.levelSpec.saveToDisk()
            self.modified = 0
