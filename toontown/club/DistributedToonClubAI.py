from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from direct.directnotify.DirectNotifyGlobal import directNotify


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
        print '[Clubs] Club AI proxy loaded.'

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

