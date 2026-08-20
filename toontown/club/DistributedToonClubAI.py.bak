import time
from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.toonbase import ToontownGlobals


class DistributedToonClubAI(DistributedObjectGlobalAI):
    """AI-side proxy for the UD-owned Club manager."""

    notify = directNotify.newCategory('DistributedToonClubAI')

    VALID_PROGRESS_TYPES = frozenset((
        'cogs',
        'buildings',
        'trolley',
        'fish',
        'bosses',
    ))

    def announceGenerate(self):
        DistributedObjectGlobalAI.announceGenerate(self)
        self._groupSuitTeleports = {}
        self.accept('GroupTrackerLogicalChangeZone-all', self._groupAvatarChangedZone)
        print '[Clubs] Club AI proxy loaded.'

    def groupPrepareSuitTeleport(self, targetZone, deptIndex):
        try:
            avId = int(self.air.getAvatarIdFromSender())
            targetZone = int(targetZone)
            deptIndex = int(deptIndex)
        except:
            return
        allowed = {
            ToontownGlobals.BossbotLobby: 0,
            ToontownGlobals.SellbotLobby: 3,
            ToontownGlobals.CashbotLobby: 2,
            ToontownGlobals.LawbotLobby: 1,
        }
        if allowed.get(targetZone) != deptIndex:
            return
        avatar = self.air.doId2do.get(avId)
        if avatar and int(getattr(avatar, 'zoneId', 0) or 0) == targetZone:
            try:
                if int(getattr(avatar, 'cogIndex', -1)) != deptIndex:
                    avatar.b_setCogIndex(deptIndex)
                return
            except:
                pass
        self._groupSuitTeleports[avId] = (targetZone, deptIndex, time.time() + 20.0)

    def _groupAvatarChangedZone(self, newZone, oldZone, avatar):
        avId = int(getattr(avatar, 'doId', 0))
        lobbyDepts = {
            ToontownGlobals.BossbotLobby: 0,
            ToontownGlobals.LawbotLobby: 1,
            ToontownGlobals.CashbotLobby: 2,
            ToontownGlobals.SellbotLobby: 3,
        }
        deptIndex = lobbyDepts.get(int(newZone))
        request = self._groupSuitTeleports.get(avId)
        if request:
            if time.time() > request[2]:
                self._groupSuitTeleports.pop(avId, None)
                request = None
            elif int(newZone) == int(request[0]):
                deptIndex = int(request[1])
                self._groupSuitTeleports.pop(avId, None)
        if deptIndex is None:
            return
        try:
            if int(getattr(avatar, 'cogIndex', -1)) != deptIndex:
                avatar.b_setCogIndex(deptIndex)
        except:
            pass

    def reportProgress(self, avId, progressType, amount=1):
        try:
            avId = int(avId)
            progressType = str(progressType)
            amount = int(amount)
        except:
            return

        if avId <= 0 or amount <= 0:
            return
        if progressType not in self.VALID_PROGRESS_TYPES:
            self.notify.warning(
                'Ignored invalid Club Task progress type: %s' % progressType)
            return

        self.sendUpdate(
            'reportProgressAI', [avId, progressType, amount])

    def reportClubCoins(self, avId, amount):
        try:
            avId = int(avId)
            amount = int(amount)
        except:
            return

        if avId <= 0 or amount <= 0:
            return
        self.sendUpdate('reportClubCoinsAI', [avId, amount])

    def magicWordAddClubCoins(self, avId, amount):
        try:
            avId = int(avId)
            amount = int(amount)
        except:
            return False
        if avId <= 0 or amount <= 0 or amount > 0xFFFFFFFF:
            return False

        # Reuse the existing AI-to-UD progress field so no new DC method is
        # required. The UD intercepts this internal type before task handling.
        self.sendUpdate(
            'reportProgressAI', [avId, '__magic_coin__', amount])
        return True

    def magicWordSetClubLevel(self, avId, level):
        try:
            avId = int(avId)
            level = int(level)
        except:
            return False
        if avId <= 0 or level < 1:
            return False
        level = min(level, 10000)

        # Reuse the existing AI-to-UD progress field so no new DC method is
        # required. The UD intercepts this internal type before task handling.
        self.sendUpdate(
            'reportProgressAI', [avId, '__magic_level__', level])
        return True

